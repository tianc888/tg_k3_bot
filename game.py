import random
import datetime
import re

class LotteryRound:
    def __init__(self, period_code, group_id, close_time):
        self.period_code = period_code
        self.group_id = group_id
        self.bets = []  # [(uid, amount, username, bet_type)]
        self.dice = []
        self.is_closed = False
        self.close_time = close_time

    def add_bet(self, user_id, amount, username, bet_type):
        self.bets.append((user_id, amount, username, bet_type))
        return True

    def get_bets(self):
        return self.bets

    def get_bet_users(self):
        return [b[0] for b in self.bets]

    def get_bets_by_user(self, user_id):
        return [b for b in self.bets if b[0] == user_id]

    def remove_bets_by_user(self, user_id):
        original_len = len(self.bets)
        self.bets = [b for b in self.bets if b[0] != user_id]
        return original_len != len(self.bets)

    def clear(self):
        self.bets = []
        self.dice = []
        self.is_closed = False

class GameManager:
    def __init__(self):
        self.current_round = None
        self.group_id = None
        self.last_period_code = None

    def config_group_id(self, group_id):
        self.group_id = group_id

    async def start_new_round(self):
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        date_part = now.strftime("%m%d")
        rand_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
        period_code = f"{date_part}{rand_part}"
        close_time = now + datetime.timedelta(seconds=45)
        self.current_round = LotteryRound(period_code, self.group_id, close_time)
        self.last_period_code = period_code
        return period_code

    async def handle_bet(self, msg, bot):
        if msg.chat.type not in ['group', 'supergroup']:
            return
        text = msg.text.strip()

        # 新下注格式解析
        bet_parsed = self.parse_bet_message(text)
        if not bet_parsed:
            await msg.reply(
                "下注格式有误，支持：\n"
                "大100、小200、单50、双100、\n"
                "大单100（组合）、豹子、顺子100、\n"
                "1b100（指定豹子，1~6b数字，100为金额）\n"
                "如需取消本期下注请输入：取消 或 取消下注"
            )
            return
        bet_type, amount = bet_parsed

        if not self.current_round or self.current_round.is_closed:
            await msg.reply("投注无效，本期已封盘")
            return

        from wallet import get_user_balance, change_user_balance, remember_username
        balance = get_user_balance(msg.from_user.id)
        if balance < amount:
            await msg.reply("余额不足，请先充值")
            return

        # 记住玩家username映射，方便管理员@加余额
        remember_username(msg.from_user.id, msg.from_user.username)
        change_user_balance(msg.from_user.id, -amount, "下注", f"{self.current_round.period_code} {bet_type}{amount}")
        username = msg.from_user.full_name
        self.current_round.add_bet(msg.from_user.id, amount, username, bet_type)
        await msg.reply(f"下注成功！本期[{self.current_round.period_code}] 你的投注：{bet_type}{amount}")

    def parse_bet_message(self, text):
        text = text.replace(" ", "")

        # 1. 指定豹子（如1b100、2b50等，1~6b+金额）
        m = re.fullmatch(r"([1-6])b(\d+)", text)
        if m:
            baozi_num = m.group(1)
            amount = int(m.group(2))
            return (f"{baozi_num}b", amount)

        # 2. 组合，如大单100、小双200等
        m = re.fullmatch(r"(大单|大小|大双|小单|小双)(\d+)", text)
        if m:
            combo = m.group(1)
            amount = int(m.group(2))
            return (f"组合{combo}", amount)

        # 3. 基本大小单双
        for k in ["大", "小", "单", "双"]:
            if text.startswith(k):
                try:
                    amount = int(text[len(k):])
                    return (k, amount)
                except:
                    return None

        # 4. 豹子/豹子100
        if text.startswith("豹子"):
            left = text[2:]
            if left == "":
                amount = 10  # 默认
            else:
                try:
                    amount = int(left)
                except:
                    return None
            return ("豹子", amount)

        # 5. 顺子100
        m = re.fullmatch(r"顺子(\d+)", text)
        if m:
            amount = int(m.group(1))
            return ("顺子", amount)

        return None

    async def handle_cancel(self, msg, bot):
        if not self.current_round or self.current_round.is_closed:
            await msg.reply("本期已封盘，无法取消下注")
            return
        bets = self.current_round.get_bets_by_user(msg.from_user.id)
        if not bets:
            await msg.reply("你本期没有下注，无需取消")
            return
        from wallet import change_user_balance
        total_refund = sum([b[1] for b in bets])
        for b in bets:
            change_user_balance(msg.from_user.id, b[1], "取消下注", f"{self.current_round.period_code} {b[2]}{b[1]}")
        self.current_round.remove_bets_by_user(msg.from_user.id)
        await msg.reply(f"已取消本期所有下注并返还{total_refund}余额。")

    def _is_baozi(self, vals):
        return vals[0] == vals[1] == vals[2]

    def _is_shunzi(self, vals):
        # 顺子：任意3个连续点数，无需正顺或倒顺
        s = sorted(vals)
        return s[0]+1 == s[1] and s[1]+1 == s[2]

    async def settle_bets(self, dice_values):
        from wallet import change_user_balance
        total = sum(dice_values)
        bet_result = []
        vals = dice_values
        big = total >= 11
        odd = total % 2 == 1
        baozi = self._is_baozi(vals)
        shunzi = self._is_shunzi(vals)
        baozi_num = str(vals[0])
        for uid, amount, username, bet_type in self.current_round.get_bets():
            win = False
            win_amt = 0
            # 大小单双（豹子不算中奖）
            if bet_type == '大' and big and not baozi:
                win = True
                win_amt = amount * 2
            elif bet_type == '小' and not big and not baozi:
                win = True
                win_amt = amount * 2
            elif bet_type == '单' and odd and not baozi:
                win = True
                win_amt = amount * 2
            elif bet_type == '双' and not odd and not baozi:
                win = True
                win_amt = amount * 2
            # 组合型
            elif bet_type.startswith("组合"):
                combo = bet_type[2:]
                c1, c2 = combo[:1], combo[1:]
                if ((c1 == "大" and big) or (c1 == "小" and not big)) and \
                   ((c2 == "单" and odd) or (c2 == "双" and not odd)) and not baozi:
                    win = True
                    win_amt = amount * 4
            # 豹子
            elif bet_type == "豹子" and baozi:
                win = True
                win_amt = amount * 10
            # 指定豹子，如 1b
            elif len(bet_type) == 2 and bet_type.endswith("b") and baozi:
                num = bet_type[0]
                if baozi_num == num:
                    win = True
                    win_amt = amount * 50
            # 顺子（只要是顺子即可，无需指定顺子点数）
            elif bet_type == "顺子" and shunzi:
                win = True
                win_amt = amount * 8
            if win:
                change_user_balance(uid, win_amt, "中奖", f"{self.current_round.period_code} {bet_type}{amount}")
                bet_result.append(f"{username} {bet_type}{amount} 中奖+{win_amt}")
            else:
                bet_result.append(f"{username} {bet_type}{amount} 未中奖")
        self.current_round.clear()
        return bet_result

    async def settle_no_bet(self, dice_values):
        self.current_round.clear()
        return

# 全局实例
game = GameManager()

def register_dice_handler(dp):
    from aiogram import types
    @dp.message_handler(lambda m: getattr(m, "dice", None) and m.chat.type in ['group', 'supergroup'])
    async def dice_handler(msg: types.Message):
        global game
        # 确保 current_round、is_closed、group_id 合法
        if not hasattr(game, "current_round") or not game.current_round or not game.current_round.is_closed:
            return
        if msg.chat.id != game.group_id:
            return
        if len(game.current_round.dice) < 3:
            game.current_round.dice.append(msg.dice.value)
