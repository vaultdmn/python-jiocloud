"""File management service for JioCloud."""

import logging

from jiocloud._http import JioCloudHTTPClient
from jiocloud.models import JioFile

logger = logging.getLogger("jiocloud.files")


class FileService:
    """Manages file listing, metadata, renaming, moving, and deletion."""

    def __init__(self, http: JioCloudHTTPClient) -> None:
        self.http = http
        self.base_url = "https://jaws-api.jioaicloud.com"

    def list(self) -> list[JioFile]:
        """List files and metadata items."""
        url = f"{self.base_url}/nms/metadata"
        response = self.http.get(url)
        items: list[JioFile] = []
        if isinstance(response, dict):
            raw_list = response.get("files") or response.get("items") or response.get("data") or []
            if not raw_list and "metadata" in response:
                raw_list = response["metadata"]
            if isinstance(raw_list, list):
                items = [JioFile.from_dict(item) for item in raw_list]
            else:
                logger.warning(
                    "Unexpected schema for files list response: %s",
                    type(response.get("files")),
                )
        elif isinstance(response, list):
            items = [JioFile.from_dict(item) for item in response]
        else:
            logger.warning("Unexpected response type for files list: %s", type(response))
        return items

    def get(self, file_id: str) -> JioFile:
        """Get metadata for a specific file ID."""
        url = f"{self.base_url}/nms/metadata/version/{file_id}"
        response = self.http.get(url)
        if isinstance(response, dict):
            item_data = response.get("file") or response.get("data") or response
            return JioFile.from_dict(item_data)
        return JioFile(id=file_id, name="", size=0)

    def rename(self, file_id: str, new_name: str) -> None:
        """Rename a file."""
        url = f"{self.base_url}/nms/metadata/1.0"
        payload = {"fileId": file_id, "name": new_name}
        self.http.put(url, json=payload)

    def move(self, file_id: str, dest_folder_id: str) -> None:
        """Move a file to another folder."""
        url = f"{self.base_url}/nms/metadata/1.0"
        payload = {"fileId": file_id, "parentId": dest_folder_id}
        self.http.put(url, json=payload)

    def delete(self, file_id: str) -> None:
        """Delete a file."""
        url = f"{self.base_url}/nms/metadata/1.0"
        payload = {"fileIds": [file_id]}
        self.http.delete(url, json=payload)
