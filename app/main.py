
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .db import get_db
from .routes import r as api_router
from .ingest import run_ingest_once
from .models import ARTICLE_INDEXES
from .bootstrap import ensure_demo_docs

app = FastAPI(title="News Aggregator (FastAPI + MongoDB)")
app.include_router(api_router)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def on_startup():
    db = await get_db()
    # Ensure indexes
    for keys, opts in ARTICLE_INDEXES:
        await db.articles.create_index(keys, **opts)

    # If DB is empty, insert demo docs (so UI isn't blank on first run)
    await ensure_demo_docs(db)

    # initial ingest + scheduler
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(run_ingest_once, "interval", minutes=10, id="ingest")
    scheduler.start()
    await run_ingest_once()
