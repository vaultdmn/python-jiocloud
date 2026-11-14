---
title: "API Reference"
description: "Every public class, method, attribute, and exception in python-jiocloud."
---

Everything below is the public surface of `python-jiocloud` v0.1.0. All examples assume:

```python
from jiocloud import JioCloudClient

client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
)
```

The package ships with `py.typed`, so editors and type checkers pick up annotations automatically.

---

## `JioCloudClient`

```python
JioCloudClient(
    user_id: str | None = None,
    device_key: str | None = None,
    refresh_token: str | None = None,
    api_key: str | None = None,
    app_secret: str | None = None,
    timeout: float = 30.0,
    max_retries: int = 3,
)
```

The main entry point. Creates the HTTP transport and exposes one service object per feature area.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `str \| None` | `None` | Authenticated JioCloud user ID, sent as `X-User-Id`. |
| `device_key` | `str \| None` | `None` | Persistent device UUID, sent as `X-Device-Key`. |
| `refresh_token` | `str \| None` | `None` | Enables automatic access-token refresh on `401` / `403`. |
| `api_key` | `str \| None` | built-in default | Overrides the default `X-Api-Key`. |
| `app_secret` | `str \| None` | built-in default | Overrides the default `X-App-Secret`. |
| `timeout` | `float` | `30.0` | Per-request timeout in seconds. |
| `max_retries` | `int` | `3` | Retries for `429`, `5xx`, and network errors. |

### Attributes

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `user_id` | `str \| None` | Current user ID. |
| `device_key` | `str \| None` | Current device key. |
| `refresh_token` | `str \| None` | Current refresh token. |
| `http` | `JioCloudHTTPClient` | Low-level transport (headers, retries, refresh). |
| `auth` | `AuthService` | OTP authentication methods. |
| `files` | `FileService` | File listing and metadata operations. |
| `folders` | `FolderService` | Folder listing and creation. |
| `transfer` | `TransferService` | Uploads and downloads. |
| `media` | `MediaService` | Media stream URLs. |

### Example

```python
from jiocloud import JioCloudClient

client = JioCloudClient()

client.auth.send_otp(mobile_number="+910000000000")
session = client.auth.verify_otp(mobile_number="+910000000000", otp="123456")

account = session.get("userAccounts", [{}])[0]
client.update_auth(
    user_id=account.get("userId"),
    refresh_token=session.get("refreshToken"),
)

for file in client.files.list():
    print(file.name)
```

### `update_auth`

```python
JioCloudClient.update_auth(
    user_id: str | None = None,
    device_key: str | None = None,
    refresh_token: str | None = None,
    access_token: str | None = None,
) -> None
```

Updates credentials in place and propagates them to the shared HTTP client. Only non-`None` values are applied. Use it after a fresh login or when rotating tokens.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `user_id` | `str \| None` | New user ID. |
| `device_key` | `str \| None` | New device key. |
| `refresh_token` | `str \| None` | New refresh token. |
| `access_token` | `str \| None` | New access token, sent as `Authorization: Basic <token>`. |

```python
client.update_auth(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
    access_token="<ACCESS_TOKEN>",
)
```

---

## `AuthService` — `client.auth`

### `send_otp`

```python
AuthService.send_otp(
    mobile_number: str | None = None,
    email_id: str | None = None,
) -> None
```

Sends a one-time password to a mobile number or an email address. When `email_id` is provided it takes precedence. Sending does not authenticate you; call `verify_otp()` with the received code.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `mobile_number` | `str \| None` | Mobile number including country code, e.g. `"+910000000000"`. |
| `email_id` | `str \| None` | Registered email address, e.g. `"user@example.com"`. |

```python
client.auth.send_otp(mobile_number="+910000000000")
client.auth.send_otp(email_id="user@example.com")
```

### `verify_otp`

```python
AuthService.verify_otp(
    mobile_number: str | None = None,
    email_id: str | None = None,
    otp: str = "",
    is_stay_sign_in: bool = True,
) -> dict[str, Any]
```

Verifies the OTP and returns the raw authentication response. The response typically contains a `requestId` and a `userAccounts` list with the `userId`, product type, and allocated space. When `email_id` is provided it takes precedence over `mobile_number`.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `mobile_number` | `str \| None` | `None` | Mobile number used for `send_otp()`. |
| `email_id` | `str \| None` | `None` | Email address used for `send_otp()`. |
| `otp` | `str` | `""` | The OTP code received. |
| `is_stay_sign_in` | `bool` | `True` | Whether to request a persistent session. |

```python
response = client.auth.verify_otp(
    mobile_number="+910000000000",
    otp="123456",
    is_stay_sign_in=True,
)

print(response["requestId"])

for account in response.get("userAccounts", []):
    print("User:", account.get("userId"))
```

```python
response = client.auth.verify_otp(
    email_id="user@example.com",
    otp="509933",
)
```

<Note>
The exact response keys are controlled by JioCloud. Access them defensively with `response.get(...)` if you are building a long-lived integration.
</Note>

---

## `FileService` — `client.files`

### `list`

```python
FileService.list() -> list[JioFile]
```

Returns all files visible to the authenticated account. Unexpected response shapes are logged and produce an empty list.

```python
for file in client.files.list():
    print(file.id, file.name, file.size, file.mime_type)
```

### `get`

```python
FileService.get(file_id: str) -> JioFile
```

Returns metadata for one file. If the API returns an unexpected payload, a `JioFile` with the requested ID, an empty name, and size `0` is returned.

```python
file = client.files.get("<FILE_ID>")
print(file.name)
print(file.parent_id)
print(file.created_at)
print(file.updated_at)
print(file.mime_type)
```

### `rename`

```python
FileService.rename(file_id: str, new_name: str) -> None
```

Renames a file in place.

```python
client.files.rename("<FILE_ID>", "quarterly-report.pdf")
```

### `move`

```python
FileService.move(file_id: str, dest_folder_id: str) -> None
```

Moves a file into another folder.

```python
folder = client.folders.create("Archive")
client.files.move("<FILE_ID>", folder.id)
```

### `delete`

```python
FileService.delete(file_id: str) -> None
```

Deletes a file by ID.

```python
client.files.delete("<FILE_ID>")
```

### Example: rename every PDF in a folder

```python
for file in client.files.list():
    if file.name.endswith(".pdf") and file.parent_id == "<FOLDER_ID>":
        client.files.rename(file.id, f"archived-{file.name}")
```

---

## `FolderService` — `client.folders`

### `list`

```python
FolderService.list() -> list[JioFolder]
```

Returns all folders visible to the authenticated account.

```python
for folder in client.folders.list():
    print(folder.id, folder.name, folder.parent_id)
```

### `create`

```python
FolderService.create(name: str, parent_id: str | None = None) -> JioFolder
```

Creates a folder and returns it. Omit `parent_id` to create it at the root.

```python
root_folder = client.folders.create("Projects")
nested = client.folders.create("2026", parent_id=root_folder.id)

print(nested.id)
```

---

## `TransferService` — `client.transfer`

### `upload`

```python
TransferService.upload(
    file_path: str,
    parent_id: str | None = None,
    progress_callback: Callable[[int, int | None], None] | None = None,
) -> dict[str, Any]
```

Streams a local file to JioCloud and returns the raw API response.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `file_path` | `str` | Local file path. |
| `parent_id` | `str \| None` | Destination folder ID. Root when omitted. |
| `progress_callback` | `Callable \| None` | Receives `(bytes_uploaded, total_bytes)`. `total_bytes` is the local file size. |

```python
result = client.transfer.upload("photo.jpg", parent_id="<FOLDER_ID>")
print(result)
```

```python
client.transfer.upload(
    "movie.mp4",
    progress_callback=lambda done, total: print(f"{done}/{total} bytes sent"),
)
```

### `download`

```python
TransferService.download(
    file_id: str,
    dest_path: str,
    progress_callback: Callable[[int, int | None], None] | None = None,
) -> None
```

Streams a file from JioCloud to a local path, creating or overwriting it.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `file_id` | `str` | ID of the file to download. |
| `dest_path` | `str` | Local destination path. |
| `progress_callback` | `Callable \| None` | Receives `(bytes_downloaded, total_bytes)`; total may be `None`. |

```python
client.transfer.download(
    "<FILE_ID>",
    "downloaded.jpg",
    progress_callback=lambda done, total: print(f"{done}/{total} bytes received"),
)
```

---

## `MediaService` — `client.media`

### `get_stream_url`

```python
MediaService.get_stream_url(object_key: str, vdc: str = "jaws") -> str
```

Records an access date (best-effort) and returns an authenticated, short-lived stream URL for the object.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `object_key` | `str` | required | Object key of the media file. |
| `vdc` | `str` | `"jaws"` | Virtual data center code. |

```python
url = client.media.get_stream_url("<OBJECT_KEY>")
print(url)
```

```python
# If the object key is not exposed directly, the file ID is the fallback.
file = client.files.get("<FILE_ID>")
object_key = file.raw.get("objectKey", file.id) if file.raw else file.id
url = client.media.get_stream_url(object_key)
```

---

## Models

### `JioFile`

```python
@dataclass
JioFile(
    id: str,
    name: str,
    size: int,
    parent_id: str | None = None,
    created_at: str | None = None,
    updated_at: str | None = None,
    mime_type: str | None = None,
    raw: dict[str, Any] | None = None,
)
```

Returned by `client.files.list()` and `client.files.get()`.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | File ID. |
| `name` | `str` | File name. |
| `size` | `int` | Size in bytes. |
| `parent_id` | `str \| None` | Containing folder ID. |
| `created_at` | `str \| None` | Creation timestamp. |
| `updated_at` | `str \| None` | Last-modified timestamp. |
| `mime_type` | `str \| None` | MIME type. |
| `raw` | `dict \| None` | Complete API payload. |

```python
file = client.files.get("<FILE_ID>")

print(f"{file.name} ({file.size} bytes)")
print(file.raw.get("objectKey") if file.raw else None)
```

The classmethod `JioFile.from_dict(data)` converts an API dictionary into a `JioFile`:

```python
from jiocloud.models import JioFile

file = JioFile.from_dict({"fileId": "<FILE_ID>", "name": "notes.txt", "size": 128})
print(file.name)
```

### `JioFolder`

```python
@dataclass
JioFolder(
    id: str,
    name: str,
    parent_id: str | None = None,
    created_at: str | None = None,
    updated_at: str | None = None,
    raw: dict[str, Any] | None = None,
)
```

Returned by `client.folders.list()` and `client.folders.create()`.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Folder ID. |
| `name` | `str` | Folder name. |
| `parent_id` | `str \| None` | Containing folder ID. |
| `created_at` | `str \| None` | Creation timestamp. |
| `updated_at` | `str \| None` | Last-modified timestamp. |
| `raw` | `dict \| None` | Complete API payload. |

```python
folder = client.folders.create("Invoices")
print(folder.id, folder.name, folder.parent_id)
```

The classmethod `JioFolder.from_dict(data)` converts an API dictionary into a `JioFolder`:

```python
from jiocloud.models import JioFolder

folder = JioFolder.from_dict({"folderId": "<FOLDER_ID>", "name": "Invoices"})
print(folder.name)
```

---

## Exceptions

```python
from jiocloud import (
    APIError,
    AuthError,
    JioCloudError,
    NotFoundError,
    RateLimitError,
)
```

| Exception | Parent | Status codes | Description |
| :--- | :--- | :--- | :--- |
| `JioCloudError` | `Exception` | — | Base class for every package error. |
| `AuthError` | `JioCloudError` | `401`, `403` | Authentication or authorization failure. |
| `NotFoundError` | `JioCloudError` | `404` | Resource not found. |
| `RateLimitError` | `JioCloudError` | `429` | Rate limit exceeded. |
| `APIError` | `JioCloudError` | `5xx`, other | Server/API error or network failure. |

Every exception accepts `message`, `status_code`, and `response_body`, and exposes them as attributes after sanitization.

```python
from jiocloud import JioCloudError

try:
    client.files.delete("<FILE_ID>")
except JioCloudError as exc:
    print(exc.message)
    print(exc.status_code)
    print(exc.response_body)
```

See [Errors & Exceptions](/errors) for retry, refresh, and redaction details.

---

## Module-level values

```python
import jiocloud

print(jiocloud.__version__)  # "0.1.0"
```

`jiocloud.__all__` exports:

```python
[
    "JioCloudClient",
    "JioCloudError",
    "AuthError",
    "NotFoundError",
    "RateLimitError",
    "APIError",
]
```

The `jiocloud.models` module exposes `JioFile` and `JioFolder`. The transport class `jiocloud._http.JioCloudHTTPClient` is internal and may change without notice.
