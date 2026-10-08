# Server-Side Request Forgery (SSRF) evaluation case 10
response = requests.get("http://" + host + "/status")

