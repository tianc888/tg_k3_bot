import asyncio
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
from db import init_db
import game, wallet, group, risk, rebate, admin

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
game.register_dice_handler(dp)

@dp.message_handler(commands=["start", "我的"])
async def my_menu(msg: types.Message):
    if msg.chat.type != 'private':
        return
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("充值", callback_data="recharge"),
        InlineKeyboardButton("提现", callback_data="withdraw"),
        InlineKeyboardButton("返利日志", callback_data="rebatelog"),
        InlineKeyboardButton("邀请信息", callback_data="inviteinfo"),
    )
    await msg.reply("请选择操作：", reply_markup=markup)

@dp.callback_query_handler(lambda call: call.data == "recharge")
async def inline_recharge(call: types.CallbackQuery):
    await wallet.handle_recharge(call.message, bot)
    await call.answer()

@dp.callback_query_handler(lambda call: call.data == "withdraw")
async def inline_withdraw(call: types.CallbackQuery):
    await wallet.handle_withdraw(call.message, bot)
    await call.answer()

@dp.callback_query_handler(lambda call: call.data == "rebatelog")
async def inline_rebatelog(call: types.CallbackQuery):
    await rebate.handle_rebate_log(call.message, bot)
    await call.answer()

@dp.callback_query_handler(lambda call: call.data == "inviteinfo")
async def inline_inviteinfo(call: types.CallbackQuery):
    await rebate.handle_invite_info(call.message, bot)
    await call.answer()

@dp.message_handler(commands=["balance", "余额"])
async def balance_cmd(msg: types.Message):
    if msg.chat.type != 'private':
        return
    await wallet.handle_balance(msg, bot)

@dp.message_handler(commands=["walletlog", "钱包日志"])
async def walletlog_cmd(msg: types.Message):
    if msg.chat.type != 'private':
        return
    await wallet.handle_wallet_log(msg, bot)

@dp.message_handler(commands=["recharge", "充值"])
async def recharge_cmd(msg: types.Message):
    if msg.chat.type != 'private':
        return
    await wallet.handle_recharge(msg, bot)

@dp.message_handler(commands=["withdraw", "提现"])
async def withdraw_cmd(msg: types.Message):
    if msg.chat.type != 'private':
        return
    await wallet.handle_withdraw(msg, bot)

@dp.message_handler(commands=["rebatelog", "返利日志"])
async def rebatelog_cmd(msg: types.Message):
    if msg.chat.type != 'private':
        return
    await rebate.handle_rebate_log(msg, bot)

@dp.message_handler(commands=["inviteinfo", "邀请信息"])
async def inviteinfo_cmd(msg: types.Message):
    if msg.chat.type != 'private':
        return
    await rebate.handle_invite_info(msg, bot)

# 管理员加余额功能
@dp.message_handler(lambda msg: (msg.reply_to_message or '@' in msg.text))
async def admin_add_balance_handler(msg: types.Message):
    # 判断管理员身份
    if msg.from_user.id not in config.ADMINS:
        return
    text = msg.text.strip().replace("＋", "+")  # 支持全角+
    if not text.startswith("+"):
        return
    try:
        amount = int(text[1:])
    except Exception:
        return
    target_id = None
    target_name = "用户"
    # 回复方式
    if msg.reply_to_message:
        target_id = msg.reply_to_message.from_user.id
        target_name = msg.reply_to_message.from_user.full_name
    # @方式
    elif '@' in text:
        for ent in msg.entities or []:
            if ent.type == 'mention':
                username = msg.text[ent.offset+1:ent.offset+ent.length]
                from wallet import get_uid_by_username
                target_id = get_uid_by_username(username)
                target_name = f"@{username}"
    if not target_id:
        await msg.reply("请通过回复玩家消息或@玩家来增加余额。")
        return
    from wallet import change_user_balance, get_user_balance
    change_user_balance(target_id, amount, "管理员加余额", f"管理员@{msg.from_user.full_name} 操作")
    new_balance = get_user_balance(target_id)
    await msg.reply(f"{target_name} 已加余额{amount}，当前余额：{new_balance}")

# 取消下注中文命令
@dp.message_handler(lambda msg: msg.text.strip() in ["取消", "取消下注"])
async def cancel_cmd_zh(msg: types.Message):
    if msg.chat.type not in ['group', 'supergroup']:
        return
    await game.handle_cancel(msg, bot)

# 下注入口（所有玩法）
@dp.message_handler(lambda msg: msg.chat.type in ['group', 'supergroup'])
async def bet_all_handler(msg: types.Message):
    await game.handle_bet(msg, bot)
    # 记住username映射
    if msg.from_user.username:
        from wallet import remember_username
        remember_username(msg.from_user.id, msg.from_user.username)

@dp.message_handler(commands=["report", "报表"])
async def report_cmd(msg: types.Message):
    await admin.handle_report(msg, bot)

@dp.message_handler(commands=["kick", "踢人"])
async def kick_cmd(msg: types.Message):
    await group.handle_kick(msg, bot)

@dp.message_handler(commands=["mute", "禁言"])
async def mute_cmd(msg: types.Message):
    await group.handle_mute(msg, bot)

@dp.message_handler(commands=["blacklist", "拉黑"])
async def blacklist_cmd(msg: types.Message):
    await risk.handle_blacklist(msg, bot)

@dp.message_handler(commands=["whitelist", "白名单"])
async def whitelist_cmd(msg: types.Message):
    await risk.handle_whitelist(msg, bot)

@dp.message_handler(lambda msg: msg.chat.type in ['group', 'supergroup'])
async def keyword_reply_hook(msg: types.Message):
    await group.handle_keyword_reply(msg, bot)

def get_admin_link():
    admin_id = config.ADMINS[0] if config.ADMINS else None
    if admin_id:
        return f"https://t.me/{config.BOT_USERNAME}" if isinstance(admin_id, str) else f"https://t.me/user?id={admin_id}"
    return "https://t.me/"

def get_bot_link():
    return f"https://t.me/{config.BOT_USERNAME}"

async def lottery_round():
    group_id = config.GROUP_ID
    game.config_group_id(group_id)
    while True:
        period_code = await game.start_new_round()
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        open_time = now
        close_time = open_time + datetime.timedelta(seconds=45)

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("联系客服", url=get_admin_link()),
            InlineKeyboardButton("充值/提现", url=get_bot_link()),
        )

        open_text = (
            f"--YLttK3第{period_code}期\n"
            f"本期封盘：{close_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"\n" * 5 +
            "--本期已开盘，玩家请开始下注"
        )
        await bot.send_message(group_id, open_text, reply_markup=markup)

        await asyncio.sleep(43)

        if game.current_round and game.current_round.get_bets():
            betlines = "\n".join(
                f"{u} {uid} {bt or ''}{amt}"
                for uid, amt, u, bt in game.current_round.get_bets()
            ) or ""
            close_text = (
                f"--YLttK3第{period_code}期\n"
                f"本期封盘时间：{close_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"{betlines}\n\n"
                "--本期已封盘，请停止下注\n"
                "--轻触【🎲】复制投掷\n"
                "请在15秒内掷出3颗骰子，超时系统自动补发，无任何争议"
            )
            await bot.send_message(group_id, close_text)
            game.current_round.is_closed = True
            player_dice = await game.collect_player_dice(group_id, 15)
            while len(player_dice) < 3:
                dice = await bot.send_dice(group_id)
                player_dice.append(dice.dice.value)
            await asyncio.sleep(1.5)
            result_str = "+".join(map(str, player_dice))
            total = sum(player_dice)
            await bot.send_message(
                group_id,
                f"--YLttK3第{period_code}期输赢\n\n骰子为：{result_str}={total}"
            )
            await game.settle_bets(player_dice)
        else:
            no_bet_close_text = (
                f"--YLttK3第{period_code}期\n"
                f"本期封盘时间：{close_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "--本期封盘，没有玩家下注，系统自动投掷骰子"
            )
            await bot.send_message(group_id, no_bet_close_text)
            results = [await bot.send_dice(group_id) for _ in range(3)]
            values = [d.dice.value for d in results]
            await asyncio.sleep(1.5)
            result_str = "+".join(map(str, values))
            total = sum(values)
            await bot.send_message(
                group_id,
                f"--YLttK3第{period_code}期输赢\n\n骰子为：{result_str}={total}\n本期流局"
            )
            await game.settle_no_bet(values)
        await asyncio.sleep(1)

async def main():
    init_db()
    asyncio.create_task(lottery_round())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
