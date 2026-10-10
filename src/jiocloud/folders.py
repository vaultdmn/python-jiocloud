"""Folder management service for JioCloud."""

from typing import Any, Optional

from jiocloud._http import JioCloudHTTPClient
from jiocloud.models import JioFolder


class FolderService:
    """Manages folder listing and creation."""

    def __init__(self, http: JioCloudHTTPClient) -> None:
        self.http = http
        self.base_url = "https://jaws-api.jioaicloud.com"

    def list(self) -> list[JioFolder]:
        """List folders."""
        url = f"{self.base_url}/nms/folders"
        response = self.http.get(url)
        items: list[JioFolder] = []
        if isinstance(response, dict):
            raw_list = (
                response.get("folders")
                or response.get("items")
                or response.get("data")
                or []
            )
            if isinstance(raw_list, list):
                items = [JioFolder.from_dict(item) for item in raw_list]
        elif isinstance(response, list):
            items = [JioFolder.from_dict(item) for item in response]
        return items

    def create(self, name: str, parent_id: Optional[str] = None) -> JioFolder:
        """Create a new folder.

        Args:
            name: Folder name.
            parent_id: Optional parent folder ID.

        Returns:
            Created JioFolder object.
        """
        url = f"{self.base_url}/nms/folders"
        payload: dict[str, Any] = {"name": name}
        if parent_id:
            payload["parentId"] = parent_id
        response = self.http.post(url, json=payload)
        if isinstance(response, dict):
            folder_data = response.get("folder") or response.get("data") or response
            return JioFolder.from_dict(folder_data)
        return JioFolder(id="", name=name)
