"""Tests for exception sanitization and secret redaction."""

import pytest
import respx

from jiocloud import JioCloudClient
from jiocloud.exceptions import AuthError


@respx.mock
def test_exception_redacts_secrets() -> None:
    fake_token = "SUPER_SECRET_TOKEN_12345"
    respx.get("https://api.jioaicloud.com/fail").respond(
        401, text=f"Unauthorized with token={fake_token}"
    )

    client = JioCloudClient()
    with pytest.raises(AuthError) as exc_info:
        client.http.get("https://api.jioaicloud.com/fail")

    exc = exc_info.value
    err_str = str(exc)
    err_repr = repr(exc)

    assert fake_token not in err_str
    assert fake_token not in err_repr
    assert "[REDACTED]" in err_str
