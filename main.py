from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command, Regexp
import asyncio
import config
from db import init_db
import game, wallet, group, risk, rebate, admin

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
game.register_dice_handler(dp)

# 私聊菜单
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

# 内联按钮
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

# 私聊余额等功能
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

# 群聊下注（正则匹配中文格式下注）
@dp.message_handler(Regexp(r"^(大|小|单|双)\d+$"))
async def chinese_bet(msg: types.Message):
    if msg.chat.type not in ['group', 'supergroup']:
        return
    await game.handle_bet(msg, bot)

@dp.message_handler(commands=["bet", "下注"])
async def bet_cmd(msg: types.Message):
    if msg.chat.type not in ['group', 'supergroup']:
        return
    await game.handle_bet(msg, bot)

# 管理员命令
@dp.message_handler(commands=["report", "报表"])
async def report_cmd(msg: types.Message):
    await admin.handle_report(msg, bot)

# 其它群管命令
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

# 群聊关键词自动回复
@dp.message_handler(lambda msg: msg.chat.type in ['group', 'supergroup'])
async def keyword_reply_hook(msg: types.Message):
    await group.handle_keyword_reply(msg, bot)

# 启动
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
