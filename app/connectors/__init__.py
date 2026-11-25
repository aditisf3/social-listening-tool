"""Source connectors. One connector per source — no generic scraper."""
from __future__ import annotations

from .base import Connector, Post
from .bluesky import BlueskyConnector
from .gdelt import GdeltConnector
from .mastodon import MastodonConnector
from .newsapi import NewsApiConnector
from .reddit import RedditConnector
from .youtube import YouTubeConnector

# Registry: source key -> connector instance
CONNECTORS: dict[str, Connector] = {
    "reddit": RedditConnector(),
    "youtube": YouTubeConnector(),
    "bluesky": BlueskyConnector(),
    "mastodon": MastodonConnector(),
    "gdelt": GdeltConnector(),
    "newsapi": NewsApiConnector(),
}


def available_sources() -> list[dict]:
    """List sources with metadata for the UI."""
    return [
        {
            "key": key,
            "name": c.display_name,
            "requires_credentials": c.requires_credentials,
            "configured": c.is_configured(),
        }
        for key, c in CONNECTORS.items()
    ]
