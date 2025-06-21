BOT_TOKEN = "7303119673:AAGAgKHWs760UdtDlVPHIhypYYkiBi_791w"  # 替换为你自己的Bot Token
ADMINS = [8166234652]  # 管理员Telegram用户ID列表（可填多个）
DATABASE = "k3bot.db"

# 支付接口占位（后面扩展）
USDT_API = ""
ALIPAY_API = ""
WECHAT_API = ""
BANK_API = ""

# 代理返佣比例（百分比）
REBATE_LEVELS = [0.1, 0.05, 0.02]  # 1级10%，2级5%，3级2%

LANGUAGES = {
    "zh": {
        "welcome": "欢迎使用机器人！",
        "balance": "您的余额为：{balance} 元"
    },
    "en": {
        "welcome": "Welcome to the bot!",
        "balance": "Your balance is: {balance}"
    }
}
