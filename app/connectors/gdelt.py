"""GDELT DOC 2.0 connector. Fully open — no credentials required.

Searches global online news (~last 3 months) by keyword.
"""
from __future__ import annotations

import httpx

from .base import Connector, Post

BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


class GdeltConnector(Connector):
    key = "gdelt"
    display_name = "GDELT (Global News)"
    requires_credentials = False

    def is_configured(self) -> bool:
        return True

    async def fetch(self, keyword: str, limit: int = 25) -> list[Post]:
        params = {
            "query": keyword,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": min(max(limit, 1), 250),
            "sort": "datedesc",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                BASE_URL,
                params=params,
                headers={"User-Agent": "social-listening-tool/0.1"},
            )
            resp.raise_for_status()
            # GDELT sometimes returns empty body or non-JSON on no results.
            if not resp.text.strip():
                return []
            data = resp.json()

        posts: list[Post] = []
        for art in data.get("articles", []):
            title = art.get("title", "")
            if not title:
                continue
            posts.append(
                Post(
                    source=self.key,
                    external_id=art.get("url", title),
                    keyword=keyword,
                    content=title,
                    author=art.get("domain"),
                    url=art.get("url"),
                    published_at=art.get("seendate"),
                )
            )
        return posts
