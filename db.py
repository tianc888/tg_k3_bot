import sqlite3

def get_conn():
    return sqlite3.connect("k3bot.db")

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    # 用户表
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        username TEXT,
        invite_code TEXT,
        inviter INTEGER,
        level INTEGER DEFAULT 0,
        balance REAL DEFAULT 0,
        password TEXT,
        telegram_bound INTEGER DEFAULT 0,
        agent_code TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 订单表
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game_type TEXT,
        bet_content TEXT,
        period TEXT,
        amount REAL,
        status TEXT,
        win_amount REAL,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 钱包流水
    cursor.execute('''CREATE TABLE IF NOT EXISTS wallet_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        change REAL,
        type TEXT,
        reason TEXT,
        status TEXT DEFAULT '成功',
        txid TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 黑名单
    cursor.execute('''CREATE TABLE IF NOT EXISTS blacklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        reason TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 白名单
    cursor.execute('''CREATE TABLE IF NOT EXISTS whitelist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 管理员表
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE
    )''')
    # 群组表
    cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER UNIQUE,
        group_name TEXT,
        admin_id INTEGER,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 机器人参数
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
        name TEXT PRIMARY KEY,
        value TEXT
    )''')
    # 开奖历史
    cursor.execute('''CREATE TABLE IF NOT EXISTS lottery_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period TEXT UNIQUE,
        numbers TEXT,
        result_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 追号表
    cursor.execute('''CREATE TABLE IF NOT EXISTS chase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        bet_content TEXT,
        game_type TEXT,
        period_start TEXT,
        period_count INTEGER,
        finished_count INTEGER DEFAULT 0,
        stop_win REAL DEFAULT 0,
        stop_loss REAL DEFAULT 0,
        active INTEGER DEFAULT 1,
        win_sum REAL DEFAULT 0,
        loss_sum REAL DEFAULT 0,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 代理返佣记录
    cursor.execute('''CREATE TABLE IF NOT EXISTS rebate_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        from_user_id INTEGER,
        order_id INTEGER,
        amount REAL,
        level INTEGER,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 充值/提现申请表
    cursor.execute('''CREATE TABLE IF NOT EXISTS transfer_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        amount REAL,
        method TEXT,
        status TEXT DEFAULT '待审核',
        account TEXT,
        proof TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 关键词自动回复
    cursor.execute('''CREATE TABLE IF NOT EXISTS auto_reply (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        reply TEXT
    )''')
    # 风控日志
    cursor.execute('''CREATE TABLE IF NOT EXISTS risk_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event TEXT,
        detail TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # 用户个性化设置
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        setting_key TEXT,
        setting_value TEXT,
        UNIQUE(user_id, setting_key)
    )''')
    # 公告/活动表
    cursor.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
