from aiogram import types
from db import get_conn
import config

async def handle_kick(msg: types.Message, bot):
    if not msg.reply_to_message:
        await msg.reply("请回复要踢出的成员消息。")
        return
    user_id = msg.reply_to_message.from_user.id
    try:
        await bot.kick_chat_member(msg.chat.id, user_id)
        await msg.reply("已踢出该成员。")
    except Exception:
        await msg.reply("操作失败，可能无权限。")

async def handle_mute(msg: types.Message, bot):
    if not msg.reply_to_message:
        await msg.reply("请回复要禁言的成员消息。")
        return
    user_id = msg.reply_to_message.from_user.id
    try:
        await bot.restrict_chat_member(msg.chat.id, user_id, can_send_messages=False)
        await msg.reply("已禁言该成员。")
    except Exception:
        await msg.reply("操作失败，可能无权限。")

async def handle_keyword_reply(msg: types.Message, bot):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT reply FROM auto_reply WHERE keyword=?", (msg.text.strip(),))
    row = cursor.fetchone()
    if row:
        await msg.reply(row[0])
    conn.close()
