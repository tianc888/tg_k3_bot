from aiogram import types
from db import get_conn
import config

async def handle_balance(msg: types.Message, bot):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE tg_id=?", (msg.from_user.id,))
    row = cursor.fetchone()
    balance = row[0] if row else 0
    await msg.reply(f"您的余额为：{balance:.2f} 元")
    conn.close()

async def handle_wallet_log(msg: types.Message, bot):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT change, type, reason, status, create_time FROM wallet_logs WHERE user_id=(SELECT id FROM users WHERE tg_id=?) ORDER BY id DESC LIMIT 10", (msg.from_user.id,))
    rows = cursor.fetchall()
    if not rows:
        await msg.reply("暂无钱包流水记录。")
    else:
        text = "最近10条钱包流水：\n"
        for r in rows:
            text += f"{r[4][:16]} | {r[1]} | {r[2]} | {r[0]:.2f} | {r[3]}\n"
        await msg.reply(text)
    conn.close()

async def handle_recharge(msg: types.Message, bot):
    await msg.reply("请联系管理员或通过指定方式充值。\n（示例功能，可自定义实现充值流程）")

async def handle_withdraw(msg: types.Message, bot):
    await msg.reply("请联系管理员或通过指定方式提现。\n（示例功能，可自定义实现提现流程）")
