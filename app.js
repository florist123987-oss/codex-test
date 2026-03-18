const API_BASE_URL = 'http://localhost:8000/api';
const USE_MOCK_DATA = true;

const mockContents = [
  {
    id: 'article-001',
    title: 'OpenAI 发布新一代多模态模型能力概览',
    sourceName: '科技日报',
    sourceUrl: 'https://example.com/openai-multimodal',
    publishedAt: '2026-03-10T09:00:00Z',
    oneSentenceSummary: '新模型在文本、图像和代码任务上表现更均衡，面向个人开发者开放更多接口能力。',
    keyPoints: [
      '模型在多语言问答中稳定性提升。',
      '推出更细粒度的 API 计费模式。',
      '新增可控输出格式能力，便于系统集成。',
      '强调安全策略和企业级审计日志。'
    ],
    tags: ['AI', '模型发布', '开发者工具'],
    cleanedContent:
      '本次发布重点在于统一推理能力与工具调用体验。官方披露了更多性能基准，并对开发者常见场景提供模板。文章指出，未来版本将继续优化响应速度与可解释性。'
  },
  {
    id: 'article-002',
    title: '个人知识库搭建实践：从采集到提炼的最小闭环',
    sourceName: '效率研究社',
    sourceUrl: 'https://example.com/pkm-workflow',
    publishedAt: '2026-03-11T14:30:00Z',
    oneSentenceSummary: '通过轻量自动化流程，把分散信息沉淀为可检索、可复用的知识资产。',
    keyPoints: [
      '先定义统一的数据结构，再接入采集源。',
      '摘要和标签生成要可追溯。',
      '前端展示优先可读性，减少交互负担。'
    ],
    tags: ['知识管理', '工作流', 'MVP'],
    cleanedContent:
      '文章从需求拆解开始，强调“先跑通再优化”。在展示层面建议优先实现列表、搜索和详情三块能力，后续再补充推荐、统计和多维筛选。'
  }
];

const app = document.getElementById('app');

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString('zh-CN', { hour12: false });
}

async function fetchContents(query = '') {
  if (USE_MOCK_DATA) {
    return mockContents.filter((item) => {
      const q = query.trim().toLowerCase();
      if (!q) return true;
      return [item.title, item.sourceName, item.tags.join(' ')].join(' ').toLowerCase().includes(q);
    });
  }

  const url = new URL(`${API_BASE_URL}/contents`);
  if (query.trim()) url.searchParams.set('q', query.trim());

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error('获取内容列表失败');
  }
  const data = await response.json();
  return data.items ?? [];
}

async function fetchContentDetail(id) {
  if (USE_MOCK_DATA) {
    return mockContents.find((item) => item.id === id) ?? null;
  }

  const response = await fetch(`${API_BASE_URL}/contents/${id}`);
  if (!response.ok) {
    throw new Error('获取内容详情失败');
  }
  return response.json();
}

function navigateToList() {
  location.hash = '#/';
}

function navigateToDetail(id) {
  location.hash = `#/content/${id}`;
}

function renderListItem(item) {
  return `
    <li class="content-item">
      <a href="#/content/${item.id}" data-id="${item.id}" class="detail-link">
        <h3 class="content-title">${item.title}</h3>
      </a>
      <div class="meta">来源：${item.sourceName} ｜ 发布时间：${formatDate(item.publishedAt)}</div>
    </li>
  `;
}

async function renderListView() {
  const template = document.getElementById('list-view-template');
  app.innerHTML = '';
  app.append(template.content.cloneNode(true));

  const input = document.getElementById('search-input');
  const list = document.getElementById('content-list');
  const meta = document.getElementById('list-meta');

  const updateList = async () => {
    const query = input.value;
    try {
      const items = await fetchContents(query);
      meta.textContent = `共 ${items.length} 条记录`;
      list.innerHTML = items.length
        ? items.map(renderListItem).join('')
        : '<li class="empty-state">暂无匹配内容。</li>';
      list.querySelectorAll('.detail-link').forEach((link) => {
        link.addEventListener('click', (event) => {
          event.preventDefault();
          navigateToDetail(link.dataset.id);
        });
      });
    } catch (error) {
      meta.textContent = '';
      list.innerHTML = `<li class="empty-state">${error.message}</li>`;
    }
  };

  input.addEventListener('input', updateList);
  await updateList();
}

function renderDetailContent(item) {
  if (!item) {
    return '<p class="empty-state">内容不存在或已删除。</p>';
  }

  const keyPoints = (item.keyPoints || []).map((point) => `<li>${point}</li>`).join('');
  const tags = (item.tags || []).map((tag) => `<li class="tag">${tag}</li>`).join('');

  return `
    <h2>${item.title}</h2>
    <div class="meta">来源：${item.sourceName} ｜ 发布时间：${formatDate(item.publishedAt)}</div>
    <p class="detail-links">来源链接：<a href="${item.sourceUrl}" target="_blank" rel="noopener noreferrer">${item.sourceUrl}</a></p>
    <h3>一句话摘要</h3>
    <p class="summary">${item.oneSentenceSummary}</p>
    <h3>核心观点</h3>
    <ol>${keyPoints}</ol>
    <h3>标签</h3>
    <ul class="tag-list">${tags}</ul>
    <h3>清洗后的正文</h3>
    <p>${item.cleanedContent}</p>
  `;
}

async function renderDetailView(id) {
  const template = document.getElementById('detail-view-template');
  app.innerHTML = '';
  app.append(template.content.cloneNode(true));

  document.getElementById('back-button').addEventListener('click', navigateToList);

  const article = document.getElementById('detail-article');
  try {
    const item = await fetchContentDetail(id);
    article.innerHTML = renderDetailContent(item);
  } catch (error) {
    article.innerHTML = `<p class="empty-state">${error.message}</p>`;
  }
}

function getRoute() {
  const hash = location.hash || '#/';
  const detailMatch = hash.match(/^#\/content\/([^/]+)$/);

  if (detailMatch) {
    return { name: 'detail', id: detailMatch[1] };
  }

  return { name: 'list' };
}

async function renderApp() {
  const route = getRoute();
  if (route.name === 'detail') {
    await renderDetailView(route.id);
  } else {
    await renderListView();
  }
}

window.addEventListener('hashchange', renderApp);
window.addEventListener('DOMContentLoaded', renderApp);
