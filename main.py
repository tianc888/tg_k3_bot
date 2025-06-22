from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command, Regexp
import asyncio
import config
from db import init_db
import game, wallet, group, risk, rebate, admin
from utils import generate_period_code, get_admin_link, get_bot_link

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
game.register_dice_handler(dp)

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

# ...（省略私聊/群聊handler，参见前面适配）

async def lottery_round():
    group_id = config.GROUP_ID
    game.config_group_id(group_id)
    while True:
        period_code = await game.start_new_round()
        # 开盘前2秒发按钮
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("联系客服", url=get_admin_link()),
            InlineKeyboardButton("充值/提现", url=get_bot_link()),
        )
        await bot.send_message(group_id, f"--YLttK3第{period_code}期", reply_markup=markup)
        await asyncio.sleep(0.5)
        # 开盘提示
        await bot.send_message(group_id, f"--YLttK3第{period_code}期\n\n--本期已开盘，玩家请开始下注")
        await asyncio.sleep(43)
        # 封盘，处理下注
        if game.current_round and game.current_round.get_bets():
            betlines = "\n".join(
                f"{u} {uid} {bt or ''}{amt}"
                for uid, amt, u, bt in game.current_round.get_bets()
            )
            await bot.send_message(
                group_id,
                f"--YLttK3第{period_code}期\n\n{betlines}\n--本期已封盘，请停止下注\n--轻触【🎲】复制投掷\n请在15秒内掷出3颗骰子，超时系统自动补发，无任何争议"
            )
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
            await bot.send_message(
                group_id,
                f"--YLttK3第{period_code}期\n\n--本期封盘，没有玩家下注，系统自动投掷骰子"
            )
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
