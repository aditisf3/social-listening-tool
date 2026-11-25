"""FastAPI application: collection API + dashboard."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import collector, database
from .connectors import available_sources

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="Social Listening Tool", version="0.1.0", lifespan=lifespan)


class CollectRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    sources: list[str] = Field(..., min_length=1)
    limit: int = Field(25, ge=1, le=100)


@app.get("/api/sources")
def get_sources() -> list[dict]:
    """List available sources and whether each is configured."""
    return available_sources()


@app.post("/api/collect")
async def post_collect(req: CollectRequest) -> dict:
    """Collect posts for a keyword from the chosen sources."""
    try:
        return await collector.collect(req.keyword, req.sources, req.limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/posts")
def get_posts(
    keyword: str | None = None,
    source: str | None = None,
    sentiment: str | None = Query(None, pattern="^(positive|neutral|negative)$"),
    limit: int = Query(200, ge=1, le=1000),
) -> list[dict]:
    """Return stored posts, filterable by keyword / source / sentiment."""
    return database.query_posts(keyword, source, sentiment, limit)


@app.get("/api/summary")
def get_summary(keyword: str | None = None) -> dict:
    """Aggregate counts by source and sentiment."""
    return database.summary(keyword)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# Serve the dashboard's static assets.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
