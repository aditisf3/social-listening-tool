# Social Listening Tool

A working prototype for keyword-based social listening. Enter a keyword, pick
one or more sources, and the app collects real public posts/articles through
**official APIs**, stores them in **SQLite**, runs **basic sentiment analysis**
(VADER), and shows everything in a **dashboard**.

One connector per source — no generic scraper.

## Sources

| Source    | Credentials | Notes |
|-----------|-------------|-------|
| **Reddit**   | Required | OAuth script app (client id + secret). Start here. |
| **YouTube**  | Required | YouTube Data API v3 key. |
| **News API** | Required | newsapi.org key. |
| **Bluesky**  | Not required | Public post search via the AT Protocol AppView (`api.bsky.app`). Works keyless — good for testing. |
| **GDELT**    | Not required | Open DOC 2.0 global-news API. Works keyless — good for testing. |
| **Mastodon** | Not required | Public hashtag timeline (keyless). A token enables full-text search. |

**Test without any credentials:** select **Bluesky**, **GDELT**, and/or
**Mastodon**. **Reddit** is pre-selected in the UI but needs a key to return data.

## Quick start

```bash
# 1. Create the virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Set up your credentials (keys stay local — .env is gitignored)
cp .env.example .env
# edit .env and fill in keys for the sources you want (optional for keyless ones)

# 3. Run the app
uvicorn app.main:app --reload

# 4. Open the dashboard
#    http://127.0.0.1:8000
```

> **Network note:** collection calls out to real external APIs, so run it on a
> machine with open internet. (It will not fetch live data from a restricted
> network/sandbox.)

## How to get keys

- **Reddit** — https://www.reddit.com/prefs/apps → create an app of type
  **script** → copy the client id and secret into `.env`.
- **YouTube** — https://console.cloud.google.com/apis/credentials → enable
  *YouTube Data API v3* → create an API key → `YOUTUBE_API_KEY`.
- **News API** — https://newsapi.org/register → copy the key → `NEWSAPI_KEY`.
- **Mastodon / Bluesky** — optional; only needed for higher limits or
  authenticated endpoints.

Keys live only in your local `.env`. **Never commit `.env`** — it is gitignored.

## API

| Method | Path            | Purpose |
|--------|-----------------|---------|
| GET    | `/`             | Dashboard |
| GET    | `/api/sources`  | List sources + whether each is configured |
| POST   | `/api/collect`  | `{ "keyword", "sources": [...], "limit" }` → fetch, score, store |
| GET    | `/api/posts`    | Stored posts, filter by `keyword` / `source` / `sentiment` |
| GET    | `/api/summary`  | Counts by source and sentiment |

## Project layout

```
app/
  main.py            FastAPI app + routes
  config.py          Settings loaded from .env
  database.py        SQLite schema, insert, query, summary
  sentiment.py       VADER sentiment scoring
  collector.py       Orchestrates fetch -> score -> store (concurrent)
  connectors/        One module per source
    base.py            Connector base + normalized Post
    reddit.py  youtube.py  newsapi.py
    bluesky.py mastodon.py gdelt.py
  static/            Dashboard (index.html, style.css, app.js)
tests/               pytest suite (sentiment, connector parsing, API smoke)
```

## Deploy to Render (live website)

This repo includes a `render.yaml` blueprint, so deploying gives you a public
URL with almost no config.

1. Sign up / log in at https://render.com with your GitHub account.
2. **New → Blueprint**, pick the `social-listening-tool` repo, and approve.
   Render reads `render.yaml` and sets up the web service automatically.
3. Click **Apply / Create**. After ~2–3 minutes you get a public URL like
   `https://social-listening-tool.onrender.com`.

The keyless sources (**Bluesky, GDELT, Mastodon**) work on the live site with no
further setup. To enable **Reddit / YouTube / News API**, add their keys as
environment variables in the Render dashboard (Service → **Environment**).

> **Free-tier notes:** the service sleeps after inactivity (first request after
> idle takes a few seconds to wake), and the SQLite file lives on an *ephemeral*
> disk, so stored results reset on restart/redeploy. For persistent storage,
> add a Render Postgres database (a later upgrade).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests mock all HTTP, so they run offline and don't touch real APIs.

## Status / next steps

This is a functional first version. Natural extensions:
- Comments/replies in addition to top-level posts.
- Scheduled/periodic collection instead of on-demand only.
- Trend-over-time charts in the dashboard.
- Swap VADER for a transformer model for better sentiment on short/social text.
