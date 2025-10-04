# News Aggregator (FastAPI + MongoDB)

Python web app that ingests articles from multiple news APIs, stores them in MongoDB,
and serves `/feed`, `/trending`, and `/search` endpoints with a tiny web UI.

## Quick start (Docker)
```bash
cp .env.example .env   # fill in keys if you have them
docker compose up --build
# open http://localhost:8000
```

## Quick start (local dev)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # edit MONGO_URI if using Atlas
uvicorn app.main:app --reload
```

### Endpoints
- `GET /api/trending?topic=&hours=48&limit=50`
- `GET /api/feed?topic=&limit=50`
- `GET /api/search?q=keyword&limit=50`
- `POST /api/click/{article_id}`

### Notes
- Uses APScheduler to fetch periodically (every 10 minutes by default).
- Dedupes using a `urlHash` unique index.
- Search uses simple regex by default; upgrade to Atlas Search later.
