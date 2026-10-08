# SQL Injection evaluation case 2
query = f"SELECT * FROM orders WHERE id = {value}"
cursor.execute(query)
