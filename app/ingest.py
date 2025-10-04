
import os, hashlib
from datetime import datetime, timezone
from dateutil import parser as dtparser, tz
from .db import get_db
from . import models
from .providers import newsapi, nyt, guardian, rss

TZINFOS = {
    "UTC": tz.gettz("UTC"),
    "GMT": tz.gettz("UTC"),
    "EST": tz.gettz("America/New_York"),
    "EDT": tz.gettz("America/New_York"),
    "CST": tz.gettz("America/Chicago"),
    "CDT": tz.gettz("America/Chicago"),
    "MST": tz.gettz("America/Denver"),
    "MDT": tz.gettz("America/Denver"),
    "PST": tz.gettz("America/Los_Angeles"),
    "PDT": tz.gettz("America/Los_Angeles"),
} 

def sha256(s: str) -> str:
    return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()

def to_dt(val):
    """
    Parse various feed/API date strings and ALWAYS return an aware UTC datetime.
    """
    if isinstance(val, datetime):
        dt = val
    else:
        try:
            dt = dtparser.parse(val, tzinfos=TZINFOS)
        except Exception:
            return datetime.now(timezone.utc)

    if dt.tzinfo is None:
        # Assume UTC if no tz info
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt

def base_score(published_at: datetime, source_weight: float = 1.0, clicks: int = 0) -> float:
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    hours = max(0.5, (now - published_at).total_seconds() / 3600.0)
    import math
    decay = math.exp(-hours / 18.0)
    engagement = (clicks + 1) ** 0.2 - 1
    return 0.7 * decay + 0.25 * source_weight + 0.05 * engagement


def _resolve_providers():
    use_keys = any([os.getenv("NEWSAPI_KEY"), os.getenv("NYT_KEY"), os.getenv("GUARDIAN_KEY")])
    if use_keys:
        return [newsapi, nyt, guardian, rss]  # include RSS too
    else:
        return [rss]  # no keys? just RSS

async def run_ingest_once():
    db = await get_db()
    providers = _resolve_providers()

    batch = []
    for prov in providers:
        try:
            items = await prov.fetch_latest()
            batch.extend(items)
        except Exception as e:
            print("Provider error:", prov.__name__, e)

    inserted = 0
    for a in batch:
        url = a.get("canonicalUrl") or a.get("url")
        if not url:
            continue
        h = sha256(url)
        try:
            published = to_dt(a.get("publishedAt"))
        except Exception:
            published = datetime.now(timezone.utc)

        doc = models.article_doc()
        doc.update({
            "url": url,
            "urlHash": h,
            "title": a.get("title") or "(untitled)",
            "excerpt": (a.get("excerpt") or "")[:300] or None,
            "text": None,
            "image": a.get("image"),
            "authors": a.get("authors") or [],
            "source": a.get("source"),
            "apiName": a.get("apiName"),
            "topics": a.get("topics") or [],
            "lang": a.get("lang") or "en",
            "publishedAt": published,
            "fetchedAt": datetime.now(timezone.utc),
        })
        doc["score"] = base_score(doc["publishedAt"], 1.0, 0)

        try:
            res = await db.articles.update_one(
                {"urlHash": h},
                {"$setOnInsert": doc},
                upsert=True
            )
            if res.upserted_id is not None:
                inserted += 1
        except Exception:
            pass
    return inserted
def _has_key(name: str) -> bool:
    val = os.getenv(name, "").strip()
    # treat pasted URLs or obvious placeholders as "no key"
    if not val:
        return False
    if "://" in val:
        return False
    if val.lower().startswith(("your_", "paste", "example")):
        return False
    return True

def _resolve_providers():
    use_newsapi = _has_key("NEWSAPI_KEY")
    use_nyt = _has_key("NYT_KEY")
    use_guardian = _has_key("GUARDIAN_KEY")

    from .providers import rss, newsapi, nyt, guardian  # local import to avoid unused if skipped
    providers = [rss]  # always keep RSS (no keys needed)
    if use_newsapi: providers.append(newsapi)
    if use_nyt: providers.append(nyt)
    if use_guardian: providers.append(guardian)
    return providers