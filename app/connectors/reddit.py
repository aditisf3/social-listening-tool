"""Reddit connector using the official OAuth API (script app, client credentials).

Requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET. Uses the application-only
OAuth flow (no user login) to search across subreddits.
"""
from __future__ import annotations

import httpx

from ..config import settings
from .base import Connector, Post

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
SEARCH_URL = "https://oauth.reddit.com/search"


class RedditConnector(Connector):
    key = "reddit"
    display_name = "Reddit"
    requires_credentials = True

    def is_configured(self) -> bool:
        return bool(settings.reddit_client_id and settings.reddit_client_secret)

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        auth = (settings.reddit_client_id, settings.reddit_client_secret)
        resp = await client.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=auth,
            headers={"User-Agent": settings.reddit_user_agent},
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    async def fetch(self, keyword: str, limit: int = 25) -> list[Post]:
        if not self.is_configured():
            raise RuntimeError(
                "Reddit connector is not configured. Set REDDIT_CLIENT_ID and "
                "REDDIT_CLIENT_SECRET in your .env file."
            )
        headers = {"User-Agent": settings.reddit_user_agent}
        async with httpx.AsyncClient(timeout=20) as client:
            token = await self._get_token(client)
            headers["Authorization"] = f"Bearer {token}"
            resp = await client.get(
                SEARCH_URL,
                params={
                    "q": keyword,
                    "limit": min(max(limit, 1), 100),
                    "sort": "new",
                    "type": "link",
                },
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        posts: list[Post] = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            title = d.get("title", "")
            body = d.get("selftext", "") or ""
            content = f"{title}\n\n{body}".strip()
            if not content:
                continue
            permalink = d.get("permalink", "")
            posts.append(
                Post(
                    source=self.key,
                    external_id=d.get("id", permalink),
                    keyword=keyword,
                    content=content,
                    author=d.get("author"),
                    url=f"https://www.reddit.com{permalink}" if permalink else None,
                    published_at=_epoch_to_iso(d.get("created_utc")),
                )
            )
        return posts


def _epoch_to_iso(epoch: float | None) -> str | None:
    if not epoch:
        return None
    from datetime import datetime, timezone

    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()
