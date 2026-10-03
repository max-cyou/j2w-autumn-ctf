# Receipt Printer

Round 2 challenge written in C++20. The service renders customer labels for coupon receipts while keeping coupon secrets private.

## Layout

- `service/` — vulnerable receipt service;
- `jury/checker.py` — verifies ordinary receipt rendering;
- `jury/inject.py` — creates a coupon whose secret is a random flag;
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

Render arbitrary customer labels as data without exposing the associated coupon secret.
