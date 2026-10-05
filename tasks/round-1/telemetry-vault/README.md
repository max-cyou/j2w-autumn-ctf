# Telemetry Vault

Round 1 challenge written in C++20. The service stores telemetry messages and authorizes reads using numeric owner IDs.

## Layout

- `service/` — vulnerable service and its multi-stage container build;
- `jury/checker.py` — verifies creation and reading with a complete owner ID;
- `jury/inject.py` — stores ten random flags as telemetry data;
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

Correct the owner authorization check without removing public telemetry metadata or breaking legitimate reads.
