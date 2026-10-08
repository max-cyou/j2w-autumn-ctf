# Example deployment

The root Compose files in this directory provide a small, generic deployment for reproducing the challenge services after the event. That stack is not the original competition infrastructure and does not include SelfAD, the runner, flag scheduling, scoring or participant repository provisioning.

A sanitized copy of the actual SelfAD/nginx event topology is available in
[`selfad/`](selfad/README.md). It preserves the real domains and operational
settings without publishing passwords, tokens or other production secrets.

The services are intentionally vulnerable. By default every port binds only to `127.0.0.1`; do not change `BIND_ADDRESS` to a public interface unless the host is protected by an appropriate isolated CTF environment.

## Requirements

- Docker Engine with the Compose plugin;
- enough resources to build the Python and C++ images;
- free local ports listed in `.env.example`.

## Configure

From the repository root:

```bash
cp deployment/.env.example deployment/.env
```

Edit `deployment/.env` if different ports or resource limits are needed.

## Start a round

```bash
docker compose \
  --env-file deployment/.env \
  -f deployment/docker-compose.yml \
  --profile round-1 \
  up --build -d
```

Replace `round-1` with `round-2` or `round-3`. To start all six services, use `--profile all`.

The default local endpoints are:

| Round | Service | URL |
| --- | --- | --- |
| 1 | Memo Drop | `http://127.0.0.1:8101` |
| 1 | Telemetry Vault | `http://127.0.0.1:8102` |
| 2 | Double Vision | `http://127.0.0.1:8201` |
| 2 | Receipt Printer | `http://127.0.0.1:8202` |
| 3 | Null Authority | `http://127.0.0.1:8301` |
| 3 | Open Gallery | `http://127.0.0.1:8302` |

## Verify a service

For example, after starting round 1:

```bash
python3 tasks/round-1/memo-drop/jury/checker.py http://127.0.0.1:8101
python3 tasks/round-1/memo-drop/jury/inject.py http://127.0.0.1:8101
python3 tasks/round-1/memo-drop/jury/exploit.py http://127.0.0.1:8101
```

The jury scripts are included for post-event reproduction. They should not be exposed to participants during a live event.

## Inspect and stop

```bash
docker compose --env-file deployment/.env -f deployment/docker-compose.yml ps
docker compose --env-file deployment/.env -f deployment/docker-compose.yml --profile all down --volumes
```

Service state is intentionally ephemeral and is discarded when the containers are removed.
