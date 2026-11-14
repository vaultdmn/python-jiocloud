---
title: "Installation"
description: "Install python-jiocloud from PyPI or set up a development environment."
---

## Requirements

- **Python 3.10 or newer** (the package metadata also allows 3.9, but CI and development target 3.10+).
- **[httpx](https://www.python-httpx.org/) 0.24 or newer**, installed automatically as a dependency.

## Install from PyPI

```bash
pip install python-jiocloud
```

Verify the installation:

```python
import jiocloud

print(jiocloud.__version__)  # 0.1.0
```

## Install with pipx or uv

```bash
uv add python-jiocloud
```

```bash
pipx install python-jiocloud
```

## Development setup

Clone the repository and install the development extras:

```bash
git clone https://github.com/vaultdmn/python-jiocloud.git
cd python-jiocloud
pip install -e ".[dev,docs]"
```

This installs `pytest`, `pytest-cov`, `respx`, `ruff`, `mypy`, and the documentation tooling declared in `pyproject.toml`.

## Verify the checkout

Run the same checks as CI:

```bash
pytest
ruff check src tests
ruff format --check src tests
mypy src
```

All four commands should pass before you open a pull request.

## Type checking support

`python-jiocloud` ships a `py.typed` marker, so mypy, pyright, and your editor pick up the bundled annotations automatically — no stubs or extra configuration required.

```python
from jiocloud import JioCloudClient

client: JioCloudClient = JioCloudClient()
```

## Next steps

- [Authenticate with an OTP](/authentication)
- [Work with files](/files) and [folders](/folders)
- [Upload and download with progress](/transfer)
- [Fetch media stream URLs](/media)
