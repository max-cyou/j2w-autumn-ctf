import json
import os
import secrets
import string
import sys
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
flag = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(32))
register = urllib.request.Request(
    f"{target}/api/register",
    data=json.dumps({"name": f"owner-{secrets.token_hex(4)}"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(register, timeout=5) as response:
    token = json.load(response)["token"]
upload = urllib.request.Request(
    f"{target}/api/files",
    data=json.dumps({"name": "private.txt", "content": flag}).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST",
)
with urllib.request.urlopen(upload, timeout=5):
    pass
print(flag)
