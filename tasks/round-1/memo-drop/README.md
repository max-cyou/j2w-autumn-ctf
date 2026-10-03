# Memo Drop

Round 1 challenge written in Python with Flask. The service stores private notes protected by capability keys.

## Layout

- `service/` — vulnerable service and its container image;
- `jury/checker.py` — verifies normal note creation and reading;
- `jury/inject.py` — creates a note containing a random flag;
- `jury/exploit.py` — canonical exploit used by the jury.

## Run locally

```bash
docker compose up --build -d
python3 jury/checker.py http://127.0.0.1:8000
python3 jury/inject.py http://127.0.0.1:8000
python3 jury/exploit.py http://127.0.0.1:8000
```

The injector prints the expected 32-character flag. The exploit should recover and print the same value.

Stop the service:

```bash
docker compose down --volumes
```

## Defense goal

Prevent unauthorized note reads while keeping the create/read flow with the complete capability key operational.
