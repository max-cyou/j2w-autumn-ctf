import os
import secrets
import threading
import urllib.parse
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
root = Path("/tmp/document-vault")
public_root = root / "public"
private_root = root / "private"
public_root.mkdir(parents=True, exist_ok=True)
private_root.mkdir(parents=True, exist_ok=True)
documents = []
lock = threading.Lock()


class Document(BaseModel):
    content: str
    private: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/documents", status_code=201)
def create_document(document: Document):
    if not 1 <= len(document.content) <= 4096:
        raise HTTPException(400, "content must contain 1-4096 characters")
    document_id = secrets.token_hex(8)
    directory = private_root if document.private else public_root
    (directory / f"{document_id}.txt").write_text(document.content, encoding="utf-8")
    with lock:
        documents.append({"id": document_id, "private": document.private})
    return {"id": document_id, "private": document.private}


@app.get("/api/index")
def index():
    with lock:
        return list(documents)


@app.get("/api/preview")
def preview(name: str):
    if ".." in name or name.startswith("/"):
        raise HTTPException(400, "invalid document name")
    decoded_name = urllib.parse.unquote(name)
    path = os.path.join(public_root, decoded_name)
    try:
        content = Path(path).read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        raise HTTPException(404, "document not found")
    return {"content": content}
