from db import get_conn

def set_user_setting(user_id, key, value):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO user_settings (user_id, setting_key, setting_value) VALUES (?, ?, ?)", (user_id, key, value))
    conn.commit()
    conn.close()

def get_user_setting(user_id, key):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT setting_value FROM user_settings WHERE user_id=? AND setting_key=?", (user_id, key))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
