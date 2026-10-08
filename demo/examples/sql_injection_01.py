# SQL Injection evaluation case 1
query = "SELECT * FROM users WHERE name = '" + value + "'"
cursor.execute(query)
