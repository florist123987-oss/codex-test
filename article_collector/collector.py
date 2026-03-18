from __future__ import annotations

import re
from datetime import datetime, timezone
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .db import ArticleRepository
from .errors import FetchError, ParseError
from .models import ArticleRecord

BLOCKLIST_TAGS = [
    "script",
    "style",
    "noscript",
    "iframe",
    "svg",
    "canvas",
    "form",
    "header",
    "footer",
    "nav",
    "aside",
]

DATE_META_KEYS = [
    "article:published_time",
    "og:published_time",
    "pubdate",
    "publishdate",
    "date",
    "datePublished",
]


class ArticleCollector:
    def __init__(self, timeout_seconds: int = 10, user_agent: str | None = None) -> None:
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent or "ArticleCollector/1.0"

    def collect(self, url: str) -> ArticleRecord:
        html = self._fetch_html(url)
        cleaned_html = self._remove_noise(html)

        title = self._extract_title(cleaned_html)
        content = self._extract_content(cleaned_html)
        author = self._extract_author(cleaned_html)
        published_at = self._extract_published_time(cleaned_html)

        return ArticleRecord(
            url=url,
            title=title,
            author=author,
            published_at=published_at,
            content=content,
            fetched_at=datetime.now(timezone.utc),
            raw_html=html,
        )

    def collect_and_save(self, url: str, repository: ArticleRepository) -> int:
        return repository.save_article(self.collect(url))

    def _fetch_html(self, url: str) -> str:
        req = Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urlopen(req, timeout=self.timeout_seconds) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    raise FetchError(f"Unsupported content type: {content_type}")
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset, errors="replace")
        except (HTTPError, URLError, TimeoutError) as exc:
            raise FetchError(f"Fetch failed for {url}: {exc}") from exc

    def _remove_noise(self, html: str) -> str:
        cleaned = html
        for tag in BLOCKLIST_TAGS:
            cleaned = re.sub(rf"(?is)<{tag}[^>]*>.*?</{tag}>", " ", cleaned)

        cleaned = re.sub(
            r'(?is)<[^>]+(?:class|id|role)=["\'][^"\']*(?:ad|ads|advert|sidebar|related|comment|share|social|footer|nav|menu)[^"\']*["\'][^>]*>.*?</[^>]+>',
            " ",
            cleaned,
        )
        return cleaned

    def _extract_title(self, html: str) -> str:
        patterns = [
            r'(?is)<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)',
            r'(?is)<meta[^>]+name=["\']twitter:title["\'][^>]+content=["\']([^"\']+)',
            r'(?is)<title[^>]*>(.*?)</title>',
            r'(?is)<h1[^>]*>(.*?)</h1>',
        ]
        for pattern in patterns:
            m = re.search(pattern, html)
            if m:
                value = self._clean_text(m.group(1))
                if value:
                    return value
        raise ParseError("Title not found")

    def _extract_author(self, html: str) -> str | None:
        patterns = [
            r'(?is)<meta[^>]+name=["\']author["\'][^>]+content=["\']([^"\']+)',
            r'(?is)<meta[^>]+property=["\']article:author["\'][^>]+content=["\']([^"\']+)',
            r'(?is)<meta[^>]+name=["\']twitter:creator["\'][^>]+content=["\']([^"\']+)',
            r'(?is)<[^>]+(?:class|id)=["\'][^"\']*(?:author|byline)[^"\']*["\'][^>]*>(.*?)</[^>]+>',
        ]
        for pattern in patterns:
            m = re.search(pattern, html)
            if m:
                cleaned = self._normalize_author(self._clean_text(m.group(1)))
                if cleaned:
                    return cleaned
        return None

    def _extract_published_time(self, html: str) -> str | None:
        for key in DATE_META_KEYS:
            pattern = rf'(?is)<meta[^>]+(?:property|name|itemprop)=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)'
            m = re.search(pattern, html)
            if m:
                return self._clean_text(m.group(1))

        tm = re.search(r'(?is)<time[^>]+datetime=["\']([^"\']+)', html)
        if tm:
            return self._clean_text(tm.group(1))

        tm_text = re.search(r'(?is)<time[^>]*>(.*?)</time>', html)
        if tm_text:
            return self._clean_text(tm_text.group(1))
        return None

    def _extract_content(self, html: str) -> str:
        root = self._first_group(r'(?is)<article[^>]*>(.*?)</article>', html)
        if not root:
            root = self._first_group(r'(?is)<main[^>]*>(.*?)</main>', html)
        if not root:
            root = self._first_group(r'(?is)<body[^>]*>(.*?)</body>', html)
        if not root:
            raise ParseError("No root content node found")

        matches = re.findall(r'(?is)<(?:p|h2|h3|blockquote|li)[^>]*>(.*?)</(?:p|h2|h3|blockquote|li)>', root)
        paragraphs: list[str] = []
        for part in matches:
            text = self._clean_text(part)
            if len(text) < 20:
                continue
            if self._looks_like_boilerplate(text):
                continue
            paragraphs.append(text)

        if len(paragraphs) < 3:
            fallback = self._clean_text(root)
            if len(fallback) < 200:
                raise ParseError("Extracted content too short")
            return fallback

        return "\n\n".join(paragraphs)

    @staticmethod
    def _first_group(pattern: str, html: str) -> str | None:
        m = re.search(pattern, html)
        return m.group(1) if m else None

    @staticmethod
    def _clean_text(raw: str) -> str:
        no_tags = re.sub(r"(?is)<[^>]+>", " ", raw)
        return re.sub(r"\s+", " ", unescape(no_tags)).strip()

    @staticmethod
    def _normalize_author(value: str) -> str:
        cleaned = re.sub(r"^(作者|编辑|By)[:：]\s*", "", value, flags=re.IGNORECASE)
        return cleaned.strip("@ ")

    @staticmethod
    def _looks_like_boilerplate(text: str) -> bool:
        lowered = text.lower()
        patterns = ["cookie", "版权所有", "privacy policy", "all rights reserved", "相关阅读", "订阅", "分享"]
        return any(p in lowered for p in patterns)
