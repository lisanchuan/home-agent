# Browser Use + Awesome LLM Apps 学习方案

## 项目概览

| 项目 | Stars | 语言 | 定位 |
|-----|-------|-----|------|
| **browser-use** | 86,845 | Python | 让 AI 控制浏览器自动化 |
| **awesome-llm-apps** | 104,923 | Python | LLM 应用集合（RAG、Agent、Multi-Agent）|

**关联性**：browser-use 是 Agent 的"眼睛和手"，awesome-llm-apps 是 Agent 的"大脑"。

---

## Browser Use 学习方案

### 核心理念

> "Make websites accessible for AI agents"

**本质**：AI 通过浏览器"看"网页、点击按钮、填写表单、提取内容。

### 学习路径

#### 第一阶段：快速体验（1天）

```bash
pip install browser-use

# 基础用法
python -c "
from browser_use import Agent
from langchain_openai import ChatOpenAI

agent = Agent(
    llm=ChatOpenAI(model='gpt-4'),
    task='帮我搜索深圳天气'
)
agent.run()
"
```

#### 第二阶段：理解架构（2-3天）

**工作原理：**
1. AI 分析网页 DOM 结构
2. 决定下一步操作（点击/输入/滚动）
3. Playwright 执行操作
4. 获取新页面状态
5. 循环直到完成

**关键代码：**
```python
# browser_use/agent.py (简化)
class Agent:
    def __init__(self, llm, task):
        self.llm = llm
        self.task = task
        self.browser = Browser()
    
    async def run(self):
        page = await self.browser.new_page()
        while not self.is_complete():
            # AI 思考下一步
            action = await self.llm.think(self.get_page_state(page))
            # 执行
            await self.execute_action(page, action)
```

#### 第三阶段：实战项目（4-5天）

**实战任务：构建自动抢票 Bot**

```python
from browser_use import Agent, Controller
from langchain_anthropic import ChatAnthropic
import asyncio

controller = Controller()

@controller.action("抢票")
async def buy_ticket(page, concert_name: str):
    # 1. 打开购票页面
    await page.goto("https://ticket.platform.com")
    
    # 2. 搜索演唱会
    await page.fill("[name=search]", concert_name)
    await page.click("[name=search_btn]")
    
    # 3. 选择场次
    await page.click(f"text={concert_name}")
    
    # 4. 选择位置
    await page.click(".available-seat")
    
    # 5. 下单
    await page.click("#buy_now")
    
    return "抢票完成"

agent = Agent(
    llm=ChatAnthropic(model="claude-sonnet-4"),
    controller=controller,
)

asyncio.run(agent.run("帮我抢axx演唱会的票"))
```

---

## Awesome LLM Apps 学习方案

### 核心理念

> "Collection of awesome LLM apps with AI Agents and RAG"

**本质**：各种 LLM 应用的参考实现集合，学完就能做出自己的 AI 产品。

### 学习路径

#### 第一阶段：概览 + RAG 应用（2-3天）

**目录结构：**
```
awesome-llm-apps/
├── rag/                  # RAG 知识库应用
│   ├── simple_rag/
│   ├── rag_with_websearch/
│   └── rag_with_memory/
├── agents/               # Agent 应用
│   ├── data_analysis_agent/
│   ├── coding_agent/
│   └── research_agent/
└── multi_agent/          # 多 Agent 协作
    └── crewai_examples/
```

#### 第二阶段：RAG 应用深度（3-4天）

**学习案例：构建 PDF RAG 问答**

```python
# rag/pdf_rag_app.py
from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms import OpenAI

# 1. 加载文档
documents = SimpleDirectoryReader("./pdfs").load_data()

# 2. 构建索引
index = VectorStoreIndex.from_documents(documents)

# 3. 查询
query_engine = index.as_query_engine(llm=OpenAI(model="gpt-4"))
response = query_engine.query("这份合同的主要条款是什么？")
print(response)
```

#### 第三阶段：Agent 应用（3-4天）

**学习案例：数据分析 Agent**

```python
# agents/data_analysis_agent/app.py
from crewai import Agent, Task, Crew

# 定义 Agent
data_analyst = Agent(
    role="数据分析师",
    goal="从数据中提取有价值的 insights",
    backstory="你是一个专业的数据分析师，擅长用 Python 分析数据",
    tools=[...],
)

# 定义 Task
analysis_task = Task(
    description="分析 sales_data.csv，找出季度趋势",
    agent=data_analyst,
)

# 执行
crew = Crew(agents=[data_analyst], tasks=[analysis_task])
result = crew.kickoff()
```

---

## 关联：Browser Use + LLM Apps = 自动化工作流

**最强组合：Browser Use 做执行，LLM Apps 提供智能**

```python
# 自动化研究助手
research_agent = Agent(
    role="研究员",
    goal="收集某个主题的最新信息",
    tools=[
        browser_use_tool,  # 搜索网页
        rag_tool,          # 查知识库
        summarizer,        # 总结内容
    ]
)

# 研究任务
task = """
研究主题：2024年 AI Agent 最新进展

步骤：
1. 用 browser_use 搜索最新论文
2. 提取论文摘要
3. 用 RAG 查询历史知识
4. 生成研究报告
"""
```

---

## 对 OpenClaw 的借鉴

| 项目 | 借鉴点 |
|-----|--------|
| **browser-use** | 网页自动化能力，可做爬虫/表单/抢票 |
| **awesome-llm-apps** | RAG/Agent 的最佳实践，代码可直接参考 |

---

## 快速上手

**browser-use：**
```bash
pip install browser-use
# 需要安装 Playwright
playwright install chromium
```

**awesome-llm-apps：**
```bash
git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
cd awesome-llm-apps
pip install -r requirements.txt
# 按需运行各应用
```

---

## 适合人群

- 想让 AI 控制浏览器的开发者
- 想快速做出 LLM 应用的创业者
- 想学习 RAG/Agent 实战的学生

---

*学习方案由 AI 生成 · 2026-04-10*
