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

async def handle_userlist(msg: types.Message, bot):
    if msg.from_user.id not in config.ADMINS:
        await msg.reply("无权限")
        return
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT tg_id, username, balance FROM users ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    text = "最近10个用户：\n"
    for r in rows:
        text += f"TG:{r[0]} | 用户名:{r[1]} | 余额:{r[2]:.2f}\n"
    await msg.reply(text)
    conn.close()

async def handle_orderlist(msg: types.Message, bot):
    if msg.from_user.id not in config.ADMINS:
        await msg.reply("无权限")
        return
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, game_type, bet_content, amount, status, win_amount FROM orders ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    text = "最近10个订单：\n"
    for r in rows:
        text += f"单号:{r[0]} | 用户:{r[1]} | 玩法:{r[2]} | 内容:{r[3]} | 金额:{r[4]:.2f} | 状态:{r[5]} | 中奖:{r[6]:.2f}\n"
    await msg.reply(text)
    conn.close()

async def handle_agentlist(msg: types.Message, bot):
    if msg.from_user.id not in config.ADMINS:
        await msg.reply("无权限")
        return
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, tg_id, username, invite_code FROM users WHERE level>0 ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    text = "最近10个代理：\n"
    for r in rows:
        text += f"ID:{r[0]} | TG:{r[1]} | 用户名:{r[2]} | 邀请码:{r[3]}\n"
    await msg.reply(text)
    conn.close()

async def handle_announce(msg: types.Message, bot):
    if msg.from_user.id not in config.ADMINS:
        await msg.reply("无权限")
        return
    args = msg.text.split(maxsplit=2)
    if len(args) < 3:
        await msg.reply("用法：/announce 标题 内容")
        return
    title, content = args[1], args[2]
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO announcements (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    cursor.execute("SELECT tg_id FROM users")
    users = cursor.fetchall()
    for u in users:
        try:
            await bot.send_message(u[0], f"【公告】{title}\n{content}")
        except:
            continue
    await msg.reply("公告已推送。")
    conn.close()

import shutil
import os
async def handle_backup(msg: types.Message, bot):
    if msg.from_user.id not in config.ADMINS:
        await msg.reply("无权限")
        return
    src = config.DATABASE
    dst = f"{src}.bak"
    shutil.copyfile(src, dst)
    await msg.reply(f"数据库已备份为 {dst}")

async def handle_restore(msg: types.Message, bot):
    if msg.from_user.id not in config.ADMINS:
        await msg.reply("无权限")
        return
    src = f"{config.DATABASE}.bak"
    dst = config.DATABASE
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        await msg.reply("数据库已恢复。")
    else:
        await msg.reply("未找到备份文件。")
