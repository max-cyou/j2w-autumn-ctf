import secrets
import threading

from flask import Flask, jsonify, request

app = Flask(__name__)
notes = {}
lock = threading.Lock()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/notes")
def create_note():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")
    if not isinstance(text, str) or not 1 <= len(text) <= 4096:
        return {"error": "text must contain 1-4096 characters"}, 400
    note_id = secrets.token_hex(6)
    key = secrets.token_urlsafe(18)
    with lock:
        notes[note_id] = {"text": text, "key": key}
    return {"id": note_id, "key": key}, 201


@app.get("/api/recent")
def recent_notes():
    with lock:
        return jsonify([{"id": note_id} for note_id in notes][-100:])


@app.get("/api/notes/<note_id>")
def read_note(note_id):
    supplied_key = request.args.get("key", "")
    with lock:
        note = notes.get(note_id)
    if note is None:
        return {"error": "note not found"}, 404
    if not note["key"].startswith(supplied_key):
        return {"error": "invalid capability"}, 403
    return {"id": note_id, "text": note["text"]}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
