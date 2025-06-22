import threading

_user_balances = {}
_usernames = {}  # username -> uid
_bal_lock = threading.Lock()

def get_user_balance(uid):
    with _bal_lock:
        return _user_balances.get(uid, 1000) # 初始余额1000

def change_user_balance(uid, amount, reason, detail):
    with _bal_lock:
        bal = _user_balances.get(uid, 1000)
        bal += amount
        _user_balances[uid] = bal

def set_user_balance(uid, value):
    with _bal_lock:
        _user_balances[uid] = value

def remember_username(uid, username):
    if username:
        with _bal_lock:
            _usernames[username.lstrip("@")] = uid

def get_uid_by_username(username):
    with _bal_lock:
        return _usernames.get(username.lstrip("@"))

async def handle_balance(msg, bot):
    remember_username(msg.from_user.id, msg.from_user.username)
    bal = get_user_balance(msg.from_user.id)
    await msg.reply(f"您的余额为：{bal}")

async def handle_wallet_log(msg, bot):
    await msg.reply("钱包日志功能暂未实现。")

async def handle_recharge(msg, bot):
    await msg.reply("充值功能暂未实现，请联系管理员。")

async def handle_withdraw(msg, bot):
    await msg.reply("提现功能暂未实现，请联系管理员。")
