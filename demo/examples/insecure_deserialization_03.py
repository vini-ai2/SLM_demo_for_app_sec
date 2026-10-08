# Insecure Deserialization evaluation case 3
session = pickle.loads(base64.b64decode(cookie))

