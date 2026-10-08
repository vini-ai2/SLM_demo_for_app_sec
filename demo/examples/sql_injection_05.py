# SQL Injection evaluation case 5
query = "SELECT * FROM products ORDER BY " + sort_key
cursor.execute(query)
