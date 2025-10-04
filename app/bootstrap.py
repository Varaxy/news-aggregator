
from datetime import datetime, timezone, timedelta
import hashlib

def _h(s: str) -> str:
    return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()

DEMO_DOCS = [
    {
        "url": "https://example.com/demo-1",
        "urlHash": _h("https://example.com/demo-1"),
        "title": "Welcome to your News Aggregator",
        "excerpt": "This is a demo article inserted automatically because no API keys were found.",
        "text": None,
        "image": None,
        "authors": ["System"],
        "source": {"name":"Bootstrap","api":"Seed"},
        "apiName": "Seed",
        "topics": ["demo","getting-started"],
        "lang": "en",
        "publishedAt": datetime.now(timezone.utc) - timedelta(hours=1),
        "fetchedAt": datetime.now(timezone.utc),
        "score": 0.95,
        "metrics": {"clicks": 0, "impressions": 0, "ctr": 0.0, "velocity": 0.0},
    },
    {
        "url": "https://example.com/demo-2",
        "urlHash": _h("https://example.com/demo-2"),
        "title": "Tip: Add RSS to ingest real headlines without keys",
        "excerpt": "Open app/providers/rss.py and customize FEEDS to your favorite sites.",
        "text": None,
        "image": None,
        "authors": ["System"],
        "source": {"name":"Bootstrap","api":"Seed"},
        "apiName": "Seed",
        "topics": ["demo","tips"],
        "lang": "en",
        "publishedAt": datetime.now(timezone.utc) - timedelta(hours=5),
        "fetchedAt": datetime.now(timezone.utc),
        "score": 0.85,
        "metrics": {"clicks": 0, "impressions": 0, "ctr": 0.0, "velocity": 0.0},
    },
]

async def ensure_demo_docs(db):
    count = await db.articles.estimated_document_count()
    if count and count > 0:
        return 0
    # insert demo docs if empty
    inserted = 0
    for d in DEMO_DOCS:
        res = await db.articles.update_one({"urlHash": d["urlHash"]}, {"$setOnInsert": d}, upsert=True)
        if res.upserted_id is not None:
            inserted += 1
    return inserted
