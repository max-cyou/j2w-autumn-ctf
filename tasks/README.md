# Challenges

The event contained three rounds with two services in each round.

| Round | Challenge | Stack | Vulnerability |
| --- | --- | --- | --- |
| 1 | [Memo Drop](round-1/memo-drop/) | Python / Flask | Capability-prefix authorization bypass |
| 1 | [Telemetry Vault](round-1/telemetry-vault/) | C++20 | Integer truncation in an owner check |
| 2 | [Double Vision](round-2/double-vision/) | Python / FastAPI | Path traversal through double URL decoding |
| 2 | [Receipt Printer](round-2/receipt-printer/) | C++20 | User-controlled format string |
| 3 | [Null Authority](round-3/null-authority/) | Python / FastAPI | Unsigned JWT accepted with `alg: none` |
| 3 | [Open Gallery](round-3/open-gallery/) | Python / Flask | IDOR without an ownership check |

Each challenge directory contains:

- `service/` — the vulnerable source distributed to participants;
- `jury/` — the functionality checker, flag injector and canonical exploit;
- `docker-compose.yml` — an isolated local service deployment;
- `README.md` — local launch and verification commands.

Run one challenge at a time because every compose file publishes the service on `127.0.0.1:8000`.
