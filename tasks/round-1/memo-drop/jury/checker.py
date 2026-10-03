import json
import os
import sys
import urllib.parse
import urllib.request

target = (os.environ.get("SELFAD_TARGET") or sys.argv[1]).rstrip("/")
marker = "memo-drop-functionality-check"
request = urllib.request.Request(
    f"{target}/api/notes",
    data=json.dumps({"text": marker}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=5) as response:
    created = json.load(response)
key = urllib.parse.quote(created["key"], safe="")
with urllib.request.urlopen(f"{target}/api/notes/{created['id']}?key={key}", timeout=5) as response:
    note = json.load(response)
if note.get("text") != marker:
    raise RuntimeError("created note could not be read with its capability")
