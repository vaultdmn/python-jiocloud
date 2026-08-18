# python-jiocloud

[![CI](https://github.com/vaultdmn/python-jiocloud/actions/workflows/ci.yml/badge.svg)](https://github.com/vaultdmn/python-jiocloud/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/python-jiocloud.svg)](https://pypi.org/project/python-jiocloud/)
[![Python Version](https://img.shields.io/pypi/pyversions/python-jiocloud.svg)](https://pypi.org/project/python-jiocloud/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

## Quickstart

```python
from jiocloud import JioCloudClient

# Initialize client with credentials or session token
client = JioCloudClient(user_id="<USER_ID>", device_key="<DEVICE_KEY>")

# List files and folders
files = client.files.list()
for f in files:
    print(f.name, f.size)
```

---

## Features

- **Authentication:** OTP-based sign-in and session management.
- **Files & Folders:** List, get metadata, create folders, rename, move, and delete files.
- **Transfer:** Upload and download files with progress callbacks.
- **Typed & Robust:** Full type hints (`py.typed`) and built-in error handling.

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
