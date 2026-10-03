import json
import os
import sys
import urllib.parse
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
owner = 77777
marker = "telemetry-functionality-check"
data = urllib.parse.urlencode({"owner": owner, "text": marker}).encode()
request = urllib.request.Request(f"{target}/api/messages", data=data, method="POST")
with urllib.request.urlopen(request, timeout=5) as response:
    created = json.load(response)
query = urllib.parse.urlencode({"id": created["id"], "owner": owner})
with urllib.request.urlopen(f"{target}/api/messages/read?{query}", timeout=5) as response:
    message = json.load(response)
if message.get("text") != marker:
    raise RuntimeError("message could not be read by its complete owner id")
