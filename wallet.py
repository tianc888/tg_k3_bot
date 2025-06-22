import threading

# 线程安全的简单钱包实现（如用数据库请替换）
_user_balances = {}
_bal_lock = threading.Lock()

def get_user_balance(uid):
    with _bal_lock:
        return _user_balances.get(uid, 1000) # 初始余额1000

def change_user_balance(uid, amount, reason, detail):
    with _bal_lock:
        bal = _user_balances.get(uid, 1000)
        bal += amount
        _user_balances[uid] = bal
        # 这里可添加日志或记录 reason/detail

def set_user_balance(uid, value):
    with _bal_lock:
        _user_balances[uid] = value
