---
title: "Files"
description: "List, inspect, rename, move, and delete files with the FileService."
---

The `client.files` service provides file management for your JioCloud account. Files are returned as typed `JioFile` dataclasses.

Requires an authenticated client:

```python
from jiocloud import JioCloudClient

client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
)
```

---

## List files

```python
FileService.list() -> list[JioFile]
```

Returns every file visible to the authenticated account.

```python
files = client.files.list()

for file in files:
    print(f"{file.name} ({file.size} bytes) — ID: {file.id}")
```

If the server returns an unexpected payload, the method logs a warning and returns an empty list instead of raising.

### Filter and inspect

```python
files = client.files.list()

pdfs = [f for f in files if f.name.lower().endswith(".pdf")]
total_bytes = sum(f.size for f in files)

print(f"{len(pdfs)} PDFs, {total_bytes / 1024 / 1024:.1f} MiB total")
```

---

## Get file metadata

```python
FileService.get(file_id: str) -> JioFile
```

Fetches metadata for a single file by ID.

```python
file = client.files.get("<FILE_ID>")

print(file.name)
print(file.size)
print(file.mime_type)
print(file.parent_id)
print(file.created_at)
print(file.updated_at)
```

<Note>
If the API returns an unexpected payload, `get()` returns a `JioFile` with the requested ID, an empty name, and size `0` rather than raising.
</Note>

### `JioFile` fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | File ID. |
| `name` | `str` | File name. |
| `size` | `int` | Size in bytes. |
| `parent_id` | `str \| None` | ID of the containing folder. |
| `created_at` | `str \| None` | Creation timestamp. |
| `updated_at` | `str \| None` | Last-modified timestamp. |
| `mime_type` | `str \| None` | MIME type. |
| `raw` | `dict \| None` | Complete, unmodified API payload. |

Use `raw` when you need a field that is not modeled:

```python
file = client.files.get("<FILE_ID>")

if file.raw:
    print(file.raw.get("objectKey"))
```

---

## Rename a file

```python
FileService.rename(file_id: str, new_name: str) -> None
```

```python
client.files.rename("<FILE_ID>", "quarterly-report.pdf")
```

The operation returns `None` on success.

---

## Move a file

```python
FileService.move(file_id: str, dest_folder_id: str) -> None
```

```python
archive = client.folders.create("Archive")

client.files.move("<FILE_ID>", archive.id)
```

---

## Delete a file

```python
FileService.delete(file_id: str) -> None
```

```python
client.files.delete("<FILE_ID>")
```

<Warning>
Deletion is performed against the file ID you provide. Double-check the ID before calling it in bulk operations.
</Warning>

---

## Find a file by name

```python
def find_file(name: str):
    for file in client.files.list():
        if file.name == name:
            return file
    return None

file = find_file("report.pdf")
if file:
    print("Found:", file.id)
```

---

## Bulk rename example

```python
folder_id = "<FOLDER_ID>"

for file in client.files.list():
    if file.parent_id == folder_id and file.name.lower().endswith(".pdf"):
        client.files.rename(file.id, f"archived-{file.name}")
```

---

## End-to-end example

```python
from jiocloud import JioCloudClient

client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
)

folder = client.folders.create("Reports")

client.transfer.upload("report.pdf", parent_id=folder.id)

for file in client.files.list():
    if file.parent_id == folder.id:
        print("Uploaded:", file.name, file.id)

        client.files.rename(file.id, "annual-report.pdf")

        destination = client.folders.create("Archive")
        client.files.move(file.id, destination.id)
```

## Errors

File operations raise the package exception hierarchy. See [Errors & Exceptions](/errors) for details.

```python
from jiocloud import AuthError, NotFoundError

try:
    client.files.get("<FILE_ID>")
except NotFoundError:
    print("File not found.")
except AuthError:
    print("Session expired — sign in again.")
```

## Next steps

- [Organize files with folders](/folders)
- [Upload and download files](/transfer)
- [Stream media files](/media)
