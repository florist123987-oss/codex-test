PRAGMA foreign_keys = ON;

INSERT INTO contents (
    content_type,
    url,
    source_name,
    title,
    author,
    published_at,
    raw_content,
    cleaned_content,
    one_line_summary,
    ingestion_status,
    extra_json
) VALUES (
    'article',
    'https://example.com/articles/ai-notes',
    'Example Tech Blog',
    '如何高效构建个人知识采集系统',
    '张三',
    '2026-01-15T10:00:00+08:00',
    '这是抓取到的原始正文，包含广告、导航和冗余信息。',
    '这是清洗后的正文，仅保留核心内容。',
    '通过标准化入库和结构化提炼，可以显著提升知识复用效率。',
    'summarized',
    '{"collector":"manual_import","version":"v1"}'
);

INSERT INTO content_key_points (content_id, point_order, point_text) VALUES
(1, 1, '采集与提炼分层有助于维护和演进。'),
(1, 2, '统一内容主表可以降低跨类型接入成本。'),
(1, 3, '标签与观点拆表可提升查询灵活性。');

INSERT INTO tags (name) VALUES ('知识管理'), ('SQLite'), ('内容采集')
ON CONFLICT(name) DO NOTHING;

INSERT INTO content_tags (content_id, tag_id)
SELECT 1, id FROM tags WHERE name IN ('知识管理', 'SQLite', '内容采集')
ON CONFLICT(content_id, tag_id) DO NOTHING;

SELECT
    c.id,
    c.title,
    c.one_line_summary,
    (
        SELECT GROUP_CONCAT(t.name, ',')
        FROM content_tags ct
        JOIN tags t ON t.id = ct.tag_id
        WHERE ct.content_id = c.id
    ) AS tags,
    (
        SELECT GROUP_CONCAT(kp.point_text, ' | ')
        FROM content_key_points kp
        WHERE kp.content_id = c.id
        ORDER BY kp.point_order
    ) AS key_points
FROM contents c
WHERE c.id = 1;
