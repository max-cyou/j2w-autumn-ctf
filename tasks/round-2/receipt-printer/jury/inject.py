import json
import os
import secrets
import string
import sys
import urllib.parse
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
flag = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(32))
request = urllib.request.Request(
    f"{target}/api/coupons",
    data=urllib.parse.urlencode({"secret": flag}).encode(),
    method="POST",
)
with urllib.request.urlopen(request, timeout=5) as response:
    json.load(response)
print(flag)
