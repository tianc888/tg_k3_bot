import asyncio
import re
import time
from aiogram import types
from utils import generate_period_code
from db import get_conn

dice_collections = {}

class LotteryRound:
    def __init__(self, period_code):
        self.period_code = period_code
        self.bets = []  # [(user_id, amount, username, bet_type)]
        self.bet_map = {}  # user_id: (username, amount, bet_type)
        self.player_dice = []
        self.dice_time = []
        self.start_time = time.time()
        self.is_closed = False

    def add_bet(self, user_id, amount, username, bet_type=None):
        self.bets.append((user_id, amount, username, bet_type))
        self.bet_map[user_id] = (username, amount, bet_type)

    def get_bets(self):
        return self.bets

    def get_bet_map(self):
        return self.bet_map

    def reset(self):
        self.bets = []
        self.bet_map = {}
        self.player_dice = []
        self.dice_time = []

current_round = None
GROUP_ID = None

def config_group_id(group_id):
    global GROUP_ID
    GROUP_ID = group_id

async def start_new_round():
    global current_round
    period_code = generate_period_code()
    current_round = LotteryRound(period_code)
    return period_code

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

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE tg_id=?", (msg.from_user.id,))
    row = cursor.fetchone()
    balance = row[0] if row else 0
    if balance <= 0:
        await msg.reply("余额不足！")
        conn.close()
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

    if not current_round or getattr(current_round, "is_closed", False):
        await msg.reply("投注无效，本期已封盘")
        return

    if amount > balance:
        await msg.reply("余额不足！")
        conn.close()
        return

    cursor.execute("UPDATE users SET balance=balance-? WHERE tg_id=?", (amount, user_id))
    conn.commit()
    conn.close()

    current_round.add_bet(user_id, amount, username, bet_type)
    await msg.reply(f"{username} {user_id} {bet_type}{amount} 已成功下注！")

async def collect_player_dice(group_id, seconds):
    dice_collections[group_id] = {}
    await asyncio.sleep(seconds)
    result = list(dice_collections[group_id].values())
    del dice_collections[group_id]
    return result

def register_dice_handler(dp):
    @dp.message_handler(content_types=types.ContentType.DICE, chat_type=['group', 'supergroup'])
    async def dice_handler(msg: types.Message):
        group_id = msg.chat.id
        user_id = msg.from_user.id
        dice_value = msg.dice.value
        if group_id in dice_collections:
            if user_id not in dice_collections[group_id]:
                dice_collections[group_id][user_id] = dice_value

async def settle_no_bet(values):
    pass

async def settle_bets(player_dice):
    pass

async def handle_lottery_history(msg: types.Message, bot):
    await msg.reply("历史开奖功能开发中…")

async def handle_trend(msg: types.Message, bot):
    await msg.reply("走势功能开发中…")
