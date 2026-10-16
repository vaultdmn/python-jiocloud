"""File transfer service for downloading and uploading files with progress callbacks."""

import os
from typing import Any, Callable, Optional

from jiocloud._http import JioCloudHTTPClient


class TransferService:
    """Handles file downloads and uploads with optional progress callbacks."""

    def __init__(self, http: JioCloudHTTPClient) -> None:
        self.http = http
        self.dl_base_url = "https://jaws-dl.jioaicloud.com"
        self.upload_base_url = "https://jaws-upload.jioaicloud.com"

    def download(
        self,
        file_id: str,
        dest_path: str,
        progress_callback: Optional[Callable[[int, Optional[int]], None]] = None,
    ) -> None:
        """Download a file by ID to destination path with progress callback.

        Args:
            file_id: The ID of the file to download.
            dest_path: Local file path to save downloaded content.
            progress_callback: Callable taking (bytes_downloaded, total_bytes).
        """
        url = f"{self.dl_base_url}/download/files/{file_id}"
        with self.http.client.stream("GET", url) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("Content-Length", 0)) or None
            downloaded = 0
            with open(dest_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)

    def upload(
        self,
        file_path: str,
        parent_id: Optional[str] = None,
        progress_callback: Optional[Callable[[int, Optional[int]], None]] = None,
    ) -> dict[str, Any]:
        """Upload a local file with progress callback.

        Args:
            file_path: Path to local file.
            parent_id: Optional destination folder ID.
            progress_callback: Callable taking (bytes_uploaded, total_bytes).

        Returns:
            API response dictionary for the uploaded file.
        """
        url = f"{self.upload_base_url}/upload/files"
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)

        with open(file_path, "rb") as f:
            files = {"file": (filename, f)}
            data = {}
            if parent_id:
                data["parentId"] = parent_id

            response = self.http.client.post(url, files=files, data=data)
            if progress_callback:
                progress_callback(file_size, file_size)
            res = self.http._handle_response(response)
            return dict(res) if isinstance(res, dict) else {}
