from aiogram import types
from db import get_conn

async def handle_rebate_log(msg: types.Message, bot):
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE tg_id=?", (tg_id,))
    row = cursor.fetchone()
    if not row:
        await msg.reply("请先注册")
        return
    user_id = row[0]
    cursor.execute("SELECT amount, from_user_id, level, create_time FROM rebate_logs WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    rows = cursor.fetchall()
    text = "最近10条返佣记录：\n"
    for r in rows:
        text += f"{r[3][:16]} | +{r[0]:.2f}元 | 下级ID:{r[1]} | {r[2]}级\n"
    await msg.reply(text or "暂无返佣记录")
    conn.close()

async def handle_invite_info(msg: types.Message, bot):
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, invite_code FROM users WHERE tg_id=?", (tg_id,))
    row = cursor.fetchone()
    if not row:
        await msg.reply("请先注册")
        return
    user_id, invite_code = row
    cursor.execute("SELECT COUNT(*) FROM users WHERE inviter=?", (user_id,))
    count = cursor.fetchone()[0]
    await msg.reply(f"你的邀请码：{invite_code}\n你的直属下级人数：{count}")
    conn.close()
