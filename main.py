from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command, Regexp
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

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# 注册骰子handler（只需要注册一次）
game.register_dice_handler(dp)

# ===== 私聊功能：余额、钱包日志、充值、提现、菜单（内联键盘版），全部支持“中文无/” =====

@dp.message_handler(commands=["start", "我的"], chat_type=['private'])
async def my_menu(msg: types.Message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("充值", callback_data="recharge"),
        InlineKeyboardButton("提现", callback_data="withdraw"),
        InlineKeyboardButton("返利日志", callback_data="rebatelog"),
        InlineKeyboardButton("邀请信息", callback_data="inviteinfo"),
    )
    await msg.reply("请选择操作：", reply_markup=markup)

# 内联键盘的回调处理
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

# ====== 私聊指令：支持/和纯中文 ======
@dp.message_handler(commands=["balance", "余额"], chat_type=['private'])
async def balance_cmd(msg: types.Message):
    await wallet.handle_balance(msg, bot)

@dp.message_handler(lambda m: m.text and m.text.strip() == "余额", chat_type=['private'])
async def balance_cmd_cn(msg: types.Message):
    await wallet.handle_balance(msg, bot)

@dp.message_handler(commands=["walletlog", "钱包日志"], chat_type=['private'])
async def walletlog_cmd(msg: types.Message):
    await wallet.handle_wallet_log(msg, bot)

@dp.message_handler(lambda m: m.text and m.text.strip() == "钱包日志", chat_type=['private'])
async def walletlog_cmd_cn(msg: types.Message):
    await wallet.handle_wallet_log(msg, bot)

@dp.message_handler(commands=["recharge", "充值"], chat_type=['private'])
async def recharge_cmd(msg: types.Message):
    await wallet.handle_recharge(msg, bot)

@dp.message_handler(lambda m: m.text and m.text.strip() == "充值", chat_type=['private'])
async def recharge_cmd_cn(msg: types.Message):
    await wallet.handle_recharge(msg, bot)

@dp.message_handler(commands=["withdraw", "提现"], chat_type=['private'])
async def withdraw_cmd(msg: types.Message):
    await wallet.handle_withdraw(msg, bot)

@dp.message_handler(lambda m: m.text and m.text.strip() == "提现", chat_type=['private'])
async def withdraw_cmd_cn(msg: types.Message):
    await wallet.handle_withdraw(msg, bot)

@dp.message_handler(commands=["rebatelog", "返利日志"], chat_type=['private'])
async def rebatelog_cmd(msg: types.Message):
    await rebate.handle_rebate_log(msg, bot)

@dp.message_handler(lambda m: m.text and m.text.strip() == "返利日志", chat_type=['private'])
async def rebatelog_cmd_cn(msg: types.Message):
    await rebate.handle_rebate_log(msg, bot)

@dp.message_handler(commands=["inviteinfo", "邀请信息"], chat_type=['private'])
async def inviteinfo_cmd(msg: types.Message):
    await rebate.handle_invite_info(msg, bot)

@dp.message_handler(lambda m: m.text and m.text.strip() == "邀请信息", chat_type=['private'])
async def inviteinfo_cmd_cn(msg: types.Message):
    await rebate.handle_invite_info(msg, bot)

# 防止其它私聊内容无响应
@dp.message_handler(chat_type=['private'])
async def private_only(msg: types.Message):
    await msg.reply("请在群组进行投注和开奖结果等操作，或使用菜单按钮。")

# ===== 群组功能：支持“大100”“小200”等中文下注（无/） =====
@dp.message_handler(Regexp(r"^(大|小|单|双)\d+$"), chat_type=['group', 'supergroup'])
async def chinese_bet(msg: types.Message):
    await game.handle_bet(msg, bot)

@dp.message_handler(lambda m: m.text and m.text.strip() in ["余额", "钱包日志", "充值", "提现", "返利日志", "邀请信息"], chat_type=['group', 'supergroup'])
async def group_cn_commands(msg: types.Message):
    await msg.reply("请私聊机器人使用此功能。")

@dp.message_handler(commands=["bet", "下注"], chat_type=['group', 'supergroup'])
async def bet_cmd(msg: types.Message):
    await game.handle_bet(msg, bot)

@dp.message_handler(commands=["history", "开奖历史"], chat_type=['group', 'supergroup'])
async def history_cmd(msg: types.Message):
    await game.handle_lottery_history(msg, bot)

@dp.message_handler(commands=["trend", "走势"], chat_type=['group', 'supergroup'])
async def trend_cmd(msg: types.Message):
    await game.handle_trend(msg, bot)

@dp.message_handler(commands=["rebatelog", "返利日志"], chat_type=['group', 'supergroup'])
async def rebatelog_cmd_group(msg: types.Message):
    await msg.reply("请私聊机器人获取返利日志。")

@dp.message_handler(commands=["inviteinfo", "邀请信息"], chat_type=['group', 'supergroup'])
async def inviteinfo_cmd_group(msg: types.Message):
    await msg.reply("请私聊机器人获取邀请信息。")

@dp.message_handler(commands=["kick", "踢人"], chat_type=['group', 'supergroup'])
async def kick_cmd(msg: types.Message):
    await group.handle_kick(msg, bot)

@dp.message_handler(commands=["mute", "禁言"], chat_type=['group', 'supergroup'])
async def mute_cmd(msg: types.Message):
    await group.handle_mute(msg, bot)

@dp.message_handler(commands=["blacklist", "拉黑"], chat_type=['group', 'supergroup'])
async def blacklist_cmd(msg: types.Message):
    await risk.handle_blacklist(msg, bot)

@dp.message_handler(commands=["whitelist", "白名单"], chat_type=['group', 'supergroup'])
async def whitelist_cmd(msg: types.Message):
    await risk.handle_whitelist(msg, bot)

@dp.message_handler(commands=["report", "报表"], chat_type=['group', 'supergroup'])
async def report_cmd(msg: types.Message):
    await admin.handle_report(msg, bot)

@dp.message_handler(chat_type=['group', 'supergroup'])
async def keyword_reply_hook(msg: types.Message):
    await group.handle_keyword_reply(msg, bot)

# ===== 每期45秒自动开奖/封盘/投掷骰子逻辑 =====
async def lottery_round():
    group_id = config.GROUP_ID  # 群组ID需在config中配置
    game.config_group_id(group_id)
    while True:
        await bot.send_message(group_id, "新一期开始，45秒后封盘，请下注…")
        await game.start_new_round()
        await asyncio.sleep(45)
        bets = await game.get_current_bets()
        if not bets:
            await bot.send_message(group_id, "本期封盘，未检测到下注，开始投掷三颗🎲")
            results = [await bot.send_dice(group_id) for _ in range(3)]
            values = [d.dice.value for d in results]
            await bot.send_message(group_id, f"开奖结果：{' '.join(str(v) for v in values)}")
            await game.settle_no_bet(values)
        else:
            await bot.send_message(group_id, "本期封盘，停止下注，请玩家在15秒内投掷三颗🎲")
            player_dice = await game.collect_player_dice(group_id, 15)
            while len(player_dice) < 3:
                dice = await bot.send_dice(group_id)
                player_dice.append(dice.dice.value)
            await bot.send_message(group_id, f"开奖结果：{' '.join(str(v) for v in player_dice)}")
            await game.settle_bets(player_dice)
        await asyncio.sleep(1)

async def main():
    init_db()
    asyncio.create_task(lottery_round())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
