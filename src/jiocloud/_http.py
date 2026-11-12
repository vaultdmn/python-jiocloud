"""HTTP transport layer for JioCloud API using httpx."""

import threading
from typing import Any, Optional

import httpx

from jiocloud.exceptions import (
    APIError,
    AuthError,
    NotFoundError,
    RateLimitError,
)


class JioCloudHTTPClient:
    """Wrapper around httpx.Client with default headers, error mapping,

    retries, and token refresh.
    """

    DEFAULT_API_KEY = "c153b48e-d8a1-48a0-a40d-293f1dc5be0e"
    DEFAULT_APP_SECRET = "ODc0MDE2M2EtNGY0MC00YmU2LTgwZDUtYjNlZjIxZGRkZjlj"
    DEFAULT_CLIENT_DETAILS = "clientType:WEB; appVersion:89.0.12"
    DEFAULT_DEVICE_TYPE = "W"

    def __init__(
        self,
        api_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        device_key: Optional[str] = None,
        user_id: Optional[str] = None,
        refresh_token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key or self.DEFAULT_API_KEY
        self.app_secret = app_secret or self.DEFAULT_APP_SECRET
        self.device_key = device_key
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.timeout = timeout
        self.max_retries = max_retries
        self._lock = threading.Lock()

        self.client = httpx.Client(
            timeout=self.timeout,
            headers=self._build_default_headers(),
        )

    def _build_default_headers(self) -> dict[str, str]:
        headers = {
            "X-Api-Key": self.api_key,
            "X-App-Secret": self.app_secret,
            "X-Client-Details": self.DEFAULT_CLIENT_DETAILS,
            "X-Device-Type": self.DEFAULT_DEVICE_TYPE,
            "Accept": "application/json; charset=UTF-8",
            "Content-Type": "application/json; charset=UTF-8",
        }
        if self.device_key:
            headers["X-Device-Key"] = self.device_key
        if self.user_id:
            headers["X-User-Id"] = self.user_id
        return headers

    def update_auth(
        self,
        user_id: Optional[str] = None,
        device_key: Optional[str] = None,
        refresh_token: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> None:
        """Update auth / identification headers and tokens."""
        if user_id is not None:
            self.user_id = user_id
        if device_key is not None:
            self.device_key = device_key
        if refresh_token is not None:
            self.refresh_token = refresh_token
        self.client.headers.update(self._build_default_headers())
        if access_token is not None:
            self.client.headers["Authorization"] = f"Basic {access_token}"

    def _refresh_access_token(self) -> bool:
        """Refresh access token using refresh_token."""
        if not self.refresh_token:
            return False
        url = "https://api.jioaicloud.com/account/token/refresh"
        payload = {
            "refreshToken": self.refresh_token,
            "deviceType": self.DEFAULT_DEVICE_TYPE,
            "jToken": True,
            "isIdamOn": "true",
            "isStaySignIn": True,
            "deviceInfo": {
                "model": "browser",
                "deviceName": "Web Device",
                "type": "browser",
                "isWebClient": True,
                "deviceKey": self.device_key or "default-device-key",
            },
        }
        try:
            response = self.client.put(url, json=payload)
            if response.is_success:
                data = response.json()
                token_data = data.get("authToken") or data
                new_access = token_data.get("accessToken")
                new_refresh = token_data.get("refreshToken")
                if new_access:
                    self.client.headers["Authorization"] = f"Basic {new_access}"
                if new_refresh:
                    self.refresh_token = new_refresh
                return True
        except Exception:
            pass
        return False

    def _handle_response(
        self,
        response: httpx.Response,
        method: str = "GET",
        url: str = "",
        kwargs: Optional[dict[str, Any]] = None,
        refreshed: bool = False,
    ) -> Any:
        if response.is_success:
            if response.status_code == 204 or not response.content:
                return {}
            try:
                return response.json()
            except Exception:
                return response.text

        status = response.status_code
        text = response.text

        if status in (401, 403) and not refreshed:
            with self._lock:
                if self._refresh_access_token():
                    retry_kwargs = kwargs or {}
                    retry_resp = self.client.request(method, url, **retry_kwargs)
                    return self._handle_response(
                        retry_resp, method, url, retry_kwargs, refreshed=True
                    )

        if status in (401, 403):
            raise AuthError(
                f"Auth failed ({status}): {text}",
                status_code=status,
                response_body=text,
            )
        elif status == 404:
            raise NotFoundError(
                f"Not found ({status}): {text}",
                status_code=status,
                response_body=text,
            )
        elif status == 429:
            raise RateLimitError(
                f"Rate limit ({status}): {text}",
                status_code=status,
                response_body=text,
            )
        elif status >= 500:
            raise APIError(
                f"Server error ({status}): {text}",
                status_code=status,
                response_body=text,
            )
        else:
            raise APIError(
                f"API error ({status}): {text}",
                status_code=status,
                response_body=text,
            )

    def request(self, method: str, url: str, **kwargs: Any) -> Any:
        """Execute HTTP request with retry handling for 429/5xx and token refresh on 401."""
        retries = 0
        while True:
            try:
                response = self.client.request(method, url, **kwargs)
                if response.status_code == 429 or response.status_code >= 500:
                    if retries < self.max_retries:
                        retries += 1
                        continue
                return self._handle_response(response, method, url, kwargs, refreshed=False)
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                if retries < self.max_retries:
                    retries += 1
                    continue
                raise APIError(f"Network error during request to {url}: {exc}")

    def get(self, url: str, **kwargs: Any) -> Any:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Any:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Any:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Any:
        return self.request("DELETE", url, **kwargs)
