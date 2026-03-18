# 文章采集模块（v1）

## 快速调用

```python
from article_collector import ArticleCollector, SQLiteArticleRepository

collector = ArticleCollector(timeout_seconds=10)
repo = SQLiteArticleRepository(db_path="app.db")
article_id = collector.collect_and_save("https://example.com/post/1", repo)
```

## 数据库字段假设

模块默认对接已有 `articles` 表，字段如下（不做迁移）：

- `id` INTEGER PRIMARY KEY
- `url` TEXT UNIQUE NOT NULL
- `title` TEXT NOT NULL
- `author` TEXT NULL
- `published_at` TEXT NULL
- `content` TEXT NOT NULL
- `raw_html` TEXT NULL
- `fetched_at` TEXT NOT NULL

> 若你的数据库字段名不同，请在数据库模块里实现 `ArticleRepository` 协议即可。
