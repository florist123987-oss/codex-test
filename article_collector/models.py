from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ArticleRecord:
    url: str
    title: str
    content: str
    author: str | None = None
    published_at: str | None = None
    fetched_at: datetime | None = None
    raw_html: str | None = None
