from aiogram import types
from db import get_conn
import config

async def handle_blacklist(msg: types.Message, bot):
    if not msg.reply_to_message:
        await msg.reply("请回复要拉黑的成员消息。")
        return
    user_id = msg.reply_to_message.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO blacklist (tg_id, reason) VALUES (?, ?)", (user_id, "群内拉黑"))
    conn.commit()
    conn.close()
    await msg.reply("已拉黑该成员。")

async def handle_whitelist(msg: types.Message, bot):
    if not msg.reply_to_message:
        await msg.reply("请回复要移出黑名单的成员消息。")
        return
    user_id = msg.reply_to_message.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blacklist WHERE tg_id=?", (user_id,))
    conn.commit()
    conn.close()
    await msg.reply("已移出黑名单。")
