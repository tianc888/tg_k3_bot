import sqlite3

def get_conn():
    return sqlite3.connect('k3bot.db')

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS rebates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        level INTEGER,
        from_user TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS blacklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        reason TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS whitelist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER UNIQUE,
        group_name TEXT,
        admin_id INTEGER,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
        name TEXT PRIMARY KEY,
        value TEXT
    )''')
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS auto_reply (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        reply TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS risk_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event TEXT,
        detail TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        setting_key TEXT,
        setting_value TEXT
    )''')
    conn.commit()
    conn.close()
