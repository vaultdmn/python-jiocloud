---
title: "Folders"
description: "List and create folders with the FolderService."
---

The `client.folders` service manages your JioCloud folders. Every folder is returned as a typed `JioFolder` dataclass, so you can access its properties directly instead of parsing raw JSON.

All folder operations require an authenticated client:

```python
from jiocloud import JioCloudClient

client = JioCloudClient(
    user_id="<USER_ID>",
    device_key="<DEVICE_KEY>",
    refresh_token="<REFRESH_TOKEN>",
)
```

## List folders

```python
FolderService.list() -> list[JioFolder]
```

Returns every folder visible to the authenticated account. If the API returns an unexpected payload, the method logs a warning and returns an empty list rather than raising.

```python
folders = client.folders.list()

for folder in folders:
    print(f"{folder.name} ({folder.id})")
```

Each `JioFolder` exposes:

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Unique folder ID. |
| `name` | `str` | Folder display name. |
| `parent_id` | `str \| None` | ID of the containing folder, if any. |
| `created_at` | `str \| None` | Creation timestamp as returned by the API. |
| `updated_at` | `str \| None` | Last-modified timestamp as returned by the API. |
| `raw` | `dict \| None` | The complete, unmodified API response for the folder. |

```python
for folder in client.folders.list():
    print(folder.name, "inside", folder.parent_id or "root", "created", folder.created_at)
```

## Create a folder

```python
FolderService.create(name: str, parent_id: str | None = None) -> JioFolder
```

Creates a new folder and returns the created `JioFolder`.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `name` | `str` | required | Name of the new folder. |
| `parent_id` | `str \| None` | `None` | ID of the parent folder. Omit to create the folder at the root. |

### Create a top-level folder

```python
folder = client.folders.create("My Documents")

print(folder.name)  # My Documents
print(folder.id)    # <FOLDER_ID>
```

### Create a nested folder

Pass the ID of an existing folder as `parent_id`:

```python
parent = client.folders.create("Projects")
child = client.folders.create("Invoices", parent_id=parent.id)

print(f"Created {child.name} inside {parent.name}")
```

### Create a folder and upload into it

The returned `JioFolder.id` can be passed straight to `client.transfer.upload()` or `client.folders.create()`:

```python
destination = client.folders.create("Uploads")

client.transfer.upload(
    "report.pdf",
    parent_id=destination.id,
    progress_callback=lambda done, total: print(f"{done}/{total} bytes"),
)
```

## Handling errors

Folder operations use the shared HTTP layer, so failures raise the package exception hierarchy. For example, an expired session raises `AuthError` after an automatic refresh attempt:

```python
from jiocloud import AuthError, NotFoundError

try:
    folder = client.folders.create("Archive")
except AuthError as exc:
    print("Session expired:", exc)
except NotFoundError as exc:
    print("Parent folder not found:", exc)
```

See [Errors & Exceptions](/errors) for the complete list of exceptions and retry behaviour.
