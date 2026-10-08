# Server-Side Request Forgery (SSRF) evaluation case 5
response = requests.get("http://" + host + "/status")

