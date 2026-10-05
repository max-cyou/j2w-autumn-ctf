import json
import os
import secrets
import string
import sys
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
alphabet = string.ascii_uppercase + string.digits
for _ in range(10):
    flag = "".join(secrets.choice(alphabet) for _ in range(32))
    request = urllib.request.Request(
        f"{target}/api/notes",
        data=json.dumps({"text": flag}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        if response.status != 201:
            raise RuntimeError(f"create returned {response.status}")
    print(flag)
