"""JioCloudClient facade."""

from typing import Optional

from jiocloud._http import JioCloudHTTPClient
from jiocloud.auth import AuthService
from jiocloud.files import FileService
from jiocloud.folders import FolderService
from jiocloud.media import MediaService
from jiocloud.transfer import TransferService


class JioCloudClient:
    """Client facade for JioCloud API."""

    def __init__(
        self,
        user_id: Optional[str] = None,
        device_key: Optional[str] = None,
        refresh_token: Optional[str] = None,
        api_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self.user_id = user_id
        self.device_key = device_key
        self.refresh_token = refresh_token
        self.http = JioCloudHTTPClient(
            api_key=api_key,
            app_secret=app_secret,
            device_key=device_key,
            user_id=user_id,
            refresh_token=refresh_token,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.auth = AuthService(self.http)
        self.files = FileService(self.http)
        self.folders = FolderService(self.http)
        self.transfer = TransferService(self.http)
        self.media = MediaService(self.http)

    def update_auth(
        self,
        user_id: Optional[str] = None,
        device_key: Optional[str] = None,
        refresh_token: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> None:
        """Update authenticated user ID, device key, and tokens across all services."""
        if user_id is not None:
            self.user_id = user_id
        if device_key is not None:
            self.device_key = device_key
        if refresh_token is not None:
            self.refresh_token = refresh_token
        self.http.update_auth(
            user_id=self.user_id,
            device_key=self.device_key,
            refresh_token=self.refresh_token,
            access_token=access_token,
        )
