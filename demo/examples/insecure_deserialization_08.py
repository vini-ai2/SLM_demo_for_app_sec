# Insecure Deserialization evaluation case 8
session = pickle.loads(base64.b64decode(cookie))

