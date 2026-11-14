---
title: "Errors & Exceptions"
description: "Understand the exception hierarchy, automatic retries, token refresh, and secret redaction."
---

All failures raised by the package inherit from `JioCloudError`, so you can catch the whole family with one `except` block or handle specific cases individually.

## Exception hierarchy

```text
JioCloudError
├── AuthError        # 401 / 403
├── NotFoundError    # 404
├── RateLimitError   # 429
└── APIError         # 5xx, other non-success statuses, network failures
```

Import any of them directly from the package root:

```python
from jiocloud import (
    APIError,
    AuthError,
    JioCloudError,
    NotFoundError,
    RateLimitError,
)
```

| Exception | When it is raised |
| :--- | :--- |
| `JioCloudError` | Base class. Never raised directly by the package. |
| `AuthError` | Authentication failed, or the session is still invalid after an automatic token refresh (`401`, `403`). |
| `NotFoundError` | The requested file, folder, or resource does not exist (`404`). |
| `RateLimitError` | The server rejected the request because of rate limiting (`429`). |
| `APIError` | Any other non-success response (`5xx` or an unexpected `4xx`), or a network failure after all retries. |

## Exception attributes

Every exception exposes:

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `message` | `str` | The sanitized error message. |
| `status_code` | `int \| None` | HTTP status code, when the error came from a response. |
| `response_body` | `str \| None` | Sanitized response body, when available. |

```python
from jiocloud import APIError

try:
    client.files.get("<FILE_ID>")
except APIError as exc:
    print("Message:", exc.message)
    print("Status:", exc.status_code)
    print("Body:", exc.response_body)
```

## Handling specific errors

```python
from jiocloud import AuthError, JioCloudError, NotFoundError, RateLimitError

try:
    file = client.files.get("<FILE_ID>")
except NotFoundError:
    print("That file does not exist.")
except RateLimitError:
    print("Too many requests — wait before retrying.")
except AuthError:
    print("Session expired. Sign in again or pass a refresh token.")
except JioCloudError as exc:
    print("JioCloud request failed:", exc)
```

<Warning>
Catch subclasses **before** `JioCloudError`. Python checks `except` clauses in order, so a broad `except JioCloudError` first would swallow the specific handlers below it.
</Warning>

## Automatic retries

The HTTP layer retries certain failures before raising anything:

- **`429` and `5xx`** responses are retried up to `max_retries` times (default `3`).
- **Network errors and timeouts** from `httpx` are retried up to `max_retries` times.
- **`401` / `403`** responses trigger a single automatic token refresh when a `refresh_token` was supplied. If the refresh succeeds, the original request is retried transparently.

Configure the limits when creating the client:

```python
from jiocloud import JioCloudClient

client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
    timeout=60.0,     # seconds per request
    max_retries=5,    # retries for 429 / 5xx / network errors
)
```

If all retries fail, an exception from the hierarchy is raised — for example:

```python
from jiocloud import APIError

try:
    files = client.files.list()
except APIError as exc:
    print("Gave up after retries:", exc)
```

## Automatic token refresh

Token refresh only happens when the client has a `refresh_token`:

```python
client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
)
```

When a request returns `401` or `403`:

1. The client refreshes the access token once, under a lock so concurrent requests cannot refresh at the same time.
2. It retries the original request.
3. If the retry still fails — or no refresh token is configured — it raises `AuthError`.

If you obtain fresh credentials yourself, update the client without recreating it:

```python
client.update_auth(
    user_id="<NEW_USER_ID>",
    device_key="<NEW_DEVICE_KEY>",
    refresh_token="<NEW_REFRESH_TOKEN>",
    access_token="<NEW_ACCESS_TOKEN>",
)
```

## Secret redaction

Error messages and response bodies are sanitized before they reach your logs or exception handlers. Authorization headers, bearer/basic tokens, and query parameters named `token`, `cookie`, `secret`, or `key` are replaced with `[REDACTED]`.

```python
from jiocloud import JioCloudError

try:
    client.files.list()
except JioCloudError as exc:
    # Any accidental secret in the upstream response is already redacted.
    print(exc)
```

For example, a raw error containing:

```text
Authorization: Basic abc123 token=supersecret
```

is exposed as:

```text
Authorization: [REDACTED] token=[REDACTED]
```

<Note>
Redaction is a safety net, not a guarantee. Do not intentionally log credentials, and never commit tokens or captured HTTP traffic.
</Note>

## Best practices

- Catch `JioCloudError` at your application boundary; catch specific subclasses only where the recovery differs.
- Treat `AuthError` as a signal to re-authenticate and then call `client.update_auth()`.
- Back off on `RateLimitError` rather than retrying immediately.
- Never wrap these exceptions in a way that logs unsanitized request details.
- See each service guide for the operations that can raise: [Files](/files), [Folders](/folders), [Uploads & Downloads](/transfer), [Media Streaming](/media).
