# J2W Autumn CTF writeups

This directory contains the official writeups for all six services. Each writeup explains the service design, vulnerable code, manual reproduction, canonical exploit and minimal defensive patch.

Do not publish this directory or the `jury/` files before the corresponding round ends.

## Round 1

1. [Memo Drop](round-1/memo-drop.md) — Flask capability check bypass through an empty prefix.
2. [Telemetry Vault](round-1/telemetry-vault.md) — C++ owner ID truncation.

## Round 2

1. [Double Vision](round-2/double-vision.md) — FastAPI path traversal through double URL decoding.
2. [Receipt Printer](round-2/receipt-printer.md) — C++ format string secret disclosure.

## Round 3

1. [Null Authority](round-3/null-authority.md) — FastAPI accepting unsigned JWTs with `alg: none`.
2. [Open Gallery](round-3/open-gallery.md) — Flask IDOR caused by a missing ownership check.

## Source layout

- `tasks/round-N/<name>/service/` — vulnerable service distributed to participants.
- `tasks/round-N/<name>/jury/inject.py` — stores a random flag through the legitimate API.
- `tasks/round-N/<name>/jury/checker.py` — verifies functionality that a defense must preserve.
- `tasks/round-N/<name>/jury/exploit.py` — canonical organizer exploit.

SelfAD recognizes a flag only when an output line fully matches `[A-Z0-9]{32}`. Canonical exploits therefore print recovered flags without mixing them with debug output.
