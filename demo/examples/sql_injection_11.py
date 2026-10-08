# SQL Injection evaluation case 11
query = "SELECT * FROM users WHERE name = '" + value + "'"
cursor.execute(query)
