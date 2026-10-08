import sqlite3


def get_user(db_path, username):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, email FROM users WHERE name = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row
