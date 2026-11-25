"""Connector parsing tests using mocked HTTP responses (no network)."""
import httpx
import pytest

from app.connectors.bluesky import BlueskyConnector
from app.connectors.gdelt import GdeltConnector


@pytest.mark.asyncio
async def test_bluesky_parses_posts(monkeypatch):
    sample = {
        "posts": [
            {
                "uri": "at://did:plc:abc/app.bsky.feed.post/xyz",
                "author": {"handle": "alice.bsky.social", "displayName": "Alice"},
                "record": {"text": "hello climate world", "createdAt": "2026-01-01T00:00:00Z"},
            }
        ]
    }

    async def fake_get(self, url, params=None, **kwargs):
        return httpx.Response(200, json=sample, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    posts = await BlueskyConnector().fetch("climate", limit=5)
    assert len(posts) == 1
    assert posts[0].source == "bluesky"
    assert posts[0].author == "alice.bsky.social"
    assert posts[0].url == "https://bsky.app/profile/alice.bsky.social/post/xyz"
    assert "climate" in posts[0].content


@pytest.mark.asyncio
async def test_gdelt_parses_articles(monkeypatch):
    sample = {
        "articles": [
            {
                "url": "https://example.com/a",
                "title": "Climate news headline",
                "domain": "example.com",
                "seendate": "20260101T000000Z",
            }
        ]
    }

    async def fake_get(self, url, params=None, **kwargs):
        return httpx.Response(200, json=sample, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    posts = await GdeltConnector().fetch("climate", limit=5)
    assert len(posts) == 1
    assert posts[0].source == "gdelt"
    assert posts[0].url == "https://example.com/a"
