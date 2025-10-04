import os, httpx, re

TAG_RE = re.compile(r"<[^>]+>")

async def fetch_latest():
    key = os.getenv("GUARDIAN_KEY")
    if not key:
        return []
    url = "https://content.guardianapis.com/search"
    params = {"api-key": key, "show-fields": "trailText,thumbnail,byline,bodyText", "page-size": 50}
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    items = []
    for a in (data.get("response") or {}).get("results", []):
        trail = ((a.get("fields") or {}).get("trailText")) or ""
        items.append({
            "apiName": "Guardian",
            "source": {"name": "The Guardian", "api":"Guardian"},
            "url": a.get("webUrl"),
            "canonicalUrl": a.get("webUrl"),
            "title": a.get("webTitle"),
            "excerpt": TAG_RE.sub("", trail) if trail else None,
            "image": (a.get("fields") or {}).get("thumbnail"),
            "authors": [ (a.get("fields") or {}).get("byline") ] if (a.get("fields") or {}).get("byline") else [],
            "topics": [a.get("sectionName")] if a.get("sectionName") else [],
            "publishedAt": a.get("webPublicationDate"),
            "lang": "en",
        })
    return items
