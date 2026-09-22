"""Typed data models for JioCloud files and folders."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class JioFile:
    """Represents a file in JioCloud."""

    id: str
    name: str
    size: int
    parent_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    mime_type: Optional[str] = None
    raw: Optional[dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JioFile":
        """Create JioFile from API response dictionary."""
        return cls(
            id=data.get("fileId") or data.get("id") or "",
            name=data.get("name") or data.get("nm") or "",
            size=int(data.get("size") or data.get("sz") or 0),
            parent_id=data.get("parentId") or data.get("pid"),
            created_at=data.get("creationTime") or data.get("createdAt"),
            updated_at=data.get("modifiedTime") or data.get("updatedAt"),
            mime_type=data.get("mimeType") or data.get("mimetype"),
            raw=data,
        )


@dataclass
class JioFolder:
    """Represents a folder in JioCloud."""

    id: str
    name: str
    parent_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    raw: Optional[dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JioFolder":
        """Create JioFolder from API response dictionary."""
        return cls(
            id=data.get("folderId") or data.get("id") or "",
            name=data.get("name") or data.get("nm") or "",
            parent_id=data.get("parentId") or data.get("pid"),
            created_at=data.get("creationTime") or data.get("createdAt"),
            updated_at=data.get("modifiedTime") or data.get("updatedAt"),
            raw=data,
        )
