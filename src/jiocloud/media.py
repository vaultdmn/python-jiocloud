"""Media streaming and auth service for JioCloud audio/video files."""

from jiocloud._http import JioCloudHTTPClient


class MediaService:
    """Manages media streaming URL authentication and access tracking."""

    def __init__(self, http: JioCloudHTTPClient) -> None:
        self.http = http
        self.api_base_url = "https://jaws-api.jioaicloud.com"
        self.web_base_url = "https://www.jioaicloud.com"

    def get_stream_url(self, object_key: str, vdc: str = "jaws") -> str:
        """Fetch authenticated streaming URL for a media object (video/audio/image).

        Args:
            object_key: The file object key / ID.
            vdc: Virtual data center code (default "jaws").

        Returns:
            Authenticated stream URL string (e.g., HLS playlist or direct stream URL).
        """
        access_date_url = f"{self.api_base_url}/nms/metadata/accessdate/{object_key}"
        try:
            self.http.put(access_date_url, json={})
        except Exception:
            pass

        auth_url = f"{self.web_base_url}/jaws/nms/media/auth"
        params = {
            "objectKey": object_key,
            "vdc": vdc,
            "apiKey": self.http.api_key,
        }
        response = self.http.get(auth_url, params=params)
        if isinstance(response, str):
            return response
        elif isinstance(response, dict):
            return str(
                response.get("url") or response.get("streamUrl") or response.get("data") or ""
            )
        return str(response)
