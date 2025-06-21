from aiogram import types
from db import get_conn

async def handle_kick(msg: types.Message, bot):
    if msg.chat.type not in ["group", "supergroup"]:
        await msg.reply("请在群聊中使用")
        return
    if not msg.reply_to_message:
        await msg.reply("请回复要踢出的用户消息")
        return
    user_id = msg.reply_to_message.from_user.id
    await bot.ban_chat_member(msg.chat.id, user_id)
    await msg.reply(f"已踢出用户 {user_id}")

async def handle_mute(msg: types.Message, bot):
    if msg.chat.type not in ["group", "supergroup"]:
        await msg.reply("请在群聊中使用")
        return
    if not msg.reply_to_message:
        await msg.reply("请回复要禁言的用户消息")
        return
    user_id = msg.reply_to_message.from_user.id
    until_date = types.ChatPermissions(can_send_messages=False)
    await bot.restrict_chat_member(msg.chat.id, user_id, until_date)
    await msg.reply(f"已禁言用户 {user_id}")

async def handle_set_param(msg: types.Message, bot):
    # 仅超级管理员可用
    from config import ADMINS
    if not msg.from_user.id in ADMINS:
        await msg.reply("无权限")
        return
    args = msg.text.split()
    if len(args) < 3:
        await msg.reply("用法：/setparam 参数名 参数值")
        return
    param, value = args[1], args[2]
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO settings (name, value) VALUES (?, ?)", (param, value))
    conn.commit()
    conn.close()
    await msg.reply(f"参数 {param} 已设置为 {value}")

async def handle_add_keyword(msg: types.Message, bot):
    from config import ADMINS
    if not msg.from_user.id in ADMINS:
        await msg.reply("无权限")
        return
    args = msg.text.split(maxsplit=2)
    if len(args) < 3:
        await msg.reply("用法：/addkw 关键词 回复内容")
        return
    keyword, reply = args[1], args[2]
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO auto_reply (keyword, reply) VALUES (?, ?)", (keyword, reply))
    conn.commit()
    conn.close()
    await msg.reply(f"关键词 {keyword} 的自动回复已设置")

async def handle_keyword_reply(msg: types.Message, bot):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT reply FROM auto_reply WHERE keyword=?", (msg.text,))
    row = cursor.fetchone()
    if row:
        await msg.reply(row[0])
    conn.close()
