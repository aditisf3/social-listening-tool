"""News API connector (newsapi.org) /v2/everything endpoint.

Requires NEWSAPI_KEY.
"""
from __future__ import annotations

import httpx

from ..config import settings
from .base import Connector, Post

URL = "https://newsapi.org/v2/everything"


class NewsApiConnector(Connector):
    key = "newsapi"
    display_name = "News API"
    requires_credentials = True

    def is_configured(self) -> bool:
        return bool(settings.newsapi_key)

    async def fetch(self, keyword: str, limit: int = 25) -> list[Post]:
        if not self.is_configured():
            raise RuntimeError(
                "News API connector is not configured. Set NEWSAPI_KEY "
                "in your .env file."
            )
        params = {
            "q": keyword,
            "pageSize": min(max(limit, 1), 100),
            "sortBy": "publishedAt",
            "language": "en",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                URL,
                params=params,
                headers={"X-Api-Key": settings.newsapi_key},
            )
            resp.raise_for_status()
            data = resp.json()

        posts: list[Post] = []
        for art in data.get("articles", []):
            title = art.get("title", "") or ""
            description = art.get("description", "") or ""
            content = f"{title}\n\n{description}".strip()
            if not content:
                continue
            source_name = (art.get("source", {}) or {}).get("name")
            posts.append(
                Post(
                    source=self.key,
                    external_id=art.get("url", title),
                    keyword=keyword,
                    content=content,
                    author=art.get("author") or source_name,
                    url=art.get("url"),
                    published_at=art.get("publishedAt"),
                )
            )
        return posts
