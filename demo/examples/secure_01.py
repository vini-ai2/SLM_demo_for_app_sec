# Secure/negative evaluation case 1
cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
