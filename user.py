import random, string
from aiogram import types
from db import get_conn

def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def handle_start(msg: types.Message, bot):
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
    user = cursor.fetchone()
    if not user:
        invite_code = generate_invite_code()
        cursor.execute("INSERT INTO users (tg_id, username, invite_code) VALUES (?, ?, ?)", (tg_id, msg.from_user.username, invite_code))
        conn.commit()
        await msg.reply(f"欢迎新用户，已为你自动注册。\n你的邀请码：{invite_code}\n可发送 /register 邀请码 绑定上级。")
    else:
        await msg.reply(f"欢迎回来！你的邀请码：{user[3]}")
    conn.close()

async def handle_register(msg: types.Message, bot):
    args = msg.text.split()
    if len(args) < 2:
        await msg.reply("用法：/register 邀请码")
        return
    invite_code = args[1]
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
    user = cursor.fetchone()
    if not user:
        await msg.reply("请先发送 /start 注册。")
        return
    # 查询邀请码对应用户id
    cursor.execute("SELECT id FROM users WHERE invite_code=?", (invite_code,))
    parent = cursor.fetchone()
    if not parent:
        await msg.reply("邀请码不存在。")
        return
    cursor.execute("UPDATE users SET inviter=? WHERE tg_id=?", (parent[0], tg_id))
    conn.commit()
    await msg.reply(f"邀请码 {invite_code} 绑定成功！")
    conn.close()
