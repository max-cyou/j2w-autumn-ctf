import json
import os
import sys
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
marker = "double-vision-functionality-check"
request = urllib.request.Request(
    f"{target}/api/documents",
    data=json.dumps({"content": marker, "private": False}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=5) as response:
    created = json.load(response)
with urllib.request.urlopen(f"{target}/api/preview?name={created['id']}.txt", timeout=5) as response:
    preview = json.load(response)
if preview.get("content") != marker:
    raise RuntimeError("public document preview is broken")
