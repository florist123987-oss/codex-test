PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS contents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL CHECK (content_type IN ('article', 'video', 'file')),
    url TEXT UNIQUE,
    source_name TEXT,
    title TEXT NOT NULL,
    author TEXT,
    published_at TEXT,
    raw_content TEXT NOT NULL,
    cleaned_content TEXT,
    one_line_summary TEXT,
    language TEXT NOT NULL DEFAULT 'zh',
    extra_json TEXT,
    ingestion_status TEXT NOT NULL DEFAULT 'new' CHECK (ingestion_status IN ('new', 'parsed', 'summarized')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS content_key_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    point_order INTEGER NOT NULL,
    point_text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE,
    UNIQUE (content_id, point_order)
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS content_tags (
    content_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (content_id, tag_id),
    FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_contents_published_at ON contents(published_at);
CREATE INDEX IF NOT EXISTS idx_contents_source_name ON contents(source_name);
CREATE INDEX IF NOT EXISTS idx_contents_ingestion_status ON contents(ingestion_status);
CREATE INDEX IF NOT EXISTS idx_key_points_content_id ON content_key_points(content_id);
CREATE INDEX IF NOT EXISTS idx_content_tags_tag_id ON content_tags(tag_id);

CREATE TRIGGER IF NOT EXISTS trg_contents_updated_at
AFTER UPDATE ON contents
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE contents
    SET updated_at = datetime('now')
    WHERE id = OLD.id;
END;
