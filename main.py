from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
import asyncio
import config
from db import init_db, get_conn

import user
import game
import wallet
import group
import risk
import rebate
import user_settings
import admin

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ===== 私聊功能：仅允许余额、钱包日志、充值、提现、菜单 =====
@dp.message_handler(commands=["start", "我的"], chat_type=['private'])
async def my_menu(msg: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("充值"), KeyboardButton("提现"))
    await msg.reply("请选择操作：", reply_markup=markup)

@dp.message_handler(commands=["balance", "余额"], chat_type=['private'])
async def balance_cmd(msg: types.Message):
    await wallet.handle_balance(msg, bot)

@dp.message_handler(commands=["walletlog", "钱包日志"], chat_type=['private'])
async def walletlog_cmd(msg: types.Message):
    await wallet.handle_wallet_log(msg, bot)

@dp.message_handler(commands=["recharge", "充值"], chat_type=['private'])
async def recharge_cmd(msg: types.Message):
    await wallet.handle_recharge(msg, bot)

@dp.message_handler(commands=["withdraw", "提现"], chat_type=['private'])
async def withdraw_cmd(msg: types.Message):
    await wallet.handle_withdraw(msg, bot)

@dp.message_handler(chat_type=['private'])
async def private_only(msg: types.Message):
    await msg.reply("请到群组进行投注和开奖结果等操作。")

# ===== 群组功能：投注、开奖、历史等（支持中英文命令） =====
@dp.message_handler(commands=["bet", "下注"], chat_type=['group', 'supergroup'])
async def bet_cmd(msg: types.Message):
    await game.handle_bet(msg, bot)

@dp.message_handler(commands=["history", "开奖历史"], chat_type=['group', 'supergroup'])
async def history_cmd(msg: types.Message):
    await game.handle_lottery_history(msg, bot)

@dp.message_handler(commands=["trend", "走势"], chat_type=['group', 'supergroup'])
async def trend_cmd(msg: types.Message):
    await game.handle_trend(msg, bot)

# 返利/邀请
@dp.message_handler(commands=["rebatelog", "返利日志"], chat_type=['group', 'supergroup'])
async def rebatelog_cmd(msg: types.Message):
    await rebate.handle_rebate_log(msg, bot)

@dp.message_handler(commands=["inviteinfo", "邀请信息"], chat_type=['group', 'supergroup'])
async def inviteinfo_cmd(msg: types.Message):
    await rebate.handle_invite_info(msg, bot)

# 群管理
@dp.message_handler(commands=["kick", "踢人"], chat_type=['group', 'supergroup'])
async def kick_cmd(msg: types.Message):
    await group.handle_kick(msg, bot)

@dp.message_handler(commands=["mute", "禁言"], chat_type=['group', 'supergroup'])
async def mute_cmd(msg: types.Message):
    await group.handle_mute(msg, bot)

# 风控
@dp.message_handler(commands=["blacklist", "拉黑"], chat_type=['group', 'supergroup'])
async def blacklist_cmd(msg: types.Message):
    await risk.handle_blacklist(msg, bot)

@dp.message_handler(commands=["whitelist", "白名单"], chat_type=['group', 'supergroup'])
async def whitelist_cmd(msg: types.Message):
    await risk.handle_whitelist(msg, bot)

# 管理员
@dp.message_handler(commands=["report", "报表"], chat_type=['group', 'supergroup'])
async def report_cmd(msg: types.Message):
    await admin.handle_report(msg, bot)

# 关键词回复
@dp.message_handler(chat_type=['group', 'supergroup'])
async def keyword_reply_hook(msg: types.Message):
    await group.handle_keyword_reply(msg, bot)

# ===== 每期45秒自动开奖/封盘/投掷骰子逻辑 =====
async def lottery_round():
    group_id = config.GROUP_ID  # 群组ID需在config中配置
    while True:
        await bot.send_message(group_id, "新一期开始，45秒后封盘，请下注…")
        await game.start_new_round()
        await asyncio.sleep(45)
        bets = await game.get_current_bets()
        if not bets:
            await bot.send_message(group_id, "本期封盘，未检测到下注，开始投掷三颗🎲")
            results = [await bot.send_dice(group_id) for _ in range(3)]
            values = [d.result.value for d in results]
            await bot.send_message(group_id, f"开奖结果：{' '.join(str(v) for v in values)}")
            await game.settle_no_bet(values)
        else:
            await bot.send_message(group_id, "本期封盘，停止下注，请玩家在15秒内投掷三颗🎲")
            player_dice = await game.collect_player_dice(group_id, 15)
            while len(player_dice) < 3:
                dice = await bot.send_dice(group_id)
                player_dice.append(dice.result.value)
            await bot.send_message(group_id, f"开奖结果：{' '.join(str(v) for v in player_dice)}")
            await game.settle_bets(player_dice)
        await asyncio.sleep(1)  # 稍作延迟避免冲突

async def main():
    init_db()
    asyncio.create_task(lottery_round())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
