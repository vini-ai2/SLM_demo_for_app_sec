# SQL Injection evaluation case 8
cursor.execute("DELETE FROM sessions WHERE token = '" + token + "'")

