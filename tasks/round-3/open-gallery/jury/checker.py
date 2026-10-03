import json
import os
import secrets
import sys
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
register = urllib.request.Request(
    f"{target}/api/register",
    data=json.dumps({"name": f"checker-{secrets.token_hex(4)}"}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(register, timeout=5) as response:
    token = json.load(response)["token"]
marker = "open-gallery-functionality-check"
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
upload = urllib.request.Request(
    f"{target}/api/files",
    data=json.dumps({"name": "check.txt", "content": marker}).encode(),
    headers=headers,
    method="POST",
)
with urllib.request.urlopen(upload, timeout=5) as response:
    file_id = json.load(response)["id"]
read = urllib.request.Request(f"{target}/api/files/{file_id}", headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(read, timeout=5) as response:
    downloaded = json.load(response)
if downloaded.get("content") != marker:
    raise RuntimeError("owner cannot download an uploaded file")
