# SQL Injection evaluation case 7
query = f"SELECT * FROM orders WHERE id = {value}"
cursor.execute(query)
