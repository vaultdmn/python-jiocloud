---
title: "Authentication"
description: "Sign in to JioCloud with a mobile number or email OTP."
---

`python-jiocloud` supports OTP-based sign-in through either a **mobile number** or an **email address**. Authentication is a two-step flow:

1. `client.auth.send_otp(...)` sends a one-time password.
2. `client.auth.verify_otp(...)` exchanges the OTP for a session.

You do not need credentials to start the client:

```python
from jiocloud import JioCloudClient

client = JioCloudClient()
```

---

## Phone number authentication

### Step 1 — Send the OTP

```python
AuthService.send_otp(mobile_number: str | None = None, email_id: str | None = None) -> None
```

Pass the mobile number **including the country code**:

```python
client.auth.send_otp(mobile_number="+910000000000")
```

The method returns `None`. A successful request means JioCloud accepted the number and dispatched the OTP.

### Step 2 — Verify the OTP

```python
AuthService.verify_otp(
    mobile_number: str | None = None,
    email_id: str | None = None,
    otp: str = "",
    is_stay_sign_in: bool = True,
) -> dict[str, Any]
```

```python
session = client.auth.verify_otp(
    mobile_number="+910000000000",
    otp="123456",
    is_stay_sign_in=True,
)

print(session["requestId"])

for account in session.get("userAccounts", []):
    print("User ID:", account.get("userId"))
```

`verify_otp()` returns the raw JioCloud response as a dictionary. The important values typically live in `userAccounts`:

```python
account = session.get("userAccounts", [{}])[0]
user_id = account.get("userId")
```

Pass `is_stay_sign_in=False` if you do **not** want a persistent session.

---

## Email authentication

Email sign-in uses the same two methods with `email_id` instead of `mobile_number`. When both are supplied, `email_id` takes precedence.

### Step 1 — Send the OTP

```python
client.auth.send_otp(email_id="user@example.com")
```

### Step 2 — Verify the OTP

```python
session = client.auth.verify_otp(
    email_id="user@example.com",
    otp="509933",
    is_stay_sign_in=True,
)

account = session.get("userAccounts", [{}])[0]
print("Authenticated user:", account.get("userId"))
```

---

## Apply the session to the client

After a successful login, pass the returned identifiers and tokens to `update_auth()` so subsequent file, folder, transfer, and media calls are authenticated:

```python
account = session.get("userAccounts", [{}])[0]

client.update_auth(
    user_id=account.get("userId"),
    device_key="<DEVICE_KEY>",
    refresh_token=session.get("refreshToken"),
    access_token=session.get("accessToken"),
)
```

```python
JioCloudClient.update_auth(
    user_id: str | None = None,
    device_key: str | None = None,
    refresh_token: str | None = None,
    access_token: str | None = None,
) -> None
```

Only non-`None` values are applied. `access_token`, when provided, is sent as a `Basic` authorization header.

<Note>
The exact response keys are controlled by JioCloud and can change. Read them defensively with `.get()` rather than indexing directly if you need your integration to be resilient.
</Note>

---

## Create a client in one step

If you already have credentials saved from a previous session, construct the client directly:

```python
from jiocloud import JioCloudClient

client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
)
```

| Parameter | Description |
| :--- | :--- |
| `user_id` | Sent as `X-User-Id`. |
| `device_key` | Sent as `X-Device-Key`. |
| `refresh_token` | Enables automatic access-token refresh. |
| `access_token` | Optional initial `Authorization` token. |
| `api_key` / `app_secret` | Override the built-in client identification values. |
| `timeout` / `max_retries` | Tune request timeout and retry behaviour. |

---

## Automatic token refresh

When a request returns `401 Unauthorized` or `403 Forbidden`, the client:

1. Refreshes the access token once using the configured `refresh_token`.
2. Retries the original request.
3. Raises `AuthError` only if the refresh fails or no refresh token is available.

```python
client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
)
```

Concurrent requests are protected by a lock, so only one refresh runs at a time.

---

## Complete reusable login helper

```python
from typing import Any

from jiocloud import JioCloudClient


def login_with_mobile(mobile_number: str, otp: str) -> JioCloudClient:
    client = JioCloudClient()
    client.auth.send_otp(mobile_number=mobile_number)
    session: dict[str, Any] = client.auth.verify_otp(
        mobile_number=mobile_number,
        otp=otp,
    )

    account = session.get("userAccounts", [{}])[0]
    client.update_auth(
        user_id=account.get("userId"),
        refresh_token=session.get("refreshToken"),
        access_token=session.get("accessToken"),
    )
    return client
```

---

## Security notes

- Never commit phone numbers, email addresses, OTPs, tokens, or captured HTTP traffic. Use placeholders like `<USER_ID>` in code and examples.
- Treat `refresh_token` and `access_token` as secrets. Store them in an environment variable or secret manager.
- Exception messages are sanitized automatically; see [Errors & Exceptions](/errors).
- Sign out by discarding the client, and rotate tokens if a device is lost.
