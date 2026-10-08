# SQL Injection evaluation case 4
query = "UPDATE accounts SET role = 'user' WHERE id = %s" % account_id
cursor.execute(query)
