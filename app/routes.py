from fastapi import APIRouter
from typing import Optional
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from .db import get_db

r = APIRouter(prefix="/api", tags=["articles"])

def _to_out(d: dict) -> dict:
    d = dict(d)
    d["_id"] = str(d["_id"])
    return d

@r.get("/trending")
async def trending(
    topic: Optional[str] = None,
    lang: Optional[str] = "en",
    hours: int = 48,
    skip: int = 0,
    limit: int = 30
):
    db = await get_db()
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    q = {"publishedAt": {"$gte": since}}
    if topic: q["topics"] = topic
    if lang: q["lang"] = lang
    cursor = db.articles.find(q).sort([("score",-1), ("publishedAt",-1)]).skip(int(skip)).limit(int(limit))
    return [_to_out(x) async for x in cursor]

@r.get("/feed")
async def feed(
    topic: Optional[str] = None,
    lang: Optional[str] = "en",
    skip: int = 0,
    limit: int = 30
):
    db = await get_db()
    q = {}
    if topic: q["topics"] = topic
    if lang: q["lang"] = lang
    cursor = db.articles.find(q).sort("publishedAt", -1).skip(int(skip)).limit(int(limit))
    return [_to_out(x) async for x in cursor]

@r.get("/search")
async def search(q: str, skip: int = 0, limit: int = 30):
    db = await get_db()
    if not q.strip():
        return []
    cursor = db.articles.find({
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"excerpt": {"$regex": q, "$options": "i"}}
        ]
    }).sort("publishedAt", -1).skip(int(skip)).limit(int(limit))
    return [_to_out(x) async for x in cursor]

@r.post("/click/{article_id}")
async def click(article_id: str):
    db = await get_db()
    try:
        _id = ObjectId(article_id)
    except Exception:
        return {"ok": False}
    await db.articles.update_one({"_id": _id}, {"$inc": {"metrics.clicks": 1}})
    return {"ok": True}

@r.get("/categories")
async def categories(limit: int = 12):
    """
    Returns [{ name: 'world', count: 123 }, ...] sorted by recent frequency.
    """
    db = await get_db()
    pipeline = [
        {"$match": {"topics": {"$exists": True, "$ne": []}}},
        {"$unwind": "$topics"},
        {"$group": {"_id": "$topics", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": int(limit)},
        {"$project": {"_id": 0, "name": "$_id", "count": 1}}
    ]
    return [d async for d in db.articles.aggregate(pipeline)]

@r.get("/debug/stats")
async def debug_stats(days: int = 14):
    """
    Returns totals, latest publish date, counts by topic and by day.
    """
    from datetime import datetime, timedelta, timezone
    db = await get_db()
    since = datetime.now(timezone.utc) - timedelta(days=int(days))

    # Totals
    total = await db.articles.estimated_document_count()
    latest_doc = await db.articles.find().sort("publishedAt", -1).limit(1).to_list(1)
    latest_published_at = latest_doc[0]["publishedAt"] if latest_doc else None

    # By topic (all time)
    by_topic = []
    async for d in db.articles.aggregate([
        {"$unwind": "$topics"},
        {"$group": {"_id": "$topics", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
        {"$project": {"_id": 0, "topic": "$_id", "count": 1}}
    ]):
        by_topic.append(d)

    # By day (last N days)
    by_day = []
    async for d in db.articles.aggregate([
        {"$match": {"publishedAt": {"$gte": since}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$publishedAt"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "day": "$_id", "count": 1}}
    ]):
        by_day.append(d)

    # By source (optional, top 10)
    by_source = []
    async for d in db.articles.aggregate([
        {"$group": {"_id": "$source.name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "source": "$_id", "count": 1}}
    ]):
        by_source.append(d)

    return {
        "total": total,
        "latestPublishedAt": latest_published_at,
        "byTopic": by_topic,
        "byDay": by_day,
        "bySource": by_source,
    }
