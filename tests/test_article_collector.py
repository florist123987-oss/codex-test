import unittest

from article_collector.collector import ArticleCollector


SAMPLE_HTML = """
<html>
  <head>
    <title>测试文章标题</title>
    <meta name="author" content="作者：张三" />
    <meta property="article:published_time" content="2026-03-17T10:00:00+08:00" />
  </head>
  <body>
    <header>站点导航</header>
    <main>
      <article>
        <p>这是第一段正文内容，用于测试文章抓取和正文提取能力，长度足够。</p>
        <p>这是第二段正文内容，应该保留并且和第一段一起组成输出结果。</p>
        <p>这是第三段正文内容，继续验证段落拼接和清洗逻辑。</p>
      </article>
      <aside>相关阅读推荐</aside>
    </main>
    <footer>All rights reserved</footer>
  </body>
</html>
"""


class CollectorExtractionTest(unittest.TestCase):
    def test_parse_core_fields(self) -> None:
        collector = ArticleCollector()
        cleaned = collector._remove_noise(SAMPLE_HTML)

        title = collector._extract_title(cleaned)
        author = collector._extract_author(cleaned)
        published = collector._extract_published_time(cleaned)
        content = collector._extract_content(cleaned)

        self.assertEqual(title, "测试文章标题")
        self.assertEqual(author, "张三")
        self.assertEqual(published, "2026-03-17T10:00:00+08:00")
        self.assertIn("第一段正文内容", content)
        self.assertNotIn("All rights reserved", content)


if __name__ == "__main__":
    unittest.main()
