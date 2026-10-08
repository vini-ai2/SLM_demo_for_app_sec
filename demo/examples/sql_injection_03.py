# SQL Injection evaluation case 3
cursor.execute("DELETE FROM sessions WHERE token = '" + token + "'")

