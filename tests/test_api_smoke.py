"""In-process smoke test of the API using FastAPI TestClient (no server, no net)."""
import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dashboard_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "Social Listening Tool" in r.text


def test_sources_listed():
    r = client.get("/api/sources")
    assert r.status_code == 200
    keys = {s["key"] for s in r.json()}
    assert {"reddit", "youtube", "bluesky", "mastodon", "gdelt", "newsapi"} == keys


def test_collect_handles_source_errors_gracefully(monkeypatch):
    """With no network, a source raises; the batch must still return 200
    with the error captured per-source rather than crashing."""

    async def boom(self, url, params=None, **kwargs):
        raise httpx.ConnectError("no network in test")

    monkeypatch.setattr(httpx.AsyncClient, "get", boom)
    r = client.post(
        "/api/collect",
        json={"keyword": "climate", "sources": ["gdelt"], "limit": 3},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["sources"]["gdelt"]["error"] is not None
    assert body["fetched_total"] == 0


def test_collect_rejects_unknown_source():
    r = client.post(
        "/api/collect",
        json={"keyword": "x", "sources": ["myspace"], "limit": 3},
    )
    assert r.status_code == 400
