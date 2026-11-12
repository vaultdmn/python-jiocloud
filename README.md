# python-jiocloud

[![CI](https://github.com/vaultdmn/python-jiocloud/actions/workflows/ci.yml/badge.svg?style=flat)](https://github.com/vaultdmn/python-jiocloud/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/python-jiocloud.svg?style=flat)](https://pypi.org/project/python-jiocloud/)
[![Python Version](https://img.shields.io/pypi/pyversions/python-jiocloud.svg?style=flat)](https://pypi.org/project/python-jiocloud/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)](https://opensource.org/licenses/MIT)

An unofficial Python client and library for JioCloud web API, built with `httpx`.

> **Disclaimer:** This project is an unofficial, community-driven library. It is not affiliated with, endorsed by, or connected to Reliance Jio Infocomm Limited or JioCloud. Use at your own risk and respect the service's terms of service and rate limits.

---

## Installation

```bash
pip install python-jiocloud
```

For development:
```bash
pip install -e ".[dev]"
```

---

## Quickstart & Authentication

### Phone Number Login
```python
from jiocloud import JioCloudClient

client = JioCloudClient()

# 1. Send OTP to mobile number
client.auth.send_otp(mobile_number="+910000000000")

# 2. Verify OTP
auth_result = client.auth.verify_otp(mobile_number="+910000000000", otp="123456")
print(auth_result)
```

### Email Login
```python
from jiocloud import JioCloudClient

client = JioCloudClient()

# 1. Send OTP to email address
client.auth.send_otp(email_id="user@example.com")

# 2. Verify OTP
auth_result = client.auth.verify_otp(email_id="user@example.com", otp="123456")
print(auth_result)
```

### File & Folder Operations
```python
# Initialize with user ID and device key
client = JioCloudClient(user_id="<USER_ID>", device_key="<DEVICE_KEY>")

# List files
for file in client.files.list():
    print(file.name, file.size)

# Create a folder
folder = client.folders.create("My Documents")

# Upload a file with progress callback
client.transfer.upload(
    "local_document.pdf",
    parent_id=folder.id,
    progress_callback=lambda up, total: print(f"Uploaded {up}/{total} bytes"),
)

# Download a file with progress callback
client.transfer.download(
    file_id="<FILE_ID>",
    dest_path="downloaded.pdf",
    progress_callback=lambda down, total: print(f"Downloaded {down}/{total} bytes"),
)
```

---

## Features

- **Authentication:** OTP-based sign-in via Mobile Number or Email ID, automatic token refresh, and session management.
- **Files & Folders:** List, get metadata, create folders, rename, move, and delete files.
- **Transfer:** Upload and download files with streaming and progress callbacks.
- **Typed & Robust:** Full type hints (`py.typed`) and built-in error handling with secret redaction.

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
