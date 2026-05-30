# Local development

## Prerequisites

- Python 3.x (already required for `fetch_events.py`)
- A Ticketmaster API key (for refreshing data)

## Viewing the site

The site is plain HTML/CSS/JS with no build step. Start any local HTTP server from the repo root:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000 in your browser.

> You must use a server (not `file://`) because the page fetches `data/events.json` via `fetch()`.

## Refreshing event data

Copy `.env.example` to `.env` and add your API key:

```bash
cp .env.example .env
# edit .env and set TICKETMASTER_API_KEY=...
```

Then run:

```bash
uv run fetch_events.py
```

This overwrites `data/events.json`. Reload the browser to see updated events.

## Deploying

- **Cloudflare Pages**: no build command, output directory `/`
- **GitHub Pages**: push to your configured branch; `.nojekyll` is already in the repo
