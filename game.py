import asyncio
from aiogram import types
from collections import defaultdict
import random
import time

# 用于保存每期下注信息、玩家掷骰信息
class LotteryRound:
    def __init__(self):
        self.bets = []  # [(user_id, amount, username)]
        self.player_dice = []  # [(user_id, value)]
        self.dice_time = []  # [(user_id, value, timestamp)]
        self.start_time = time.time()

    def add_bet(self, user_id, amount, username):
        self.bets.append((user_id, amount, username))

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

# 全局当前开奖期
current_round = None

# 群组ID需与config.py保持一致
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

async def handle_bet(msg: types.Message, bot):
    if msg.chat.type not in ['group', 'supergroup']:
        await msg.reply("请在群组内下注。")
        return
    # 示例：用户命令 /下注 100
    try:
        args = msg.get_args()
        amount = int(args)
    except Exception:
        await msg.reply("请输入正确的下注金额，例如 /下注 100")
        return
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name
    if not current_round:
        await msg.reply("当前没有开奖期，请等待新一期开始。")
        return
    current_round.add_bet(user_id, amount, username)
    await msg.reply(f"{username} 成功下注 {amount}！")

async def collect_player_dice(group_id, seconds):
    """
    收集群组内15秒内玩家掷的🎲，只统计第一次骰子点数
    """
    collected = []

    # 用于监听aiogram全局事件
    from aiogram import Dispatcher

    dp = Dispatcher.get_current()

    # 存储玩家id和点数
    user_dice = {}

    # 定义处理骰子的方法
    async def dice_handler(msg: types.Message):
        if msg.chat.id != group_id:
            return
        # 只统计🎲
        if msg.dice and msg.dice.emoji == '🎲':
            user_id = msg.from_user.id
            # 只记录第一次
            if user_id not in user_dice:
                user_dice[user_id] = msg.dice.value

    # 注册临时handler
    dp.register_message_handler(dice_handler, content_types=types.ContentType.DICE)

    await asyncio.sleep(seconds)

    # 收集结果
    collected = list(user_dice.values())

    # 移除handler
    dp.unregister_message_handler(dice_handler, content_types=types.ContentType.DICE)

    return collected

async def settle_no_bet(values):
    # 无人下注，直接公布结果
    # 可扩展：记录历史、发送公告等
    pass

async def settle_bets(player_dice):
    # 有人下注，根据player_dice列表结算
    # 可扩展：中奖判定、分发奖励等
    pass

async def handle_lottery_history(msg: types.Message, bot):
    await msg.reply("历史开奖功能开发中…")

async def handle_trend(msg: types.Message, bot):
    await msg.reply("走势功能开发中…")
