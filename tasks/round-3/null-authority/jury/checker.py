import json
import os
import secrets
import sys
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
username = f"checker-{secrets.token_hex(4)}"
login = urllib.request.Request(
    f"{target}/api/login",
    data=json.dumps({"username": username}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(login, timeout=5) as response:
    token = json.load(response)["token"]
marker = "null-authority-functionality-check"
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
create = urllib.request.Request(
    f"{target}/api/reports",
    data=json.dumps({"content": marker}).encode(),
    headers=headers,
    method="POST",
)
with urllib.request.urlopen(create, timeout=5):
    pass
read = urllib.request.Request(f"{target}/api/reports", headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(read, timeout=5) as response:
    reports = json.load(response)
if not any(report.get("content") == marker for report in reports):
    raise RuntimeError("ordinary signed-token report flow is broken")
