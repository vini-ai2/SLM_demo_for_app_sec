# SQL Injection evaluation case 13
cursor.execute("DELETE FROM sessions WHERE token = '" + token + "'")

