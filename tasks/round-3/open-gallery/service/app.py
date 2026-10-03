import secrets
import threading

from flask import Flask, jsonify, request

app = Flask(__name__)
accounts = {}
files = []
lock = threading.Lock()


def current_token():
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    with lock:
        return token if token in accounts else None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/register")
def register():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    if not isinstance(name, str) or not 3 <= len(name) <= 40:
        return {"error": "invalid name"}, 400
    token = secrets.token_hex(18)
    with lock:
        accounts[token] = {"name": name}
    return {"token": token}, 201


@app.post("/api/files")
def upload_file():
    token = current_token()
    if token is None:
        return {"error": "bearer token required"}, 401
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    content = payload.get("content")
    if (
        not isinstance(name, str)
        or not name
        or not isinstance(content, str)
        or not 1 <= len(content) <= 4096
    ):
        return {"error": "invalid file"}, 400
    with lock:
        file_id = len(files) + 1
        files.append(
            {"id": file_id, "name": name, "content": content, "owner": token}
        )
    return {"id": file_id}, 201


@app.get("/api/gallery")
def gallery():
    with lock:
        return jsonify(
            [{"id": item["id"], "name": item["name"]} for item in files]
        )


@app.get("/api/files/<int:file_id>")
def read_file(file_id):
    if current_token() is None:
        return {"error": "bearer token required"}, 401
    with lock:
        if not 1 <= file_id <= len(files):
            return {"error": "file not found"}, 404
        item = files[file_id - 1]
        return {
            "id": item["id"],
            "name": item["name"],
            "content": item["content"],
        }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
