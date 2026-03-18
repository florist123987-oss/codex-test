# 内容采集与提炼器（前端展示模块 MVP）

这是一个面向“已采集 + 已提炼”内容的前端展示模块 MVP，支持：
- 内容列表浏览
- 标题/来源/标签搜索
- 详情查看（标题、来源链接、一句话摘要、核心观点、标签、清洗正文）

## 快速启动

### 1) 本地静态启动
```bash
python3 -m http.server 4173
```
然后打开：
`http://localhost:4173`

### 2) 接入后端 API
在 `app.js` 中修改：
- `USE_MOCK_DATA = false`
- `API_BASE_URL = "你的后端地址"`

## 接口假设

### GET /api/contents?q=关键词
返回列表：
```json
{
  "items": [
    {
      "id": "article-001",
      "title": "文章标题",
      "sourceName": "来源名",
      "sourceUrl": "https://example.com/a",
      "publishedAt": "2026-03-10T09:00:00Z",
      "oneSentenceSummary": "一句话摘要",
      "keyPoints": ["观点1", "观点2", "观点3"],
      "tags": ["标签A", "标签B"],
      "cleanedContent": "清洗后的正文"
    }
  ]
}
```

### GET /api/contents/:id
返回单条详情（字段同上）。

## 文件说明
- `index.html`：页面骨架与模板
- `styles.css`：MVP 样式
- `app.js`：路由、搜索、列表、详情渲染与数据获取
