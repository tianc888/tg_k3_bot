from aiogram import types
from db import get_conn
import time

BET_MIN = 1
BET_MAX = 10000
BET_FREQUENCY_LIMIT = 5

def is_blacklisted(tg_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM blacklist WHERE tg_id=?", (tg_id,))
    ret = cursor.fetchone()
    conn.close()
    return bool(ret)

def is_whitelisted(tg_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM whitelist WHERE tg_id=?", (tg_id,))
    ret = cursor.fetchone()
    conn.close()
    return bool(ret)

def log_risk(user_id, event, detail=""):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO risk_logs (user_id, event, detail) VALUES (?, ?, ?)", (user_id, event, detail))
    conn.commit()
    conn.close()

freq_cache = {}

def check_bet_limit(tg_id, amount):
    if amount < BET_MIN or amount > BET_MAX:
        return False, f"单注金额需在{BET_MIN}-{BET_MAX}元之间"
    now = int(time.time())
    freq_cache.setdefault(tg_id, [])
    freq_cache[tg_id] = [ts for ts in freq_cache[tg_id] if now - ts < 60]
    if len(freq_cache[tg_id]) >= BET_FREQUENCY_LIMIT:
        return False, "操作过于频繁，请稍后再试"
    freq_cache[tg_id].append(now)
    return True, ""

async def handle_blacklist(msg: types.Message, bot):
    args = msg.text.split()
    if len(args) < 3:
        await msg.reply("用法：/blacklist add/del tg_id [reason]")
        return
    op, tg_id = args[1], int(args[2])
    reason = args[3] if len(args) > 3 else ""
    conn = get_conn()
    cursor = conn.cursor()
    if op == "add":
        cursor.execute("INSERT OR IGNORE INTO blacklist (tg_id, reason) VALUES (?, ?)", (tg_id, reason))
        await msg.reply(f"{tg_id} 已加入黑名单")
    elif op == "del":
        cursor.execute("DELETE FROM blacklist WHERE tg_id=?", (tg_id,))
        await msg.reply(f"{tg_id} 已移出黑名单")
    conn.commit()
    conn.close()

async def handle_whitelist(msg: types.Message, bot):
    args = msg.text.split()
    if len(args) < 3:
        await msg.reply("用法：/whitelist add/del tg_id")
        return
    op, tg_id = args[1], int(args[2])
    conn = get_conn()
    cursor = conn.cursor()
    if op == "add":
        cursor.execute("INSERT OR IGNORE INTO whitelist (tg_id) VALUES (?)", (tg_id,))
        await msg.reply(f"{tg_id} 已加入白名单")
    elif op == "del":
        cursor.execute("DELETE FROM whitelist WHERE tg_id=?", (tg_id,))
        await msg.reply(f"{tg_id} 已移出白名单")
    conn.commit()
    conn.close()

async def handle_risklogs(msg: types.Message, bot):
    tg_id = msg.from_user.id
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE tg_id=?", (tg_id,))
    row = cursor.fetchone()
    if not row:
        await msg.reply("请先注册")
        return
    user_id = row[0]
    cursor.execute("SELECT event, detail, create_time FROM risk_logs WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    rows = cursor.fetchall()
    text = "最近10条风控记录：\n"
    for r in rows:
        text += f"{r[2][:16]} | {r[0]} | {r[1]}\n"
    await msg.reply(text or "暂无风控记录")
    conn.close()
