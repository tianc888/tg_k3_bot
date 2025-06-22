# Telegram Bot Token
BOT_TOKEN = "7303119673:AAGAgKHWs760UdtDlVPHIhypYYkiBi_791w"  # 请换成你的BotToken

# 管理员Telegram用户ID列表
ADMINS = [8166234652]

# 数据库路径
DATABASE = "k3bot.db"

# 群组ID
GROUP_ID = -1002874860074  # 修改为你的群组ID

# 支付接口（占位）
USDT_API = ""
ALIPAY_API = ""
WECHAT_API = ""
BANK_API = ""

# 代理返佣比例
REBATE_LEVELS = [0.1, 0.05, 0.02]

# 多语言提示
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

# 业务相关配置
MIN_BET_AMOUNT = 10
MAX_BET_AMOUNT = 10000

# 支付/提现方式
RECHARGE_METHODS = ["支付宝", "微信", "银行卡"]
WITHDRAW_METHODS = ["银行卡"]

# 彩票/开奖相关
LOTTERY_ROUND_SECONDS = 45
PLAYER_DICE_SECONDS = 15
DICE_PER_ROUND = 3
