# app/seed.py
import os, asyncio
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import hashlib

load_dotenv()
URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/newsagg")

def h(s: str) -> str:
    return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()

docs = [
    {
        "url": "https://example.com/article-1",
        "urlHash": h("https://example.com/article-1"),
        "title": "Demo: Breaking News One",
        "excerpt": "This is a seeded article to verify the UI and API.",
        "text": None,
        "image": None,
        "authors": ["Demo Author"],
        "source": {"name":"Seed","api":"Seed"},
        "apiName": "Seed",
        "topics": ["demo","world"],
        "lang": "en",
        "publishedAt": datetime.now(timezone.utc) - timedelta(hours=1),
        "fetchedAt": datetime.now(timezone.utc),
        "score": 0.9,
        "metrics": {"clicks": 0, "impressions": 0, "ctr": 0.0, "velocity": 0.0},
    },
    {
        "url": "https://example.com/article-2",
        "urlHash": h("https://example.com/article-2"),
        "title": "Demo: Technology Article",
        "excerpt": "Another seeded article for testing.",
        "text": None,
        "image": None,
        "authors": ["Demo Author 2"],
        "source": {"name":"Seed","api":"Seed"},
        "apiName": "Seed",
        "topics": ["tech"],
        "lang": "en",
        "publishedAt": datetime.now(timezone.utc) - timedelta(hours=5),
        "fetchedAt": datetime.now(timezone.utc),
        "score": 0.7,
        "metrics": {"clicks": 0, "impressions": 0, "ctr": 0.0, "velocity": 0.0},
    },
]

async def run():
    client = AsyncIOMotorClient(URI)
    db = client.get_default_database()
    if db is None:
        db = client["newsagg"]

    await db.articles.create_index("urlHash", unique=True)
    for d in docs:
        await db.articles.update_one(
            {"urlHash": d["urlHash"]},
            {"$setOnInsert": d},
            upsert=True
        )
    print("Seeded sample articles.")


if __name__ == "__main__":
    asyncio.run(run())
