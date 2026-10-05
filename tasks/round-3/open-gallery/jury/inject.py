import json
import os
import secrets
import string
import sys
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
register = urllib.request.Request(
    f"{target}/api/register",
    data=json.dumps({"name": f"owner-{secrets.token_hex(4)}"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(register, timeout=5) as response:
    token = json.load(response)["token"]
alphabet = string.ascii_uppercase + string.digits
for index in range(10):
    flag = "".join(secrets.choice(alphabet) for _ in range(32))
    upload = urllib.request.Request(
        f"{target}/api/files",
        data=json.dumps({"name": f"private-{index}.txt", "content": flag}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(upload, timeout=5):
        pass
    print(flag)
