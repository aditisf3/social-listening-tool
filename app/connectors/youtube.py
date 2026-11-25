"""YouTube connector using the YouTube Data API v3 search endpoint.

Requires YOUTUBE_API_KEY. Returns matching videos (title + description).
"""
from __future__ import annotations

import httpx

from ..config import settings
from .base import Connector, Post

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


class YouTubeConnector(Connector):
    key = "youtube"
    display_name = "YouTube"
    requires_credentials = True

    def is_configured(self) -> bool:
        return bool(settings.youtube_api_key)

    async def fetch(self, keyword: str, limit: int = 25) -> list[Post]:
        if not self.is_configured():
            raise RuntimeError(
                "YouTube connector is not configured. Set YOUTUBE_API_KEY "
                "in your .env file."
            )
        params = {
            "key": settings.youtube_api_key,
            "q": keyword,
            "part": "snippet",
            "type": "video",
            "order": "date",
            "maxResults": min(max(limit, 1), 50),
        }
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        posts: list[Post] = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {}) or {}
            video_id = (item.get("id", {}) or {}).get("videoId")
            title = snippet.get("title", "")
            description = snippet.get("description", "") or ""
            content = f"{title}\n\n{description}".strip()
            if not content or not video_id:
                continue
            posts.append(
                Post(
                    source=self.key,
                    external_id=video_id,
                    keyword=keyword,
                    content=content,
                    author=snippet.get("channelTitle"),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    published_at=snippet.get("publishedAt"),
                )
            )
        return posts
