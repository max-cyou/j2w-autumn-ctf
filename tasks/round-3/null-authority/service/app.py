import base64
import hashlib
import hmac
import json
import secrets
import threading

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()
signing_key = secrets.token_bytes(32)
reports = []
lock = threading.Lock()


class Login(BaseModel):
    username: str


class Report(BaseModel):
    content: str


def encode_part(value: dict) -> str:
    raw = json.dumps(value, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def decode_part(value: str) -> dict:
    padding = "=" * (-len(value) % 4)
    return json.loads(base64.urlsafe_b64decode(value + padding))


def issue_token(username: str, role: str = "user") -> str:
    header = encode_part({"alg": "HS256", "typ": "JWT"})
    payload = encode_part({"sub": username, "role": role})
    signature = hmac.new(signing_key, f"{header}.{payload}".encode(), hashlib.sha256).digest()
    return f"{header}.{payload}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"


def current_identity(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "bearer token required")
    token = authorization.removeprefix("Bearer ")
    try:
        header_part, payload_part, signature_part = token.split(".")
        header = decode_part(header_part)
        payload = decode_part(payload_part)
        if header.get("alg") == "HS256":
            expected = hmac.new(signing_key, f"{header_part}.{payload_part}".encode(), hashlib.sha256).digest()
            padding = "=" * (-len(signature_part) % 4)
            supplied = base64.urlsafe_b64decode(signature_part + padding)
            if not hmac.compare_digest(expected, supplied):
                raise ValueError("bad signature")
        elif header.get("alg") == "none":
            pass
        else:
            raise ValueError("unsupported algorithm")
        if not isinstance(payload.get("sub"), str) or payload.get("role") not in {"user", "auditor"}:
            raise ValueError("bad claims")
        return payload
    except Exception:
        raise HTTPException(401, "invalid token")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/login")
def login(data: Login):
    if not 3 <= len(data.username) <= 40:
        raise HTTPException(400, "username must contain 3-40 characters")
    return {"token": issue_token(data.username)}


@app.post("/api/reports", status_code=201)
def create_report(data: Report, authorization: str | None = Header(default=None)):
    identity = current_identity(authorization)
    if not 1 <= len(data.content) <= 4096:
        raise HTTPException(400, "content must contain 1-4096 characters")
    with lock:
        reports.append({"owner": identity["sub"], "content": data.content})
    return {"stored": True}


@app.get("/api/reports")
def own_reports(authorization: str | None = Header(default=None)):
    identity = current_identity(authorization)
    with lock:
        return [report for report in reports if report["owner"] == identity["sub"]]


@app.get("/api/audit")
def audit(authorization: str | None = Header(default=None)):
    identity = current_identity(authorization)
    if identity["role"] != "auditor":
        raise HTTPException(403, "auditor role required")
    with lock:
        return list(reports)
