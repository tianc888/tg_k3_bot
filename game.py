import asyncio
import re
import random
import time
from aiogram import types

# ====== 全局收集骰子数据结构 ======
dice_collections = {}  # {group_id: {user_id: dice_value}}

# ====== 全局骰子消息处理器，只注册一次 ======
def register_dice_handler(dp):
    @dp.message_handler(content_types=types.ContentType.DICE, chat_type=['group', 'supergroup'])
    async def dice_handler(msg: types.Message):
        group_id = msg.chat.id
        user_id = msg.from_user.id
        dice_value = msg.dice.value
        # 只有在收集中才记录
        if group_id in dice_collections:
            if user_id not in dice_collections[group_id]:
                dice_collections[group_id][user_id] = dice_value

# ====== 在开奖流程中调用的收集函数 ======
async def collect_player_dice(group_id, seconds):
    """
    在 group_id 群组内，N 秒内收集每个玩家第一次掷的 🎲 点数。
    """
    dice_collections[group_id] = {}
    await asyncio.sleep(seconds)
    result = list(dice_collections[group_id].values())
    del dice_collections[group_id]
    return result

# ==============================
# 原有业务相关逻辑
# ==============================

class LotteryRound:
    def __init__(self):
        self.bets = []  # [(user_id, amount, username, bet_type)]
        self.player_dice = []  # [(user_id, value)]
        self.dice_time = []  # [(user_id, value, timestamp)]
        self.start_time = time.time()

    def add_bet(self, user_id, amount, username, bet_type=None):
        self.bets.append((user_id, amount, username, bet_type))

    def add_dice(self, user_id, value):
        self.player_dice.append((user_id, value))
        self.dice_time.append((user_id, value, time.time()))

    def get_bets(self):
        return self.bets

    def get_dice_values(self):
        return [v for _, v in self.player_dice]

    def get_user_dice_count(self, user_id):
        return len([u for u, v in self.player_dice if u == user_id])

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

# 支持“大100”“小200”“单300”“双400”格式，无需空格
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

    # 1. 支持中文格式：大100、小200、单300、双400
    bet_type, amount = parse_chinese_bet(text)
    # 2. 兼容 /bet 100 或 /下注 100
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
    # 无人下注，直接公布结果
    # 可扩展：记录历史、发送公告等
    # 这里只做占位
    pass

async def settle_bets(player_dice):
    # 有人下注，根据player_dice列表结算
    # 可扩展：中奖判定、分发奖励等
    # 这里只做占位
    pass

async def handle_lottery_history(msg: types.Message, bot):
    await msg.reply("历史开奖功能开发中…")

async def handle_trend(msg: types.Message, bot):
    await msg.reply("走势功能开发中…")
