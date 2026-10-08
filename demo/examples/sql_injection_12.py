# SQL Injection evaluation case 12
query = f"SELECT * FROM orders WHERE id = {value}"
cursor.execute(query)
