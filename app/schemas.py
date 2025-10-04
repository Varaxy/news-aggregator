from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ArticleOut(BaseModel):
    id: str = Field(alias="_id")
    url: str
    title: str
    excerpt: Optional[str] = None
    image: Optional[str] = None
    authors: List[str] = []
    topics: List[str] = []
    lang: str = "en"
    publishedAt: datetime
    score: float = 0.0
