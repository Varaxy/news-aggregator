import feedparser
from datetime import datetime, timezone

# Each feed paired with a category you want to show as a button
FEEDS = [
    ("http://feeds.bbci.co.uk/news/world/rss.xml", "world"),
    ("https://www.reddit.com/r/worldnews/.rss", "world"),
    ("https://feeds.bbci.co.uk/news/technology/rss.xml", "tech"),
    ("https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "science"),
    ("https://feeds.bbci.co.uk/news/business/rss.xml", "business"),
    ("https://www.espn.com/espn/rss/news", "sports"),
]

def _pick_date(e):
    # prefer published, fall back to updated, else now UTC
    for key in ("published", "updated"):
        v = getattr(e, key, None)
        if v:
            return v
    return datetime.now(timezone.utc).isoformat()

async def fetch_latest():
    items = []
    for url, category in FEEDS:
        f = feedparser.parse(url)
        for e in f.entries[:50]:
            link = getattr(e, "link", None)
            if not link: 
                continue
            items.append({
                "apiName": "RSS",
                "source": {"name": "RSS", "api": "RSS"},
                "url": link, "canonicalUrl": link,
                "title": getattr(e, "title", "(untitled)"),
                "excerpt": getattr(e, "summary", None),
                "image": None,
                "authors": [],
                "topics": [category],
                "publishedAt": _pick_date(e),
                "lang": "en",
            })
    return items