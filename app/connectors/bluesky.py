"""Bluesky connector via the AT Protocol AppView.

Public post search works WITHOUT credentials against api.bsky.app.
Note (verified 2026): unauthenticated search only returns the first page;
cursor pagination returns 403. So without credentials we fetch one page only.
"""
from __future__ import annotations

import httpx

from ..config import settings
from .base import Connector, Post

# Public AppView host that serves unauthenticated searchPosts.
PUBLIC_HOST = "https://api.bsky.app"
SEARCH_PATH = "/xrpc/app.bsky.feed.searchPosts"


class BlueskyConnector(Connector):
    key = "bluesky"
    display_name = "Bluesky"
    requires_credentials = False  # public search works keyless

    def is_configured(self) -> bool:
        # Always usable: public read works without credentials.
        return True

    async def fetch(self, keyword: str, limit: int = 25) -> list[Post]:
        params = {"q": keyword, "limit": min(max(limit, 1), 100)}
        url = f"{PUBLIC_HOST}{SEARCH_PATH}"
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        posts: list[Post] = []
        for item in data.get("posts", []):
            record = item.get("record", {}) or {}
            author = item.get("author", {}) or {}
            text = record.get("text", "")
            if not text:
                continue
            uri = item.get("uri", "")
            # Build a web URL: at://did/app.bsky.feed.post/rkey -> bsky.app link
            handle = author.get("handle", "")
            rkey = uri.rsplit("/", 1)[-1] if uri else ""
            web_url = (
                f"https://bsky.app/profile/{handle}/post/{rkey}"
                if handle and rkey
                else None
            )
            posts.append(
                Post(
                    source=self.key,
                    external_id=uri or text[:60],
                    keyword=keyword,
                    content=text,
                    author=handle or author.get("displayName"),
                    url=web_url,
                    published_at=record.get("createdAt"),
                )
            )
        return posts
