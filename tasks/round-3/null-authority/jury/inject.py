import json
import os
import secrets
import string
import sys
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
username = f"reporter-{secrets.token_hex(4)}"
login = urllib.request.Request(
    f"{target}/api/login",
    data=json.dumps({"username": username}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(login, timeout=5) as response:
    token = json.load(response)["token"]
alphabet = string.ascii_uppercase + string.digits
for _ in range(10):
    flag = "".join(secrets.choice(alphabet) for _ in range(32))
    report = urllib.request.Request(
        f"{target}/api/reports",
        data=json.dumps({"content": flag}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(report, timeout=5):
        pass
    print(flag)
