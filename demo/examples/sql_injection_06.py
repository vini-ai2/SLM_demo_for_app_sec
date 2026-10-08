# SQL Injection evaluation case 6
query = "SELECT * FROM users WHERE name = '" + value + "'"
cursor.execute(query)
