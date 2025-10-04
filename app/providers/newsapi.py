import os, httpx

async def fetch_latest():
    key = os.getenv("NEWSAPI_KEY")
    if not key:
        return []
    url = "https://newsapi.org/v2/top-headlines"
    params = {"country": "us", "pageSize": 50, "apiKey": key}
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    items = []
    for a in data.get("articles", []):
        items.append({
            "apiName": "NewsAPI",
            "source": {"name": (a.get("source") or {}).get("name","NewsAPI"), "api":"NewsAPI"},
            "url": a.get("url"),
            "canonicalUrl": a.get("url"),
            "title": a.get("title"),
            "excerpt": a.get("description"),
            "image": a.get("urlToImage"),
            "authors": [a["author"]] if a.get("author") else [],
            "topics": [],
            "publishedAt": a.get("publishedAt"),
            "lang": "en",
        })
    return items
