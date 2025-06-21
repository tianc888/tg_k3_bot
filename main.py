from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
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

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await user.handle_start(msg, bot)

@dp.message(Command("register"))
async def register_cmd(msg: types.Message):
    await user.handle_register(msg, bot)

@dp.message(Command("balance"))
async def balance_cmd(msg: types.Message):
    await wallet.handle_balance(msg, bot)

@dp.message(Command("walletlog"))
async def walletlog_cmd(msg: types.Message):
    await wallet.handle_wallet_log(msg, bot)

@dp.message(Command("recharge"))
async def recharge_cmd(msg: types.Message):
    await wallet.handle_recharge(msg, bot)

@dp.message(Command("withdraw"))
async def withdraw_cmd(msg: types.Message):
    await wallet.handle_withdraw(msg, bot)

@dp.message(Command("review"))
async def review_cmd(msg: types.Message):
    await wallet.handle_transfer_review(msg, bot)

@dp.message(Command("bet"))
async def bet_cmd(msg: types.Message):
    await game.handle_bet(msg, bot)

@dp.message(Command("chase"))
async def chase_cmd(msg: types.Message):
    await game.handle_chase(msg, bot)

@dp.message(Command("chase_list"))
async def chase_list_cmd(msg: types.Message):
    await game.handle_chase_list(msg, bot)

@dp.message(Command("history"))
async def history_cmd(msg: types.Message):
    await game.handle_lottery_history(msg, bot)

@dp.message(Command("trend"))
async def trend_cmd(msg: types.Message):
    await game.handle_trend(msg, bot)

@dp.message(Command("rebatelog"))
async def rebatelog_cmd(msg: types.Message):
    await rebate.handle_rebate_log(msg, bot)

@dp.message(Command("inviteinfo"))
async def inviteinfo_cmd(msg: types.Message):
    await rebate.handle_invite_info(msg, bot)

@dp.message(Command("kick"))
async def kick_cmd(msg: types.Message):
    await group.handle_kick(msg, bot)

@dp.message(Command("mute"))
async def mute_cmd(msg: types.Message):
    await group.handle_mute(msg, bot)

@dp.message(Command("setparam"))
async def setparam_cmd(msg: types.Message):
    await group.handle_set_param(msg, bot)

@dp.message(Command("addkw"))
async def addkw_cmd(msg: types.Message):
    await group.handle_add_keyword(msg, bot)

@dp.message(Command("blacklist"))
async def blacklist_cmd(msg: types.Message):
    await risk.handle_blacklist(msg, bot)

@dp.message(Command("whitelist"))
async def whitelist_cmd(msg: types.Message):
    await risk.handle_whitelist(msg, bot)

@dp.message(Command("risklog"))
async def risklog_cmd(msg: types.Message):
    await risk.handle_risklogs(msg, bot)

@dp.message(Command("setnotify"))
async def setnotify_cmd(msg: types.Message):
    await user_settings.handle_set_notify(msg, bot)

@dp.message(Command("setlang"))
async def setlang_cmd(msg: types.Message):
    await user_settings.handle_set_lang(msg, bot)

@dp.message(Command("report"))
async def report_cmd(msg: types.Message):
    await admin.handle_report(msg, bot)

@dp.message(Command("userlist"))
async def userlist_cmd(msg: types.Message):
    await admin.handle_userlist(msg, bot)

@dp.message(Command("orderlist"))
async def orderlist_cmd(msg: types.Message):
    await admin.handle_orderlist(msg, bot)

@dp.message(Command("agentlist"))
async def agentlist_cmd(msg: types.Message):
    await admin.handle_agentlist(msg, bot)

@dp.message(Command("announce"))
async def announce_cmd(msg: types.Message):
    await admin.handle_announce(msg, bot)

@dp.message(Command("backup"))
async def backup_cmd(msg: types.Message):
    await admin.handle_backup(msg, bot)

@dp.message(Command("restore"))
async def restore_cmd(msg: types.Message):
    await admin.handle_restore(msg, bot)

@dp.message()
async def keyword_reply_hook(msg: types.Message):
    await group.handle_keyword_reply(msg, bot)

async def main():
    init_db()
    asyncio.create_task(game.auto_lottery_task(bot))
    asyncio.create_task(game.chase_auto_bet(bot))
    asyncio.create_task(game.settle_orders_and_payout(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
