# 内容采集与提炼器（MVP）规划文档

## A. 项目需求文档（PRD）

### 1) 项目背景
你需要一个「个人知识整理系统」，将分散在网页中的高价值内容沉淀成可检索、可复习、可二次利用的知识资产。

### 2) MVP 目标（范围内）
1. 输入网页文章链接
2. 抓取：标题、作者、发布时间、正文
3. 清洗正文
4. 存入 SQLite
5. 生成一句话摘要
6. 生成 3-7 条核心观点
7. Web 页面支持：列表、搜索、详情

### 3) 明确不做（范围外）
- 短视频抓取
- 公众号复杂兼容
- 登录绕过 / 反爬绕过
- 复杂权限系统
- 小程序版本

### 4) 用户故事（个人单用户）
- 作为用户，我希望粘贴一个链接后可一键入库。
- 作为用户，我希望看到自动提炼的摘要和核心观点，快速判断是否值得复习。
- 作为用户，我希望通过关键词快速搜到历史文章。
- 作为用户，我希望在详情页查看原文清洗结果和结构化元数据。

### 5) 功能需求

#### 5.1 内容采集
- 输入：URL
- 输出：原始 HTML + 基础元数据（title/author/published_at/content）
- 失败处理：抓取失败时记录错误原因，允许重试

#### 5.2 内容清洗
- 去除导航、广告、脚注等噪声
- 保留段落结构
- 统一空白字符、换行、编码
- 产出：clean_text

#### 5.3 内容提炼
- 基于 clean_text 生成：
  - one_sentence_summary（1 句话）
  - key_points（3-7 条）
- 失败处理：若提炼失败，文章可先入库并标记 `analysis_status=failed`

#### 5.4 数据存储
- 使用 SQLite，记录采集、清洗、提炼全流程状态
- 支持按标题、正文、关键词搜索

#### 5.5 Web 界面
- 列表页：展示标题、来源域名、发布时间、摘要
- 搜索：关键字搜索标题与正文
- 详情页：展示元数据、清洗正文、摘要、核心观点、原文链接

### 6) 非功能需求
- 稳定优先于“全网兼容”
- 模块可替换（抓取器、提炼模型、前端）
- 错误可追踪（日志 + 状态字段）
- 单机可运行，部署复杂度低

### 7) MVP 验收标准
- 至少支持常见新闻/博客静态网页链接入库
- 10 篇文章连续处理成功率 >= 80%（不含明显反爬站点）
- 搜索可在 1 秒内返回（<5k 文章规模）
- 详情页可完整显示摘要与核心观点

---

## B. 技术架构建议

## 1) 推荐技术栈（轻量、稳）
- **后端**：Python + FastAPI
- **抓取**：httpx + readability-lxml + beautifulsoup4
- **任务执行**：MVP 先同步执行（请求触发即处理）；后续可升级为后台队列（RQ/Celery）
- **数据库**：SQLite + SQLModel / SQLAlchemy
- **前端**：服务端模板（Jinja2 + HTMX）或极简 Vanilla JS
- **摘要提炼**：可插拔 `LLMProvider`（先接一个稳定 API，后续可切换）

## 2) 架构风格
采用分层 + 端口适配器思路：
- API 层（输入输出协议）
- 应用服务层（用例编排）
- 领域层（文章实体与规则）
- 基础设施层（抓取、数据库、LLM、日志）

这样可保证后续替换抓取策略或 LLM 时不影响上层。

## 3) 运行形态
- 单进程 FastAPI 应用 + SQLite 文件
- 本地开发直接 `uvicorn` 启动
- 后续可 Docker 化

---

## C. 项目目录结构建议

```text
content-curator/
├─ app/
│  ├─ main.py                     # FastAPI 入口
│  ├─ config.py                   # 配置管理
│  ├─ api/
│  │  ├─ routes_ingest.py         # 提交 URL / 重试
│  │  ├─ routes_articles.py       # 列表/搜索/详情
│  │  └─ schemas.py               # Pydantic 请求响应模型
│  ├─ services/
│  │  ├─ ingest_service.py        # 采集编排
│  │  ├─ clean_service.py         # 清洗编排
│  │  └─ summarize_service.py     # 提炼编排
│  ├─ domain/
│  │  ├─ models.py                # 领域模型
│  │  └─ enums.py                 # 状态枚举
│  ├─ infra/
│  │  ├─ crawler/
│  │  │  ├─ fetcher.py            # HTTP 抓取
│  │  │  └─ extractor.py          # 正文提取
│  │  ├─ llm/
│  │  │  ├─ base.py               # Provider 抽象
│  │  │  └─ provider_openai.py    # 某 LLM 实现
│  │  ├─ db/
│  │  │  ├─ engine.py             # SQLite 连接
│  │  │  ├─ orm_models.py         # ORM 模型
│  │  │  └─ repository.py         # 数据访问
│  │  └─ logging.py               # 日志封装
│  ├─ web/
│  │  ├─ templates/
│  │  │  ├─ list.html
│  │  │  └─ detail.html
│  │  └─ static/
│  └─ utils/
│     ├─ text_utils.py
│     └─ time_utils.py
├─ scripts/
│  ├─ init_db.py
│  └─ import_urls.py
├─ tests/
│  ├─ test_cleaner.py
│  ├─ test_extractor.py
│  └─ test_api_articles.py
├─ data/
│  └─ app.db
├─ .env.example
├─ pyproject.toml
└─ README.md
```

---

## D. 模块划分建议

1. **Ingest 模块**
   - 职责：接收 URL，拉取原始 HTML，提取正文和元数据
   - 输出：`ArticleRaw` + 初步结构化字段

2. **Clean 模块**
   - 职责：正文清洗、标准化
   - 输出：`clean_text`

3. **Summarize 模块**
   - 职责：调用 LLM，生成摘要 + 核心观点
   - 输出：`summary`、`key_points[]`

4. **Storage 模块**
   - 职责：统一持久化文章、状态、错误日志
   - 输出：可查询记录

5. **Search & Query 模块**
   - 职责：列表、全文关键字匹配、详情聚合

6. **Web UI 模块**
   - 职责：输入链接、展示列表、搜索、详情

7. **Observability 模块（轻量）**
   - 职责：结构化日志 + 基本处理指标（成功/失败计数）

---

## E. 第一阶段开发顺序

1. **数据模型和 SQLite 落地**
   - 先建表：articles、analysis_results、ingest_logs
2. **抓取 + 正文提取最小链路打通**
   - 手工输入 URL，拿到 title + content
3. **清洗模块接入并入库**
   - 可查看清洗后的正文
4. **摘要/核心观点模块接入**
   - 先做同步调用，失败可重试
5. **API 完整化（新增、列表、详情、搜索）**
6. **Web 页面（列表 + 搜索 + 详情）**
7. **补充错误处理、日志、基础测试**

这个顺序优点：先保证数据资产可沉淀，再增加智能提炼与体验层。

---

## F. 子模块接口依赖（实战版）

## 1) 处理流程（同步）
`POST /ingest` → IngestService
1. Fetcher.fetch(url) -> `raw_html`
2. Extractor.extract(raw_html, url) -> `title, author, published_at, content`
3. Cleaner.clean(content) -> `clean_text`
4. Summarizer.summarize(clean_text) -> `summary, key_points`
5. Repository.save(...) -> SQLite

## 2) 关键接口定义建议

### Fetcher
- `fetch(url: str) -> FetchResult`
- `FetchResult { final_url, status_code, html, fetched_at }`

### Extractor
- `extract(html: str, url: str) -> ExtractResult`
- `ExtractResult { title, author, published_at, raw_text }`

### Cleaner
- `clean(raw_text: str) -> CleanResult`
- `CleanResult { clean_text, word_count }`

### Summarizer
- `summarize(clean_text: str) -> SummaryResult`
- `SummaryResult { one_sentence_summary, key_points: list[str] }`

### Repository
- `create_article(article: ArticleCreate) -> Article`
- `update_analysis(article_id: int, analysis: SummaryResult) -> None`
- `search_articles(query: str, limit: int, offset: int) -> list[Article]`
- `get_article_detail(article_id: int) -> ArticleDetail`

## 3) 解耦原则
- Service 仅依赖抽象接口，不依赖具体 LLM 实现
- 数据库存储结构与 API 响应结构分离（避免 ORM 直接透出）
- 抓取失败、提炼失败分别建状态字段，避免“一刀切失败”

---

## G. 最容易踩的坑（重点）

1. **把“抓取失败”和“提炼失败”混成一个失败状态**
   - 会导致无法重试局部步骤。应拆分 `ingest_status` 与 `analysis_status`。

2. **过早追求全站兼容**
   - MVP 先聚焦常见静态内容站点；兼容性作为后续迭代。

3. **正文提取策略单一**
   - 仅靠一种库会在不同站点失效。建议“readability 优先 + BeautifulSoup 兜底”。

4. **未保存原始数据**
   - 只存 clean_text 会丢失可追溯性。建议保留 raw_html（可选压缩）和 raw_text。

5. **LLM 输出不稳定未做约束**
   - 必须在提示词中限制格式，并做解析校验（条数 3-7、去重、空值过滤）。

6. **SQLite 查询性能被忽视**
   - 随数据增大，`LIKE %keyword%` 变慢。建议提前考虑 FTS5 或最少建立索引。

7. **前端一次性做太复杂**
   - MVP 用服务端渲染即可，避免前后端分离增加维护成本。

8. **缺少可观测性**
   - 没有日志就无法定位哪一步失败。至少记录 `url`, `stage`, `error_message`, `duration_ms`。

9. **提示词与模型绑定太死**
   - 未来切模型会痛苦。建议抽象 `LLMProvider` + Prompt Template。

10. **没有“幂等策略”导致重复入库**
   - 同一 URL 多次提交时应支持去重（URL 唯一键 + content hash）。

---

## 建议的下一步（可直接执行）
1. 先确认数据表字段（我可下一步直接给你 SQLite 建表 SQL）。
2. 再做 API 合同（OpenAPI 草案）。
3. 最后按开发顺序逐模块落地，先跑通 5 篇样例文章。
