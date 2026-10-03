import json
import os
import sys
import urllib.parse
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
request = urllib.request.Request(
    f"{target}/api/coupons",
    data=urllib.parse.urlencode({"secret": "functionality-secret"}).encode(),
    method="POST",
)
with urllib.request.urlopen(request, timeout=5) as response:
    created = json.load(response)
query = urllib.parse.urlencode({"id": created["id"], "label": "Customer receipt"})
with urllib.request.urlopen(f"{target}/api/receipt?{query}", timeout=5) as response:
    receipt = json.load(response)
if receipt.get("receipt") != "Customer receipt":
    raise RuntimeError("ordinary receipt rendering is broken")
