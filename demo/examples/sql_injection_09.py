# SQL Injection evaluation case 9
query = "UPDATE accounts SET role = 'user' WHERE id = %s" % account_id
cursor.execute(query)
