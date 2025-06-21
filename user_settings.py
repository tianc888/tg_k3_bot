from aiogram import types
from db import get_conn

async def handle_set_notify(msg: types.Message, bot):
    args = msg.text.split()
    if len(args) < 3:
        await msg.reply("用法：/setnotify 开奖提醒/盈亏提醒 on/off")
        return
    tg_id = msg.from_user.id
    setting, value = args[1], args[2]
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE tg_id=?", (tg_id,))
    row = cursor.fetchone()
    if not row:
        await msg.reply("请先注册")
        return
    user_id = row[0]
    if setting not in ("开奖提醒", "盈亏提醒"):
        await msg.reply("只支持 开奖提醒/盈亏提醒")
        return
    key = "notify_lottery" if setting == "开奖提醒" else "notify_profit"
    cursor.execute("REPLACE INTO user_settings (user_id, setting_key, setting_value) VALUES (?, ?, ?)", (user_id, key, value))
    conn.commit()
    await msg.reply(f"{setting} 已设置为 {value}")
    conn.close()

async def handle_set_lang(msg: types.Message, bot):
    args = msg.text.split()
    if len(args) < 2 or args[1] not in ("zh", "en"):
        await msg.reply("用法：/setlang zh/en")
        return
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE tg_id=?", (tg_id,))
    row = cursor.fetchone()
    if not row:
        await msg.reply("请先注册")
        return
    user_id = row[0]
    cursor.execute("REPLACE INTO user_settings (user_id, setting_key, setting_value) VALUES (?, ?, ?)", (user_id, "lang", args[1]))
    conn.commit()
    await msg.reply(f"已切换语言为 {args[1]}")
    conn.close()

def get_user_setting(user_id, key, default=None):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT setting_value FROM user_settings WHERE user_id=? AND setting_key=?", (user_id, key))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return default
