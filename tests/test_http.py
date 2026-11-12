"""Tests for JioCloudHTTPClient."""

import httpx
import pytest
import respx

from jiocloud._http import JioCloudHTTPClient
from jiocloud.exceptions import APIError, AuthError, NotFoundError, RateLimitError


@respx.mock
def test_http_get_success() -> None:
    respx.get("https://api.jioaicloud.com/test").respond(200, json={"status": "ok"})
    http = JioCloudHTTPClient()
    res = http.get("https://api.jioaicloud.com/test")
    assert res == {"status": "ok"}


@respx.mock
def test_http_error_mapping() -> None:
    http = JioCloudHTTPClient()

    respx.get("https://api.jioaicloud.com/401").respond(401, text="Unauthorized")
    with pytest.raises(AuthError) as exc_info:
        http.get("https://api.jioaicloud.com/401")
    assert exc_info.value.status_code == 401

    respx.get("https://api.jioaicloud.com/404").respond(404, text="Not Found")
    with pytest.raises(NotFoundError) as exc_info:
        http.get("https://api.jioaicloud.com/404")
    assert exc_info.value.status_code == 404

    respx.get("https://api.jioaicloud.com/429").respond(429, text="Rate Limit")
    with pytest.raises(RateLimitError) as exc_info:
        http.get("https://api.jioaicloud.com/429")
    assert exc_info.value.status_code == 429

    respx.get("https://api.jioaicloud.com/500").respond(500, text="Server Error")
    with pytest.raises(APIError) as exc_info:
        http.get("https://api.jioaicloud.com/500")
    assert exc_info.value.status_code == 500

    respx.get("https://api.jioaicloud.com/400").respond(400, text="Bad Request")
    with pytest.raises(APIError) as exc_info:
        http.get("https://api.jioaicloud.com/400")
    assert exc_info.value.status_code == 400


@respx.mock
def test_http_retries() -> None:
    route = respx.get("https://api.jioaicloud.com/retry").respond(
        503, text="Service Unavailable"
    )
    http = JioCloudHTTPClient(max_retries=2)
    with pytest.raises(APIError):
        http.get("https://api.jioaicloud.com/retry")
    assert route.call_count == 3  # initial + 2 retries


@respx.mock
def test_http_no_retry_on_4xx() -> None:
    route = respx.get("https://api.jioaicloud.com/bad").respond(
        400, text="Bad Request"
    )
    http = JioCloudHTTPClient(max_retries=2)
    with pytest.raises(APIError):
        http.get("https://api.jioaicloud.com/bad")
    assert route.call_count == 1


@respx.mock
def test_http_transport_error_retry() -> None:
    route = respx.get("https://api.jioaicloud.com/timeout")
    route.side_effect = httpx.TimeoutException("Timeout")
    http = JioCloudHTTPClient(max_retries=1)
    with pytest.raises(APIError) as exc_info:
        http.get("https://api.jioaicloud.com/timeout")
    assert "Network error" in str(exc_info.value)
    assert route.call_count == 2
