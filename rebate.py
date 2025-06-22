from aiogram import types
from db import get_conn

async def handle_rebate_log(msg: types.Message, bot):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT amount, level, from_user, create_time FROM rebates WHERE user_id=(SELECT id FROM users WHERE tg_id=?) ORDER BY id DESC LIMIT 10", (msg.from_user.id,))
    rows = cursor.fetchall()
    if not rows:
        await msg.reply("暂无返利日志。")
    else:
        text = "最近10条返利日志：\n"
        for r in rows:
            text += f"{r[3][:16]} | 金额:{r[0]:.2f} | 来自:{r[2]} | 等级:{r[1]}\n"
        await msg.reply(text)
    conn.close()

async def handle_invite_info(msg: types.Message, bot):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT invite_code FROM users WHERE tg_id=?", (msg.from_user.id,))
    code = cursor.fetchone()
    code = code[0] if code else "未设置"
    cursor.execute("SELECT COUNT(*) FROM users WHERE inviter=(SELECT id FROM users WHERE tg_id=?)", (msg.from_user.id,))
    num = cursor.fetchone()
    num = num[0] if num else 0
    await msg.reply(f"您的邀请码：{code}\n邀请人数：{num}\n返佣比例：10%/5%/2%")
    conn.close()
