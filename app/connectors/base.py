"""Connector base class and the normalized Post shape."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Post:
    """Normalized representation of a collected item across all sources."""

    source: str
    external_id: str
    keyword: str
    content: str
    author: str | None = None
    url: str | None = None
    published_at: str | None = None  # ISO 8601 string when available
    sentiment_score: float | None = None
    sentiment_label: str | None = None

    def as_row(self) -> dict:
        return {
            "source": self.source,
            "external_id": self.external_id,
            "keyword": self.keyword,
            "author": self.author,
            "content": self.content,
            "url": self.url,
            "published_at": self.published_at,
            "sentiment_score": self.sentiment_score,
            "sentiment_label": self.sentiment_label,
        }


class Connector:
    """Base class. Each source implements fetch()."""

    key: str = "base"
    display_name: str = "Base"
    requires_credentials: bool = True

    def is_configured(self) -> bool:
        """Whether this connector has what it needs to run."""
        return not self.requires_credentials

    async def fetch(self, keyword: str, limit: int = 25) -> list[Post]:
        raise NotImplementedError
