from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Protocol

from .errors import PersistenceError
from .models import ArticleRecord


class ArticleRepository(Protocol):
    def save_article(self, article: ArticleRecord) -> int:
        """Persist article and return row id (or existing id)."""


class SQLiteArticleRepository:
    """SQLite adapter for existing `articles` table.

    Assumed schema (already exists in DB module):
      id INTEGER PRIMARY KEY
      url TEXT UNIQUE NOT NULL
      title TEXT NOT NULL
      author TEXT NULL
      published_at TEXT NULL
      content TEXT NOT NULL
      raw_html TEXT NULL
      fetched_at TEXT NOT NULL
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def save_article(self, article: ArticleRecord) -> int:
        article.fetched_at = article.fetched_at or datetime.now(timezone.utc)
        sql = """
        INSERT INTO articles (url, title, author, published_at, content, raw_html, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
          title=excluded.title,
          author=excluded.author,
          published_at=excluded.published_at,
          content=excluded.content,
          raw_html=excluded.raw_html,
          fetched_at=excluded.fetched_at
        """
        params = (
            article.url,
            article.title,
            article.author,
            article.published_at,
            article.content,
            article.raw_html,
            article.fetched_at.isoformat(),
        )

        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                conn.commit()
                if cur.lastrowid:
                    return int(cur.lastrowid)

                # On conflict update path: retrieve id by url.
                lookup = cur.execute("SELECT id FROM articles WHERE url = ?", (article.url,)).fetchone()
                if not lookup:
                    raise PersistenceError("Article persisted but could not read id back")
                return int(lookup[0])
        except sqlite3.Error as exc:
            raise PersistenceError(f"DB save failed: {exc}") from exc
