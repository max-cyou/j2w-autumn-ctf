# Double Vision

Round 2 challenge written in Python with FastAPI. The service separates public document previews from private documents.

## Layout

- `service/` — vulnerable document service;
- `jury/checker.py` — verifies public document creation and preview;
- `jury/inject.py` — stores a private document containing a random flag;
- `jury/exploit.py` — canonical exploit used by the jury.

## Run locally

```bash
docker compose up --build -d
python3 jury/checker.py http://127.0.0.1:8000
python3 jury/inject.py http://127.0.0.1:8000
python3 jury/exploit.py http://127.0.0.1:8000
```

The injector and exploit should print the same flag.

Stop the service:

```bash
docker compose down --volumes
```

## Defense goal

Keep public previews working while ensuring that every resolved preview path remains inside the public directory.
