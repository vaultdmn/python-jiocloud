---
title: "python-jiocloud"
description: "An unofficial Python client and library for the JioCloud web API."
---

Welcome to the documentation for **python-jiocloud**, a clean, fully typed, robust Python library that wraps JioCloud's web API.

## What you can build

`python-jiocloud` lets you integrate JioCloud into Python applications, scripts, and automations:

- **Sign in** with an OTP sent to a mobile number or an email address.
- **Browse and manage** files and folders: list, inspect metadata, rename, move, and delete.
- **Upload and download** files as streams, with live progress callbacks.
- **Stream media** by requesting authenticated, short-lived URLs for audio, video, and images.
- **Handle failures** through a typed exception hierarchy with automatic retries, token refresh, and secret redaction.

## Quick example

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
    print(f"{file.name} ({file.size} bytes)")

client.transfer.download("<FILE_ID>", "downloaded.bin")
```

## Where to go next

<CardGroup cols={2}>
  <Card title="Installation" icon="download" href="/installation">
    Install from PyPI or set up a development environment.
  </Card>
  <Card title="Authentication" icon="key" href="/authentication">
    Sign in with a mobile number or email OTP.
  </Card>
  <Card title="Files" icon="file" href="/files">
    List, inspect, rename, move, and delete files.
  </Card>
  <Card title="Uploads & Downloads" icon="arrows-up-down" href="/transfer">
    Stream transfers with progress callbacks.
  </Card>
  <Card title="Media Streaming" icon="play" href="/media">
    Resolve authenticated stream URLs for media.
  </Card>
  <Card title="API Reference" icon="book" href="/api-reference">
    Every class, method, parameter, and exception.
  </Card>
</CardGroup>

## Disclaimer

> This project is an unofficial, community-driven library. It is not affiliated with, endorsed by, or connected to Reliance Jio Infocomm Limited or JioCloud. Use at your own risk and respect the service's terms of service and rate limits.
