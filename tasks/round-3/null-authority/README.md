# Null Authority

Round 3 challenge written in Python with FastAPI. The service uses JWT bearer tokens to separate user reports from the auditor feed.

## Layout

- `service/` — vulnerable report service and JWT implementation;
- `jury/checker.py` — verifies the normal signed-token report flow;
- `jury/inject.py` — creates ten user reports containing random flags;
- `jury/exploit.py` — canonical exploit used by the jury.

## Run locally

```bash
docker compose up --build -d
python3 jury/checker.py http://127.0.0.1:8000
python3 jury/inject.py http://127.0.0.1:8000
python3 jury/exploit.py http://127.0.0.1:8000
```

The injector and exploit should print the same ten flags.

Stop the service:

```bash
docker compose down --volumes
```

## Defense goal

Require an authentic server signature for privileged claims while preserving valid HS256 user tokens.
