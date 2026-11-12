"""Tests for automated token refresh functionality."""

import httpx
import pytest
import respx

from jiocloud import JioCloudClient
from jiocloud.exceptions import AuthError


@respx.mock
def test_token_refresh_success() -> None:
    respx.get("https://api.jioaicloud.com/protected").side_effect = [
        httpx.Response(401, text="Expired Token"),
        httpx.Response(200, json={"data": "success"}),
    ]
    respx.put("https://api.jioaicloud.com/account/token/refresh").respond(
        200,
        json={
            "authToken": {
                "accessToken": "new_access_token",
                "refreshToken": "new_refresh_token",
            }
        },
    )

    client = JioCloudClient(refresh_token="old_refresh_token")
    res = client.http.get("https://api.jioaicloud.com/protected")
    assert res == {"data": "success"}


@respx.mock
def test_token_refresh_failure() -> None:
    respx.get("https://api.jioaicloud.com/protected").respond(
        401, text="Expired Token"
    )
    respx.put("https://api.jioaicloud.com/account/token/refresh").respond(
        401, text="Invalid Refresh"
    )

    client = JioCloudClient(refresh_token="bad_refresh_token")
    with pytest.raises(AuthError):
        client.http.get("https://api.jioaicloud.com/protected")
