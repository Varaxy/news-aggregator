# 🗞️ News Aggregator

A **full-stack news aggregation web app** built with **FastAPI + MongoDB + Vanilla JS**.  
It collects, stores, and displays fresh articles from multiple sources with **search, category filtering, infinite scroll, and dark/light mode**.

---

## 🚀 Features

- **Backend (FastAPI + MongoDB Atlas)**
  - REST API endpoints for trending, search, categories, and ingestion.
  - Stores thousands of articles with metadata (`title`, `excerpt`, `url`, `topics`, `publishedAt`, etc.).
  - Ingestion pipeline parses RSS feeds and APIs, scoring articles by freshness and relevance.
  - Admin routes for manual refresh and health monitoring.

- **Frontend (HTML + CSS + JS)**
  - Clean UI with **infinite scroll** for loading articles.
  - **Dynamic category chips** powered by MongoDB aggregation.
  - **Search bar + reset button** for full-text search across titles and excerpts.
  - **↻ Refresh button** to fetch the latest news instantly.

- **Architecture**
  - Asynchronous database access with Motor.
  - MongoDB indexes for fast queries and text search.
  - Ready for deployment with Docker / Render / Fly.io.


## ⚡ API Endpoints

| Endpoint              | Method | Description                                |
|-----------------------|--------|--------------------------------------------|
| `/api/trending`       | GET    | Get trending articles (default last 12h)   |
| `/api/search?q=term`  | GET    | Search articles by keyword                 |
| `/api/categories`     | GET    | Top categories with counts                 |
| `/api/admin/ingest`   | POST   | Trigger ingestion of latest feeds          |
| `/api/health`         | GET    | DB health + total count of articles        |

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11+, Motor (MongoDB async driver)
- **Database**: MongoDB Atlas
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Other**: Uvicorn, Jinja2 templates

---

## 🏗️ Setup & Run Locally

1. **Clone repo**
   ```bash
   git clone https://github.com/your-username/news-aggregator.git
   cd news-aggregator
