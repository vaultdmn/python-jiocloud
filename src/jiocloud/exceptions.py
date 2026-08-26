"""Exception hierarchy for python-jiocloud."""

from typing import Optional


class JioCloudError(Exception):
    """Base exception for all JioCloud errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body


class AuthError(JioCloudError):
    """Raised when authentication fails or token is expired/invalid (401/403)."""


class NotFoundError(JioCloudError):
    """Raised when a requested resource or file/folder is not found (404)."""


class RateLimitError(JioCloudError):
    """Raised when rate limits are exceeded (429)."""


class APIError(JioCloudError):
    """Raised when the API returns an unexpected error (5xx or other non-success)."""
