"""YouTube id + local media payload — no Home Assistant imports."""

from __future__ import annotations

import json
import re
from typing import Any

_YT = re.compile(r"(?:youtu\.be/|/shorts/|/embed/|v=)([A-Za-z0-9_-]{6,})")


def youtube_id(raw: str | None) -> str | None:
    if not raw:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if re.fullmatch(r"[A-Za-z0-9_-]{6,}", s) and "://" not in s:
        return s
    m = _YT.search(s)
    if m:
        return m.group(1)
    return None


def media_payload(youtube: str | None, local: Any) -> tuple[str, Any] | None:
    vid = youtube_id(youtube)
    if vid:
        return "cast", json.dumps({"app_name": "youtube", "media_id": vid})
    if isinstance(local, dict):
        mid = local.get("media_content_id") or local.get("id")
        mtype = local.get("media_content_type") or local.get("media_class") or "video"
        if mid:
            return str(mtype), str(mid)
    if isinstance(local, str) and local.strip():
        path = local.strip()
        if path.startswith("media-source://") or path.startswith("/"):
            lower = path.lower()
            if lower.endswith((".mp3", ".aac", ".wav", ".ogg", ".flac", ".m4a")):
                return "music", path
            return "video", path
    return None
