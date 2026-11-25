"""Collection orchestration: fetch from sources, score, and store."""
from __future__ import annotations

import asyncio

from . import database, sentiment
from .connectors import CONNECTORS, Post


async def _fetch_one(source: str, keyword: str, limit: int) -> tuple[str, list[Post], str | None]:
    connector = CONNECTORS[source]
    try:
        posts = await connector.fetch(keyword, limit=limit)
        return source, posts, None
    except Exception as exc:  # surface per-source errors without failing the batch
        return source, [], f"{type(exc).__name__}: {exc}"


async def collect(keyword: str, sources: list[str], limit: int = 25) -> dict:
    """Fetch from each requested source concurrently, score sentiment, store.

    Returns a per-source report with counts and any errors.
    """
    keyword = keyword.strip()
    if not keyword:
        raise ValueError("keyword must not be empty")

    unknown = [s for s in sources if s not in CONNECTORS]
    if unknown:
        raise ValueError(f"Unknown source(s): {', '.join(unknown)}")

    results = await asyncio.gather(
        *(_fetch_one(s, keyword, limit) for s in sources)
    )

    report: dict[str, dict] = {}
    all_rows: list[dict] = []
    for source, posts, error in results:
        for p in posts:
            score, label = sentiment.analyze(p.content)
            p.sentiment_score = score
            p.sentiment_label = label
            all_rows.append(p.as_row())
        report[source] = {
            "fetched": len(posts),
            "error": error,
        }

    new_count = database.insert_posts(all_rows)
    return {
        "keyword": keyword,
        "sources": report,
        "fetched_total": len(all_rows),
        "new_stored": new_count,
    }
