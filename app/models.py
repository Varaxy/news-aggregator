from datetime import datetime
from typing import Any, Dict

# Using plain dicts with Motor; indexes created in main at startup.
ARTICLE_INDEXES = [
    ({"urlHash": 1}, {"unique": True}),
    ({"publishedAt": -1}, {}),
    ({"topics": 1, "publishedAt": -1}, {}),
    ({"score": -1, "publishedAt": -1}, {}),
]

def article_doc():
    return {
        "url": "",
        "urlHash": "",
        "title": "",
        "excerpt": None,
        "text": None,
        "image": None,
        "authors": [],
        "source": None,  # e.g., {"name":"NYT","api":"NYT"}
        "apiName": None,
        "topics": [],
        "lang": "en",
        "publishedAt": datetime.utcnow(),
        "fetchedAt": datetime.utcnow(),
        "score": 0.0,
        "metrics": {"clicks": 0, "impressions": 0, "ctr": 0.0, "velocity": 0.0},
    }
