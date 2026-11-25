"""SQLite storage for collected posts."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT NOT NULL,
    external_id     TEXT NOT NULL,
    keyword         TEXT NOT NULL,
    author          TEXT,
    content         TEXT NOT NULL,
    url             TEXT,
    published_at    TEXT,
    collected_at    TEXT NOT NULL DEFAULT (datetime('now')),
    sentiment_score REAL,
    sentiment_label TEXT,
    UNIQUE(source, external_id, keyword)
);
CREATE INDEX IF NOT EXISTS idx_posts_keyword ON posts(keyword);
CREATE INDEX IF NOT EXISTS idx_posts_source ON posts(source);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def insert_posts(posts: list[dict]) -> int:
    """Insert posts, skipping duplicates. Returns number of new rows."""
    if not posts:
        return 0
    inserted = 0
    with get_connection() as conn:
        for p in posts:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO posts
                    (source, external_id, keyword, author, content, url,
                     published_at, sentiment_score, sentiment_label)
                VALUES
                    (:source, :external_id, :keyword, :author, :content, :url,
                     :published_at, :sentiment_score, :sentiment_label)
                """,
                p,
            )
            inserted += cur.rowcount
    return inserted


def query_posts(
    keyword: str | None = None,
    source: str | None = None,
    sentiment: str | None = None,
    limit: int = 200,
) -> list[dict]:
    clauses = []
    params: list = []
    if keyword:
        clauses.append("keyword = ?")
        params.append(keyword)
    if source:
        clauses.append("source = ?")
        params.append(source)
    if sentiment:
        clauses.append("sentiment_label = ?")
        params.append(sentiment)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = (
        f"SELECT * FROM posts {where} "
        f"ORDER BY COALESCE(published_at, collected_at) DESC LIMIT ?"
    )
    params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def summary(keyword: str | None = None) -> dict:
    """Aggregate counts by source and sentiment."""
    where = "WHERE keyword = ?" if keyword else ""
    params = [keyword] if keyword else []
    with get_connection() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) AS c FROM posts {where}", params
        ).fetchone()["c"]
        by_source = conn.execute(
            f"SELECT source, COUNT(*) AS c FROM posts {where} "
            f"GROUP BY source ORDER BY c DESC",
            params,
        ).fetchall()
        by_sentiment = conn.execute(
            f"SELECT sentiment_label AS label, COUNT(*) AS c FROM posts {where} "
            f"GROUP BY sentiment_label",
            params,
        ).fetchall()
    return {
        "total": total,
        "by_source": {r["source"]: r["c"] for r in by_source},
        "by_sentiment": {r["label"]: r["c"] for r in by_sentiment},
    }
