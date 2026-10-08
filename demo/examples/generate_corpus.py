"""Generate the fixed, labeled 130-example evaluation corpus."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Each case is a distinct unsafe/safe sink pattern. The source is intentionally
# small so models can focus on the security decision rather than project context.
CASES = {
    "sql_injection": ("SQL Injection", "CWE-89", [
        ('query = "SELECT * FROM users WHERE name = \'" + value + "\'"', "cursor.execute(query)", "parameterized query"),
        ('query = f"SELECT * FROM orders WHERE id = {value}"', "cursor.execute(query)", "parameterized query"),
        ('cursor.execute("DELETE FROM sessions WHERE token = \'" + token + "\'")', "cursor.execute", "parameterized query"),
        ('query = "UPDATE accounts SET role = \'user\' WHERE id = %s" % account_id', "cursor.execute(query)", "parameterized query"),
        ('query = "SELECT * FROM products ORDER BY " + sort_key', "cursor.execute(query)", "allowlist"),
    ]),
    "command_injection": ("Command Injection", "CWE-78", [
        ('command = "ping -c 1 " + host', 'subprocess.run(command, shell=True)', "shell=False"),
        ('os.system("convert " + filename + " output.png")', "os.system", "subprocess"),
        ('subprocess.Popen("grep " + term + " data.txt", shell=True)', "shell=True", "shell=False"),
        ('command = f"tar -xf {archive}"', 'subprocess.call(command, shell=True)', "shell=False"),
        ('subprocess.run(["sh", "-c", "echo " + message])', '"sh", "-c"', "argument list"),
    ]),
    "path_traversal": ("Path Traversal", "CWE-22", [
        ('path = os.path.join(ROOT, filename)', "open(path", "commonpath"),
        ('with open(BASE / user_path) as stream:', "BASE / user_path", "resolve"),
        ('target = os.path.join(DOWNLOADS, name)', "open(target", "commonpath"),
        ('path = ROOT + "/" + requested', 'open(path, "rb")', "resolve"),
        ('shutil.copyfile(os.path.join(TMP, upload), destination)', "os.path.join(TMP, upload)", "basename"),
    ]),
    "xss": ("Cross-Site Scripting (XSS)", "CWE-79", [
        ('return "<h1>" + username + "</h1>"', "username", "escape"),
        ('return f"<p>{comment}</p>"', "comment", "escape"),
        ('return "<div data-name=\'" + name + "\'></div>"', "data-name", "escape"),
        ('return "<script>show(\\\"" + value + "\\\")</script>"', "<script>", "json"),
        ('return f"<a href=\'{url}\'>open</a>"', "href", "validate"),
    ]),
    "hardcoded_secrets": ("Hardcoded Secrets", "CWE-798", [
        ('API_KEY = "sk_live_example_secret_123"', "API_KEY", "environment"),
        ('password = "admin1234"', "password", "environment"),
        ('client_secret = "oauth-secret-value"', "client_secret", "secret manager"),
        ('AWS_SECRET_ACCESS_KEY = "EXAMPLE_STATIC_SECRET"', "AWS_SECRET_ACCESS_KEY", "environment"),
        ('TOKEN = "ghp_example_hardcoded_token"', "TOKEN", "environment"),
    ]),
    "insecure_deserialization": ("Insecure Deserialization", "CWE-502", [
        ('value = pickle.loads(request_body)', "pickle.loads", "json.loads"),
        ('obj = yaml.load(content, Loader=yaml.Loader)', "yaml.load", "safe_load"),
        ('session = pickle.loads(base64.b64decode(cookie))', "pickle.loads", "json"),
        ('data = marshal.loads(blob)', "marshal.loads", "json"),
        ('obj = dill.loads(upload.read())', "dill.loads", "safe format"),
    ]),
    "ssrf": ("Server-Side Request Forgery (SSRF)", "CWE-918", [
        ('response = requests.get(url)', "requests.get", "allowlist"),
        ('urllib.request.urlopen(target)', "urlopen", "allowlist"),
        ('requests.post(callback, data=payload)', "requests.post", "validate"),
        ('httpx.get(user_url)', "httpx.get", "allowlist"),
        ('response = requests.get("http://" + host + "/status")', "requests.get", "allowlist"),
    ]),
    "weak_cryptography": ("Weak Cryptography", "CWE-327", [
        ('digest = hashlib.md5(data).hexdigest()', "md5", "sha256"),
        ('cipher = DES.new(key, DES.MODE_ECB)', "DES.MODE_ECB", "AES.MODE_GCM"),
        ('digest = hashlib.sha1(password.encode()).hexdigest()', "sha1", "argon2"),
        ('cipher = ARC4.new(key)', "ARC4", "AES.MODE_GCM"),
        ('random.seed(time.time()); token = random.getrandbits(64)', "random.getrandbits", "secrets"),
    ]),
    "other_cwes": ("Other CWEs", "CWE-362", [
        ('balance = account.balance', "account.balance", "lock", "CWE-362"),
        ('if request.headers.get("X-Admin"):\n    grant_admin()', "X-Admin", "authorize", "CWE-862"),
        ('zipfile.ZipFile(path).extractall(destination)', "extractall", "validate paths", "CWE-22"),
        ('app.run(debug=True, host="0.0.0.0")', "debug=True", "debug=False", "CWE-489"),
        ('subprocess.run(["tool", user_arg])', "subprocess.run", "validate", "CWE-78"),
    ]),
}

TYPES = {
    "SQL Injection": ("User-controlled data changes the structure of a SQL statement.", "parameterized query"),
    "Command Injection": ("Untrusted input reaches an operating-system command interpreter.", "shell=False"),
    "Path Traversal": ("An untrusted path can escape the intended directory.", "resolve"),
    "Cross-Site Scripting (XSS)": ("Unescaped input is inserted into HTML or script content.", "escape"),
    "Hardcoded Secrets": ("A reusable credential is embedded in source code.", "environment"),
    "Insecure Deserialization": ("Untrusted serialized data can instantiate attacker-controlled objects.", "safe_load"),
    "Server-Side Request Forgery (SSRF)": ("An attacker can make the server request an arbitrary destination.", "allowlist"),
    "Weak Cryptography": ("The code uses an obsolete or unsuitable cryptographic primitive.", "sha256"),
    "Other CWEs": ("The code contains a security weakness requiring context-specific safeguards.", "validate"),
}


def main() -> None:
    truth: dict[str, dict] = {}
    for stem, (kind, cwe, patterns) in CASES.items():
        reason, fix = TYPES[kind]
        for i in range(15 if stem in {"sql_injection", "command_injection", "path_traversal", "xss"} else 10):
            pattern = patterns[i % len(patterns)]
            assignment, marker, remedy = pattern[:3]
            case_cwe = pattern[3] if len(pattern) == 4 else cwe
            filename = f"{stem}_{i + 1:02}.py"
            code = f"# {kind} evaluation case {i + 1}\n{assignment}\n"
            if stem == "sql_injection": code += "cursor.execute(query)\n" if "query =" in assignment else "\n"
            elif stem == "path_traversal": code += "with open(path, 'rb') as stream:\n    content = stream.read()\n"
            elif stem == "command_injection": code += "\n"
            elif stem == "xss": code += "\n"
            elif stem == "insecure_deserialization": code += "\n"
            elif stem == "ssrf": code += "\n"
            elif stem == "weak_cryptography": code += "\n"
            elif stem == "other_cwes": code += "\n"
            elif stem == "hardcoded_secrets": code += "\n"
            (HERE / filename).write_text(code, encoding="utf-8")
            truth[filename] = {"vulnerable": True, "type": kind, "cwe": case_cwe,
                "cwe_accept": [case_cwe], "why": reason, "code_markers": [marker],
                "explanation_keywords": ["untrusted", "user input", "attacker", "hardcoded", "weak", "unsafe", "arbitrary", "escape", "insecure"],
                "fix_keywords": [remedy]}

    secure_samples = [
        "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
        "subprocess.run(['ping', '-c', '1', host], shell=False, check=True)",
        "path = (ROOT / filename).resolve(); assert path.is_relative_to(ROOT.resolve())",
        "return html.escape(username)", "API_KEY = os.environ['API_KEY']",
        "obj = json.loads(payload)", "requests.get(allowlisted_url, timeout=3)",
        "digest = hashlib.sha256(data).hexdigest()", "with account_lock: account.balance -= amount",
        "if current_user.is_admin: grant_admin()",
    ]
    for i in range(20):
        filename = f"secure_{i + 1:02}.py"
        (HERE / filename).write_text(f"# Secure/negative evaluation case {i + 1}\n{secure_samples[i % len(secure_samples)]}\n", encoding="utf-8")
        truth[filename] = {"vulnerable": False, "type": None, "cwe": None,
                           "why": "Uses a safe API or validated input and should not be flagged."}

    (HERE / "ground_truth.json").write_text(json.dumps(truth, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(truth)} cases to {HERE}")


if __name__ == "__main__":
    main()
