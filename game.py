import asyncio
import re
import time
from aiogram import types

dice_collections = {}

def register_dice_handler(dp):
    @dp.message_handler(content_types=types.ContentType.DICE, chat_type=['group', 'supergroup'])
    async def dice_handler(msg: types.Message):
        group_id = msg.chat.id
        user_id = msg.from_user.id
        dice_value = msg.dice.value
        if group_id in dice_collections:
            if user_id not in dice_collections[group_id]:
                dice_collections[group_id][user_id] = dice_value

async def collect_player_dice(group_id, seconds):
    dice_collections[group_id] = {}
    await asyncio.sleep(seconds)
    result = list(dice_collections[group_id].values())
    del dice_collections[group_id]
    return result

class LotteryRound:
    def __init__(self):
        self.bets = []
        self.player_dice = []
        self.dice_time = []
        self.start_time = time.time()
    def add_bet(self, user_id, amount, username, bet_type=None):
        self.bets.append((user_id, amount, username, bet_type))
    def get_bets(self):
        return self.bets
    def reset(self):
        self.bets = []
        self.player_dice = []
        self.dice_time = []

current_round = None
GROUP_ID = None

def config_group_id(group_id):
    global GROUP_ID
    GROUP_ID = group_id

async def start_new_round():
    global current_round
    current_round = LotteryRound()

def has_bet():
    return bool(current_round and current_round.get_bets())

async def get_current_bets():
    return current_round.get_bets() if current_round else []

def parse_chinese_bet(text):
    pattern = re.compile(r'^(大|小|单|双)(\d+)$')
    match = pattern.match(text)
    if match:
        bet_type = match.group(1)
        amount = int(match.group(2))
        return bet_type, amount
    return None, None

async def handle_bet(msg: types.Message, bot):
    if msg.chat.type not in ['group', 'supergroup']:
        await msg.reply("请在群组内下注。")
        return
    text = msg.text.strip()
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name
    bet_type, amount = parse_chinese_bet(text)
    if bet_type is None:
        try:
            args = msg.get_args()
            amount = int(args)
            bet_type = ""
        except Exception:
            await msg.reply("请输入正确的下注格式，例如 大100、小200，或 /下注 100")
            return
    if not current_round:
        await msg.reply("当前没有开奖期，请等待新一期开始。")
        return
    current_round.add_bet(user_id, amount, username, bet_type)
    await msg.reply(f"{username} 成功下注{bet_type or ''} {amount}！")

async def settle_no_bet(values):
    pass

async def settle_bets(player_dice):
    pass

async def handle_lottery_history(msg: types.Message, bot):
    await msg.reply("历史开奖功能开发中…")

async def handle_trend(msg: types.Message, bot):
    await msg.reply("走势功能开发中…")
