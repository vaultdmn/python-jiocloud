"""Exception hierarchy for python-jiocloud with sensitive data redaction."""

import re
from typing import Optional


def _sanitize_message(message: str) -> str:
    """Redact tokens, cookies, and authorization secrets from error messages."""
    if not message:
        return message
    message = re.sub(
        r"(authorization|bearer|basic)\s+[^\s]+",
        r"\1 [REDACTED]",
        message,
        flags=re.IGNORECASE,
    )
    message = re.sub(
        r"(token|cookie|secret|key)=[^&\s]+",
        r"\1=[REDACTED]",
        message,
        flags=re.IGNORECASE,
    )
    return message


class JioCloudError(Exception):
    """Base exception for all JioCloud errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ) -> None:
        sanitized_msg = _sanitize_message(message)
        super().__init__(sanitized_msg)
        self.message = sanitized_msg
        self.status_code = status_code
        self.response_body = _sanitize_message(response_body) if response_body else None


class AuthError(JioCloudError):
    """Raised when authentication fails or token is expired/invalid (401/403)."""


class NotFoundError(JioCloudError):
    """Raised when a requested resource or file/folder is not found (404)."""


class RateLimitError(JioCloudError):
    """Raised when rate limits are exceeded (429)."""


class APIError(JioCloudError):
    """Raised when the API returns an unexpected error (5xx or other non-success)."""
