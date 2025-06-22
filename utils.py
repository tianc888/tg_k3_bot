import random
import string
import config

def generate_period_code():
    nums = ''.join(random.choices('0123456789', k=3))
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{nums}{letters}"

def get_admin_link():
    admin = config.ADMINS[0]
    if isinstance(admin, str) and admin.startswith("t.me/"):
        return admin
    if isinstance(admin, int) or (isinstance(admin, str) and admin.isdigit()):
        return f"https://t.me/user?id={admin}"
    return f"https://t.me/{admin}"

def get_bot_link():
    return f"https://t.me/{config.BOT_USERNAME}"
