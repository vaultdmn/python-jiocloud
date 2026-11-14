---
title: "Uploads & Downloads"
description: "Stream files to and from JioCloud with progress callbacks using the TransferService."
---

The `client.transfer` service streams file content in **8 KiB chunks**, so large files are never loaded fully into memory. Both methods accept an optional `progress_callback` that is invoked after every chunk.

The callback signature is:

```python
def callback(bytes_done: int, total_bytes: int | None) -> None: ...
```

`total_bytes` comes from the server's `Content-Length` header for downloads, and from the local file size for uploads. It can be `None` when the server does not report a length.

Requires an authenticated client:

```python
from jiocloud import JioCloudClient

client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
)
```

## Upload a file

```python
TransferService.upload(
    file_path: str,
    parent_id: str | None = None,
    progress_callback: Callable[[int, int | None], None] | None = None,
) -> dict[str, Any]
```

Uploads a local file as a streamed multipart request and returns the API response as a dictionary.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `file_path` | `str` | required | Path to the local file to upload. |
| `parent_id` | `str \| None` | `None` | ID of the destination folder. Omit to upload to the root. |
| `progress_callback` | `Callable \| None` | `None` | Called with `(bytes_uploaded, total_bytes)` after each chunk. |

### Basic upload

```python
result = client.transfer.upload("photo.jpg")

print(result)
```

### Upload into a specific folder

```python
folder = client.folders.create("Holiday Photos")

result = client.transfer.upload(
    "beach.jpg",
    parent_id=folder.id,
)
```

### Upload with progress reporting

```python
def on_progress(uploaded: int, total: int | None) -> None:
    if total:
        percent = uploaded / total * 100
        print(f"Uploaded {uploaded}/{total} bytes ({percent:.1f}%)")
    else:
        print(f"Uploaded {uploaded} bytes")

client.transfer.upload(
    "backup.zip",
    progress_callback=on_progress,
)
```

<Note>
A common issue is logging progress for every 8 KiB chunk, which floods the console. Throttle the output if the file is large:

```python
last_reported = -1

def on_progress(uploaded: int, total: int | None) -> None:
    global last_reported
    if not total:
        return
    percent = int(uploaded / total * 100)
    if percent != last_reported and percent % 10 == 0:
        last_reported = percent
        print(f"{percent}% uploaded")

client.transfer.upload("large-video.mp4", progress_callback=on_progress)
```
</Note>

## Download a file

```python
TransferService.download(
    file_id: str,
    dest_path: str,
    progress_callback: Callable[[int, int | None], None] | None = None,
) -> None
```

Streams a file from JioCloud directly to a local path. The destination file is created or overwritten. The method returns `None` and raises an exception if the HTTP request fails.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `file_id` | `str` | required | ID of the file to download. |
| `dest_path` | `str` | required | Local path to write the downloaded content to. |
| `progress_callback` | `Callable \| None` | `None` | Called with `(bytes_downloaded, total_bytes)` after each chunk. |

### Basic download

```python
client.transfer.download(
    file_id="<FILE_ID>",
    dest_path="downloaded-photo.jpg",
)

print("Download complete")
```

### Download with progress reporting

```python
def on_progress(downloaded: int, total: int | None) -> None:
    if total:
        print(f"Downloaded {downloaded}/{total} bytes ({downloaded / total * 100:.1f}%)")
    else:
        print(f"Downloaded {downloaded} bytes")

client.transfer.download(
    file_id="<FILE_ID>",
    dest_path="backup.zip",
    progress_callback=on_progress,
)
```

### Find a file ID before downloading

Use `client.files.list()` to locate the ID, then download:

```python
for file in client.files.list():
    if file.name == "report.pdf":
        client.transfer.download(file.id, "report.pdf")
        break
```

## End-to-end example

Create a folder, upload a file into it, verify it appears in the listing, then download it back:

```python
from jiocloud import JioCloudClient

client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
)

folder = client.folders.create("Reports")

result = client.transfer.upload(
    "report.pdf",
    parent_id=folder.id,
)
print("Upload response:", result)

uploaded = next(f for f in client.files.list() if f.name == "report.pdf")

client.transfer.download(
    uploaded.id,
    "report-copy.pdf",
    progress_callback=lambda done, total: print(f"Downloaded {done} bytes"),
)
```

## Behaviour and limitations

- Transfers are **streaming**, not resumable. If the connection drops mid-transfer, retry the whole operation.
- The download destination is overwritten without prompting.
- `upload()` sends a standard multipart request through the configured `httpx.Client`; `download()` opens its own streaming request. Both respect the client's configured `timeout`.
- Rate limits and server errors are retried automatically up to `max_retries`; see [Errors & Exceptions](/errors).
