from aiogram import types
from db import get_conn
import config

async def handle_balance(msg: types.Message, bot):
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE tg_id=?", (tg_id,))
    row = cursor.fetchone()
    if row:
        await msg.reply(f"您的余额为：{row[0]:.2f} 元")
    else:
        await msg.reply("请先 /start 注册。")
    conn.close()

async def handle_wallet_log(msg: types.Message, bot):
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE tg_id=?", (tg_id,))
    u = cursor.fetchone()
    if not u:
        await msg.reply("请先 /start 注册。")
        conn.close()
        return
    user_id = u[0]
    cursor.execute("SELECT change, type, reason, status, create_time FROM wallet_logs WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    rows = cursor.fetchall()
    if not rows:
        await msg.reply("暂无账单记录。")
    else:
        text = "最近10条钱包流水：\n"
        for r in rows:
            text += f"{r[4][:16]} | {r[1]:<8} | {r[0]:>7}元 | {r[2][:8]} | {r[3]}\n"
        await msg.reply(text)
    conn.close()

async def handle_recharge(msg: types.Message, bot):
    args = msg.text.split()
    if len(args) < 4:
        await msg.reply("用法：/recharge 金额 支付方式(USDT/支付宝/微信/银行卡) 账号/地址 [凭证图片url]")
        return
    amount, method, account = float(args[1]), args[2], args[3]
    proof = args[4] if len(args) > 4 else ""
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE tg_id=?", (tg_id,))
    u = cursor.fetchone()
    if not u:
        await msg.reply("请先 /start 注册。")
        conn.close()
        return
    user_id = u[0]
    cursor.execute("""INSERT INTO transfer_requests (user_id, type, amount, method, status, account, proof)
                      VALUES (?, 'recharge', ?, ?, '待审核', ?, ?)""",
                   (user_id, amount, method, account, proof))
    conn.commit()
    await msg.reply(f"充值申请已提交，金额：{amount}，方式：{method}，请等待人工审核。")
    for admin_id in config.ADMINS:
        await bot.send_message(admin_id, f"新充值申请：用户{tg_id}，金额{amount}，方式{method}，账号/地址：{account}，凭证：{proof}")
    conn.close()

async def handle_withdraw(msg: types.Message, bot):
    args = msg.text.split()
    if len(args) < 4:
        await msg.reply("用法：/withdraw 金额 提现方式(USDT/支付宝/微信/银行卡) 账号/地址")
        return
    amount, method, account = float(args[1]), args[2], args[3]
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, balance FROM users WHERE tg_id=?", (tg_id,))
    u = cursor.fetchone()
    if not u:
        await msg.reply("请先 /start 注册。")
        conn.close()
        return
    user_id, balance = u
    if balance < amount:
        await msg.reply("余额不足。")
        conn.close()
        return
    cursor.execute("UPDATE users SET balance=balance-? WHERE id=?", (amount, user_id))
    cursor.execute("""INSERT INTO transfer_requests (user_id, type, amount, method, status, account)
                      VALUES (?, 'withdraw', ?, ?, '待审核', ?)""",
                   (user_id, amount, method, account))
    cursor.execute("INSERT INTO wallet_logs (user_id, change, type, reason, status) VALUES (?, ?, 'withdraw', ?, '待审核')",
                   (user_id, -amount, f"{method}-{account}"))
    conn.commit()
    await msg.reply("提现申请已提交，请等待审核。")
    for admin_id in config.ADMINS:
        await bot.send_message(admin_id, f"新提现申请：用户{tg_id}，金额{amount}，方式{method}，账号/地址：{account}")
    conn.close()

async def handle_transfer_review(msg: types.Message, bot):
    if msg.from_user.id not in config.ADMINS:
        await msg.reply("无权限")
        return
    args = msg.text.split()
    if len(args) < 3:
        await msg.reply("用法：/review 订单号 approve/reject")
        return
    req_id, action = int(args[1]), args[2]
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, type, amount FROM transfer_requests WHERE id=? AND status='待审核'", (req_id,))
    row = cursor.fetchone()
    if not row:
        await msg.reply("订单不存在或已审核。")
        conn.close()
        return
    user_id, tx_type, amount = row
    if action == "approve":
        if tx_type == "recharge":
            cursor.execute("UPDATE users SET balance=balance+? WHERE id=?", (amount, user_id))
            cursor.execute("INSERT INTO wallet_logs (user_id, change, type, reason, status) VALUES (?, ?, 'recharge', '人工审核', '成功')",
                           (user_id, amount))
        elif tx_type == "withdraw":
            cursor.execute("UPDATE wallet_logs SET status='成功' WHERE user_id=? AND change=? AND type='withdraw'", (user_id, -amount))
        cursor.execute("UPDATE transfer_requests SET status='通过' WHERE id=?", (req_id,))
        await msg.reply("审核通过。")
    elif action == "reject":
        if tx_type == "withdraw":
            cursor.execute("UPDATE users SET balance=balance+? WHERE id=?", (amount, user_id))
            cursor.execute("UPDATE wallet_logs SET status='拒绝' WHERE user_id=? AND change=? AND type='withdraw'", (user_id, -amount))
        cursor.execute("UPDATE transfer_requests SET status='拒绝' WHERE id=?", (req_id,))
        await msg.reply("已拒绝。")
    conn.commit()
    conn.close()
