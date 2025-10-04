import os, httpx

async def fetch_latest():
    key = os.getenv("NYT_KEY")
    if not key:
        return []
    url = "https://api.nytimes.com/svc/topstories/v2/home.json"
    params = {"api-key": key}
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    items = []
    for a in data.get("results", []):
        img = None
        mm = a.get("multimedia") or []
        if mm:
            img = mm[0].get("url")
        items.append({
            "apiName": "NYT",
            "source": {"name": "The New York Times", "api":"NYT"},
            "url": a.get("url"),
            "canonicalUrl": a.get("url"),
            "title": a.get("title"),
            "excerpt": a.get("abstract"),
            "image": img,
            "authors": [a["byline"]] if a.get("byline") else [],
            "topics": a.get("des_facet") or [],
            "publishedAt": a.get("published_date"),
            "lang": "en",
        })
    return items
