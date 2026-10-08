# SQL Injection evaluation case 10
query = "SELECT * FROM products ORDER BY " + sort_key
cursor.execute(query)
