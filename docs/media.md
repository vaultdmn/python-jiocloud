---
title: "Media Streaming"
description: "Fetch authenticated stream URLs for audio, video, and image objects."
---

JioCloud does not expose permanent public stream URLs. Audio, video, and image objects must be requested through an authenticated media endpoint that returns a short-lived URL.

The `client.media` service handles this handshake for you:

1. It records an access date for the object (best-effort).
2. It requests an authenticated media URL using your session.
3. It returns the URL as a plain string, ready to hand to a browser, media player, or HTTP client.

Requires an authenticated client:

```python
from jiocloud import JioCloudClient

client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
)
```

## Get a stream URL

```python
MediaService.get_stream_url(object_key: str, vdc: str = "jaws") -> str
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `object_key` | `str` | required | The object key of the media file. |
| `vdc` | `str` | `"jaws"` | Virtual data center code. Leave as the default unless JioCloud instructs otherwise. |

Returns the authenticated stream URL (for example an HLS `.m3u8` playlist or a direct media URL).

### Basic usage

```python
url = client.media.get_stream_url("<OBJECT_KEY>")
print(url)
```

### Resolve a file to its object key

File listings expose both a file `id` and the raw API response. The `raw` dictionary can contain the object key used by the media service:

```python
for file in client.files.list():
    if file.name == "movie.mp4":
        object_key = (
            file.raw.get("objectKey")
            or file.raw.get("objKey")
            or file.id
        )
        stream_url = client.media.get_stream_url(object_key)
        print("Play at:", stream_url)
        break
```

<Note>
The exact key name can vary by API response. If `objectKey` is not present, the file `id` is the standard fallback.
</Note>

## Play or consume the URL

The returned URL is a normal HTTP URL. You can open it in a browser, pass it to a media player, or stream it from Python.

### Stream with httpx

```python
import httpx

url = client.media.get_stream_url("<OBJECT_KEY>")

with httpx.stream("GET", url, follow_redirects=True) as response:
    response.raise_for_status()
    with open("media-copy.mp4", "wb") as f:
        for chunk in response.iter_bytes(chunk_size=8192):
            f.write(chunk)
```

### Download a media file with transfer

If you already know the file ID, `client.transfer.download()` is simpler and adds progress reporting:

```python
client.transfer.download(
    file_id="<FILE_ID>",
    dest_path="movie.mp4",
    progress_callback=lambda done, total: print(f"{done}/{total} bytes"),
)
```

See [Uploads & Downloads](/transfer).

## Supported media

`get_stream_url()` is not limited to video. It works for any object the media endpoint accepts, including:

- **Video:** HLS playlists (`.m3u8`) and direct video URLs.
- **Audio:** music and podcast streams.
- **Images:** image objects served through the media host.

## Error handling

The access-date update is **best-effort** and never blocks the result. If it fails, the method continues and still requests the stream URL.

The URL request itself uses the shared HTTP layer, so it raises the standard exceptions:

```python
from jiocloud import APIError, AuthError, JioCloudError

try:
    url = client.media.get_stream_url("<OBJECT_KEY>")
except AuthError:
    print("Sign in again or provide a valid refresh token.")
except APIError as exc:
    print("Media service error:", exc)
except JioCloudError as exc:
    print("Request failed:", exc)
```

## Guidelines

- Treat stream URLs as **temporary secrets**. Do not log, commit, or share them.
- Generate a fresh URL for each playback session instead of caching it indefinitely.
- Reuse one authenticated `JioCloudClient` across calls so the session and token refresh are shared.
- See [Errors & Exceptions](/errors) for retry and redaction behaviour.
