# Telegram Bot Token
BOT_TOKEN = "7303119673:AAGAgKHWs760UdtDlVPHIhypYYkiBi_791w"  # 替换为你自己的Bot Token

# 管理员Telegram用户ID列表（可填多个）
ADMINS = [8166234652]

# 数据库路径
DATABASE = "k3bot.db"

# 群组ID（负号开头，必须为int类型，务必替换为你的目标群组ID）
GROUP_ID = -1002874860074  # TODO: 替换为你的群组ID

# 支付接口占位（后面扩展）
USDT_API = ""
ALIPAY_API = ""
WECHAT_API = ""
BANK_API = ""

# 代理返佣比例（百分比）
REBATE_LEVELS = [0.1, 0.05, 0.02]  # 1级10%，2级5%，3级2%

# 多语言提示文本
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
MIN_BET_AMOUNT = 10        # 最小下注金额
MAX_BET_AMOUNT = 10000     # 最大下注金额

# 支付/提现方式
RECHARGE_METHODS = ["支付宝", "微信", "银行卡"]
WITHDRAW_METHODS = ["银行卡"]

# 彩票/开奖相关
LOTTERY_ROUND_SECONDS = 45     # 每期时长（秒）
PLAYER_DICE_SECONDS = 15       # 玩家掷骰时间（秒）
DICE_PER_ROUND = 3             # 每期投掷骰子数

# 语言/本地化配置
DEFAULT_LANG = "zh"

# 其它可扩展配置项
# ...
