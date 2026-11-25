"""Mastodon connector.

Reads public statuses from a Mastodon instance. Full-text search via the
/api/v2/search endpoint usually requires a token, so without one we fall back
to the public hashtag timeline (/api/v1/timelines/tag/{tag}), which is open.
"""
from __future__ import annotations

import re

import httpx

from ..config import settings
from .base import Connector, Post

_TAG_RE = re.compile(r"[^0-9a-zA-Z]+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(html: str) -> str:
    return _HTML_TAG_RE.sub("", html or "").strip()


class MastodonConnector(Connector):
    key = "mastodon"
    display_name = "Mastodon"
    requires_credentials = False  # public reads work without a token

    def is_configured(self) -> bool:
        return bool(settings.mastodon_instance)

    async def fetch(self, keyword: str, limit: int = 25) -> list[Post]:
        instance = settings.mastodon_instance.rstrip("/")
        token = settings.mastodon_access_token
        headers = {"User-Agent": "social-listening-tool/0.1"}
        limit = min(max(limit, 1), 40)

        async with httpx.AsyncClient(timeout=20) as client:
            if token:
                # Authenticated full-text search for statuses.
                headers["Authorization"] = f"Bearer {token}"
                resp = await client.get(
                    f"{instance}/api/v2/search",
                    params={"q": keyword, "type": "statuses", "limit": limit},
                    headers=headers,
                )
                resp.raise_for_status()
                statuses = resp.json().get("statuses", [])
            else:
                # Public hashtag timeline (keyless). Normalize keyword to a tag.
                tag = _TAG_RE.sub("", keyword)
                if not tag:
                    return []
                resp = await client.get(
                    f"{instance}/api/v1/timelines/tag/{tag}",
                    params={"limit": limit},
                    headers=headers,
                )
                resp.raise_for_status()
                statuses = resp.json()

        posts: list[Post] = []
        for s in statuses:
            content = _strip_html(s.get("content", ""))
            if not content:
                continue
            account = s.get("account", {}) or {}
            posts.append(
                Post(
                    source=self.key,
                    external_id=s.get("id", content[:60]),
                    keyword=keyword,
                    content=content,
                    author=account.get("acct") or account.get("username"),
                    url=s.get("url"),
                    published_at=s.get("created_at"),
                )
            )
        return posts
