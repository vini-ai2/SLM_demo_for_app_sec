import sqlite3


def get_user(db_path, username):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = "SELECT id, email FROM users WHERE name = '" + username + "'"
    cur.execute(query)
    row = cur.fetchone()
    conn.close()
    return row
