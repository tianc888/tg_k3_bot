from aiogram import types
from db import get_conn
import config

async def handle_report(msg: types.Message, bot):
    if msg.from_user.id not in config.ADMINS:
        await msg.reply("无权限")
        return
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(balance) FROM users")
    u_count, u_sum = cursor.fetchone()
    cursor.execute("SELECT COUNT(*), SUM(amount), SUM(win_amount) FROM orders")
    o_count, o_sum, win_sum = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='已中奖'")
    win_orders = cursor.fetchone()[0]
    text = (f"用户数：{u_count}\n用户总余额：{u_sum or 0:.2f}\n"
            f"订单数：{o_count}\n下注总额：{o_sum or 0:.2f}\n"
            f"总中奖金额：{win_sum or 0:.2f}\n中奖订单数：{win_orders}")
    await msg.reply(text)
    conn.close()
