# J2W Autumn CTF

Official challenge source archive for **J2W Autumn CTF**, organized by the **jmp2win** team.

- CTF announcements and community: [t.me/j2wctf](https://t.me/j2wctf)
- Organizer: [t.me/jmp2win](https://t.me/jmp2win)
- Website: [jmp2win.xyz](https://jmp2win.xyz)

## About the event

J2W Autumn CTF was built around source review and practical vulnerability fixing. The event contained three rounds with two services in each round.

For every service, participants worked in two directions:

1. **Attack** — find the intended vulnerability, write an exploit and recover injected flags.
2. **Defense** — patch the vulnerable service without breaking its legitimate behavior.

The jury checked both parts automatically. A successful defense had to stop the canonical exploit while continuing to pass the functionality checker.

## Challenges

| Round | Challenge | Stack | Main idea | Writeup |
| --- | --- | --- | --- | --- |
| 1 | [Memo Drop](tasks/round-1/memo-drop/) | Python / Flask | Capability-based authorization | [Read](writeups/round-1/memo-drop.md) |
| 1 | [Telemetry Vault](tasks/round-1/telemetry-vault/) | C++20 | Integer conversions in access checks | [Read](writeups/round-1/telemetry-vault.md) |
| 2 | [Double Vision](tasks/round-2/double-vision/) | Python / FastAPI | Path validation and URL decoding | [Read](writeups/round-2/double-vision.md) |
| 2 | [Receipt Printer](tasks/round-2/receipt-printer/) | C++20 | Unsafe string formatting | [Read](writeups/round-2/receipt-printer.md) |
| 3 | [Null Authority](tasks/round-3/null-authority/) | Python / FastAPI | JWT signature validation | [Read](writeups/round-3/null-authority.md) |
| 3 | [Open Gallery](tasks/round-3/open-gallery/) | Python / Flask | Object-level authorization | [Read](writeups/round-3/open-gallery.md) |

The complete challenge index is available in [`tasks/README.md`](tasks/README.md).

## Repository structure

```text
tasks/
├── round-1/
├── round-2/
└── round-3/
    └── challenge-name/
        ├── service/             # vulnerable source given to participants
        ├── jury/
        │   ├── checker.py       # legitimate functionality check
        │   ├── inject.py        # inserts a random flag
        │   └── exploit.py       # canonical jury exploit
        ├── docker-compose.yml   # isolated local deployment
        └── README.md            # challenge-specific instructions
writeups/                        # official solutions and defensive patches
├── round-1/
├── round-2/
└── round-3/
```

During the event, the `jury/` directories were private. They are included here so the complete check flow can be reproduced after the CTF.

## Official writeups

Detailed solutions are available in [`writeups/`](writeups/README.md). Each writeup explains the vulnerable code, manual reproduction, canonical jury exploit, correct defensive patch and the functionality that the patch must preserve.

## Running a challenge locally

Every challenge is self-contained and uses the same workflow. For example:

```bash
cd tasks/round-1/memo-drop
docker compose up --build -d
```

Run the legitimate functionality check:

```bash
python3 jury/checker.py http://127.0.0.1:8000
```

Inject a random flag, then run the canonical exploit:

```bash
python3 jury/inject.py http://127.0.0.1:8000
python3 jury/exploit.py http://127.0.0.1:8000
```

The injector and exploit should print the same 32-character flag. Flags use the format:

```text
[A-Z0-9]{32}
```

Stop the service when finished:

```bash
docker compose down --volumes
```

Run one challenge at a time: all compose files publish their service on `127.0.0.1:8000`.

## Safety

These services are intentionally vulnerable. The supplied compose files bind them to localhost and apply basic container restrictions, but they are still challenge code. Do not expose them directly to the public internet or reuse them as production applications.

## Credits

Organized by **jmp2win**.

- [CTF channel — @j2wctf](https://t.me/j2wctf)
- [Team channel — @jmp2win](https://t.me/jmp2win)
- [jmp2win.xyz](https://jmp2win.xyz)
