import random
from aiogram import types
from db import get_conn
import asyncio
from datetime import datetime
import risk

GAME_TYPES = ['大小单双', '和值', '三同号', '豹子', '顺子']

def generate_k3_numbers():
    return [random.randint(1, 6) for _ in range(3)]

def analyze_result(numbers):
    nums = sorted(numbers)
    total = sum(nums)
    result = {
        "和值": total,
        "豹子": nums[0] == nums[1] == nums[2],
        "三同号": nums[0] == nums[1] == nums[2],
        "顺子": nums in ([1,2,3],[2,3,4],[3,4,5],[4,5,6]),
        "大": total > 10,
        "小": total <= 10,
        "单": total % 2 == 1,
        "双": total % 2 == 0
    }
    return result

async def auto_lottery_task(bot):
    while True:
        now = datetime.now()
        period = now.strftime("%Y%m%d%H%M")
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM lottery_history WHERE period=?", (period,))
        if not cursor.fetchone():
            numbers = generate_k3_numbers()
            cursor.execute("INSERT INTO lottery_history (period, numbers) VALUES (?, ?)", (period, ','.join(map(str,numbers))))
            conn.commit()
            cursor.execute("SELECT group_id FROM groups")
            groups = cursor.fetchall()
            msg = f"第{period}期 开奖结果：{' '.join(map(str, numbers))}\n"
            result = analyze_result(numbers)
            for k,v in result.items():
                msg += f"{k}:{v} "
            for g in groups:
                try:
                    await bot.send_message(g[0], msg)
                except:
                    pass
        conn.close()
        await asyncio.sleep(60*5)

async def handle_bet(msg: types.Message, bot):
    tg_id = msg.from_user.id
    if risk.is_blacklisted(tg_id):
        await msg.reply("您已被列入黑名单，无法操作。")
        return
    if not risk.is_whitelisted(tg_id):
        try:
            amount = float(msg.text.split()[2])
        except:
            await msg.reply("金额格式错误")
            return
        ok, info = risk.check_bet_limit(tg_id, amount)
        if not ok:
            await msg.reply(info)
            return
    args = msg.text.split()
    if len(args) < 4:
        await msg.reply("用法示例：/bet 大小 10 大")
        return
    game_type, amount, bet_content = args[1], float(args[2]), args[3]
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, balance FROM users WHERE tg_id=?", (tg_id,))
    u = cursor.fetchone()
    if not u: await msg.reply("请先注册。"); return
    user_id, balance = u
    if amount > balance:
        await msg.reply("余额不足。")
        return
    cursor.execute("UPDATE users SET balance=balance-? WHERE id=?", (amount, user_id))
    period = datetime.now().strftime("%Y%m%d%H%M")
    cursor.execute("INSERT INTO orders (user_id, game_type, bet_content, period, amount, status) VALUES (?,?,?,?,?,?)",
                   (user_id, game_type, bet_content, period, amount, "待开奖"))
    cursor.execute("INSERT INTO wallet_logs (user_id, change, type, reason) VALUES (?, ?, ?, ?)",
                   (user_id, -amount, "bet", f"{game_type}-{bet_content}"))
    conn.commit()
    await msg.reply(f"下注成功，期号：{period}，玩法：{game_type}，内容：{bet_content}，金额：{amount}")
    conn.close()

async def handle_lottery_history(msg: types.Message, bot):
    args = msg.text.split()
    count = int(args[1]) if len(args)>1 else 10
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT period, numbers FROM lottery_history ORDER BY period DESC LIMIT ?", (count,))
    rows = cursor.fetchall()
    text = "最近开奖：\n" + '\n'.join([f"{r[0]}: {r[1]}" for r in rows])
    await msg.reply(text)
    conn.close()

async def handle_chase(msg: types.Message, bot):
    args = msg.text.split()
    if len(args) < 7:
        await msg.reply("用法：/chase 玩法 金额 内容 期数 止盈(元) 止损(元)\n例如：/chase 大小 10 大 5 100 30")
        return
    game_type, amount, bet_content, period_count, stop_win, stop_loss = args[1], float(args[2]), args[3], int(args[4]), float(args[5]), float(args[6])
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, balance FROM users WHERE tg_id=?", (tg_id,))
    u = cursor.fetchone()
    if not u: await msg.reply("请先注册。"); return
    user_id, balance = u
    if balance < amount:
        await msg.reply("余额不足，至少需要一注金额。")
        return
    now = datetime.now()
    period_start = now.strftime("%Y%m%d%H%M")
    cursor.execute("""
        INSERT INTO chase_orders 
        (user_id, bet_content, game_type, period_start, period_count, stop_win, stop_loss, active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (user_id, bet_content, game_type, period_start, period_count, stop_win, stop_loss))
    conn.commit()
    await msg.reply(f"追号创建成功！从{period_start}起，{period_count}期，每期{amount}元，止盈{stop_win}元，止损{stop_loss}元。")
    conn.close()

async def chase_auto_bet(bot):
    while True:
        now = datetime.now()
        period = now.strftime("%Y%m%d%H%M")
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chase_orders WHERE active=1")
        chase_orders = cursor.fetchall()
        for order in chase_orders:
            oid, user_id, bet_content, game_type, period_start, period_count, finished_count, stop_win, stop_loss, active, win_sum, loss_sum, _ = order
            if finished_count >= period_count or not active:
                cursor.execute("UPDATE chase_orders SET active=0 WHERE id=?", (oid,))
                continue
            if win_sum >= stop_win or loss_sum >= stop_loss:
                cursor.execute("UPDATE chase_orders SET active=0 WHERE id=?", (oid,))
                continue
            cursor.execute("SELECT 1 FROM orders WHERE user_id=? AND period=? AND game_type=? AND bet_content=?", (user_id, period, game_type, bet_content))
            if cursor.fetchone():
                continue
            cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
            bal = cursor.fetchone()
            if not bal or bal[0] < 1:
                continue
            amount = 10
            if bal[0] < amount:
                continue
            cursor.execute("UPDATE users SET balance=balance-? WHERE id=?", (amount, user_id))
            cursor.execute("""INSERT INTO orders (user_id, game_type, bet_content, period, amount, status)
                              VALUES (?, ?, ?, ?, ?, ?)""",
                           (user_id, game_type, bet_content, period, amount, "待开奖"))
            cursor.execute("INSERT INTO wallet_logs (user_id, change, type, reason) VALUES (?, ?, ?, ?)",
                           (user_id, -amount, "chase-bet", f"{game_type}-{bet_content}"))
            cursor.execute("UPDATE chase_orders SET finished_count=finished_count+1 WHERE id=?", (oid,))
        conn.commit()
        conn.close()
        await asyncio.sleep(60*5)

def get_parent_chain(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    chain = []
    cur_id = user_id
    for _ in range(3):
        cursor.execute("SELECT inviter FROM users WHERE id=?", (cur_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            break
        chain.append(row[0])
        cur_id = row[0]
    conn.close()
    return chain

def add_rebate(user_id, from_user_id, order_id, amount, level):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance=balance+? WHERE id=?", (amount, user_id))
    cursor.execute("""INSERT INTO wallet_logs (user_id, change, type, reason) VALUES (?, ?, 'rebate', '代理返佣')""",
                   (user_id, amount))
    cursor.execute("""INSERT INTO rebate_logs (user_id, from_user_id, order_id, amount, level) VALUES (?,?,?,?,?)""",
                   (user_id, from_user_id, order_id, amount, level))
    conn.commit()
    conn.close()

async def settle_orders_and_payout(bot):
    from config import REBATE_LEVELS
    while True:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, game_type, bet_content, period, amount FROM orders WHERE status='待开奖'")
        orders = cursor.fetchall()
        for oid, user_id, game_type, bet_content, period, amount in orders:
            cursor.execute("SELECT numbers FROM lottery_history WHERE period=?", (period,))
            row = cursor.fetchone()
            if not row:
                continue
            numbers = list(map(int, row[0].split(',')))
            result = analyze_result(numbers)
            win = False
            win_amount = 0
            if game_type == "大小单双":
                if bet_content in ("大", "小") and result[bet_content]:
                    win = True
                elif bet_content in ("单", "双") and result[bet_content]:
                    win = True
            elif game_type == "和值":
                if str(result["和值"]) == bet_content:
                    win = True
            elif game_type == "豹子":
                if result["豹子"]:
                    win = True
            elif game_type == "三同号":
                if result["三同号"]:
                    win = True
            elif game_type == "顺子":
                if result["顺子"]:
                    win = True
            if win:
                win_amount = amount * 2
                cursor.execute("UPDATE users SET balance=balance+? WHERE id=?", (win_amount, user_id))
                cursor.execute("INSERT INTO wallet_logs (user_id, change, type, reason) VALUES (?, ?, ?, ?)",
                               (user_id, win_amount, "win", f"{game_type}-{bet_content}"))
                cursor.execute("UPDATE orders SET status='已中奖', win_amount=? WHERE id=?", (win_amount, oid))
                cursor.execute("UPDATE chase_orders SET win_sum=win_sum+? WHERE user_id=? AND active=1", (win_amount-amount, user_id))
            else:
                cursor.execute("UPDATE orders SET status='未中奖', win_amount=0 WHERE id=?", (oid,))
                cursor.execute("UPDATE chase_orders SET loss_sum=loss_sum+? WHERE user_id=? AND active=1", (amount, user_id))
            # 结算返佣
            chain = get_parent_chain(user_id)
            from config import REBATE_LEVELS
            for idx, pid in enumerate(chain):
                if idx < len(REBATE_LEVELS):
                    rebate = amount * REBATE_LEVELS[idx]
                    add_rebate(pid, user_id, oid, rebate, idx + 1)
        conn.commit()
        conn.close()
        await asyncio.sleep(60)

async def handle_chase_list(msg: types.Message, bot):
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE tg_id=?", (tg_id,))
    row = cursor.fetchone()
    if not row:
        await msg.reply("请先注册")
        return
    user_id = row[0]
    cursor.execute("SELECT id, game_type, bet_content, period_start, period_count, finished_count, active, win_sum, loss_sum FROM chase_orders WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    text = "您的追号单：\n"
    for r in rows:
        text += f"单号:{r[0]}, 玩法:{r[1]}, 内容:{r[2]}, 起始期:{r[3]}, 总期数:{r[4]}, 已完成:{r[5]}, 状态:{'进行中' if r[6] else '已结束'}, 盈利:{r[7]}, 亏损:{r[8]}\n"
    await msg.reply(text or "暂无追号单")
    conn.close()

async def handle_trend(msg: types.Message, bot):
    args = msg.text.split()
    count = int(args[1]) if len(args) > 1 else 20
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT numbers FROM lottery_history ORDER BY period DESC LIMIT ?", (count,))
    rows = cursor.fetchall()
    hezhi = [sum(map(int, row[0].split(','))) for row in rows]
    text = f"近{count}期和值走势：\n" + ' '.join(map(str, hezhi))
    await msg.reply(text)
    conn.close()
