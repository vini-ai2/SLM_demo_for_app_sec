# SQL Injection evaluation case 15
query = "SELECT * FROM products ORDER BY " + sort_key
cursor.execute(query)
