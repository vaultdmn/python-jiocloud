"""python-jiocloud: Unofficial Python client for JioCloud API."""

__version__ = "0.1.0"

from jiocloud.client import JioCloudClient
from jiocloud.exceptions import (
    APIError,
    AuthError,
    JioCloudError,
    NotFoundError,
    RateLimitError,
)

__all__ = [
    "JioCloudClient",
    "JioCloudError",
    "AuthError",
    "NotFoundError",
    "RateLimitError",
    "APIError",
]
