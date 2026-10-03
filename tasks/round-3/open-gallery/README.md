# Open Gallery

Round 3 beginner challenge written in Python with Flask. Public metadata belongs in the gallery, while file contents belong only to the uploader.

## Layout

- `service/` — vulnerable gallery service;
- `jury/checker.py` — verifies owner upload and download;
- `jury/inject.py` — uploads a private file containing a random flag;
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

Enforce file ownership during downloads without hiding public metadata or breaking an owner's access to their own file.
