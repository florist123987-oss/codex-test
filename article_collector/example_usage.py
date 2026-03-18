"""Simple call example for article collector module."""

from article_collector import ArticleCollector, SQLiteArticleRepository


def run(url: str, db_path: str = "app.db") -> int:
    collector = ArticleCollector(timeout_seconds=10)
    repo = SQLiteArticleRepository(db_path=db_path)
    article_id = collector.collect_and_save(url, repo)
    return article_id


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m article_collector.example_usage <url> [db_path]")
        raise SystemExit(2)

    target_url = sys.argv[1]
    db = sys.argv[2] if len(sys.argv) > 2 else "app.db"
    saved_id = run(target_url, db)
    print(f"saved article id={saved_id}")
