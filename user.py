from db import get_conn

def get_or_create_user(tg_id, username=None):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE tg_id=?", (tg_id,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row[0]
    cursor.execute("INSERT INTO users (tg_id, username) VALUES (?, ?)", (tg_id, username or ""))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def update_username(tg_id, username):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username=? WHERE tg_id=?", (username, tg_id))
    conn.commit()
    conn.close()
