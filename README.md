# Signal Desk — Social Listening Prototype

A static front-end prototype for a social listening dashboard ("Signal Desk").
This is the **UI-first** starting point: it runs entirely in the browser on
**demo data**, with no backend and no API calls yet.

## What's here

A single self-contained file, `index.html`, containing the full prototype:

- **Signal Desk branding** and sidebar navigation
- **Overview** dashboard — metric cards, conversation-volume chart, topic
  breakdown, independent voices, early marketing takeaway
- **Conversations** feed — table of example mentions, filtered by source
- **Competitors** — share-of-conversation comparison
- **Trends** — six-month sample chart
- **Report** — draft marketing report
- Data-source toggles (**Bluesky · RSS · CSV**), charts, cards, filters,
  buttons, and responsive styling
- **Demo data** drives everything; buttons show toast placeholders where real
  functionality will be wired in later

## Run it locally

It's a static file — just open it:

```bash
# Option 1: open directly
open index.html          # macOS (or double-click the file)

# Option 2: serve it (any static server works)
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Deploy (Render static site)

This repo includes a `render.yaml` blueprint for a **static site**:

1. Log in at https://render.com with GitHub.
2. **New → Blueprint**, select this repo/branch, and apply.
3. Render serves `index.html` and gives you a public URL.

(Any static host works too — GitHub Pages, Netlify, Vercel — since it's just
one HTML file.)

## Roadmap (next steps)

The current build intentionally stops at a working UI on demo data. Planned
next:

1. Backend service to serve/collect data
2. Real data sources: **Reddit**, **Bluesky**, **RSS**
3. API credentials handling (kept out of git)
4. Sentiment analysis
5. Database persistence
6. Wire the Run / CSV upload / export buttons to the live pipeline
