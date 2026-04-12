# LangChain 学习方案

## 项目概览
- **Stars**: 132,985
- **语言**: Python
- **定位**: Agent 工程平台，AI 应用开发框架
- **GitHub**: https://github.com/langchain-ai/langchain
- **学习优先级**: ⭐⭐⭐⭐⭐

---

## 核心理念

> "The agent engineering platform"

LangChain = **AI 应用的"操作系统"**，提供了构建 AI 应用所需的所有组件。

**六大核心模块：**

| 模块 | 作用 |
|-----|------|
| **Models** | 多模型支持（OpenAI、Anthropic、Local） |
| **Prompts** | Prompt 模板管理 |
| **Indexes** | 文档加载、分割、向量检索 |
| **Memory** | 对话历史管理 |
| **Chains** | 多步骤任务串联 |
| **Agents** | 自主决策执行 |

## 学习路径

### 第一阶段：核心概念（2-3天）

**Hello World：**
```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

llm = ChatOpenAI(model="gpt-4")

response = llm.invoke([
    HumanMessage(content="用一句话解释量子计算")
])
print(response.content)
```

### 第二阶段：Chain 链路（3-4天）

**LCEL（LangChain Expression Language）：**
```python
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser

# 构建 chain
chain = (
    ChatPromptTemplate.from_messages([
        ("system", "你是一个{topic}专家"),
        ("human", "解释{concept}的核心原理")
    ])
    | ChatOpenAI(model="gpt-4")
    | StrOutputParser()
)

# 执行
result = chain.invoke({
    "topic": "机器学习",
    "concept": "梯度下降"
})
```

### 第三阶段：RAG 构建（3-4天）

**学习案例：构建企业知识库问答**

```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

# 1. 加载文档
loader = DirectoryLoader('./docs/', glob="**/*.pdf")
docs = loader.load()

# 2. 分割
splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
chunks = splitter.split_documents(docs)

# 3. 向量存储
vectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings())

# 4. 构建 RAG Chain
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4"),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# 5. 问答
result = qa.invoke("公司的年假政策是什么？")
```

### 第四阶段：Agent 开发（5-7天）

**实战项目：构建多工具 Agent**

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain import hub

# 定义工具
tools = [
    Tool(
        name="search",
        func=search_engine,
        description="搜索互联网信息"
    ),
    Tool(
        name="calculator", 
        func=calculate,
        description="数学计算"
    )
]

# 创建 Agent
prompt = hub.pull("hwchase17/openai-functions-agent")
agent = create_openai_functions_agent(llm, tools, prompt)

# 执行
executor = AgentExecutor(agent=agent, tools=tools)
result = executor.invoke({"input": "查一下深圳人口，再除以北京人口"})
```

---

## 对 OpenClaw 的借鉴

| LangChain 设计 | 借鉴点 |
|---------------|--------|
| Chain + LCEL | 任务链路组合 |
| Tool 定义规范 | OpenClaw Tool 接口 |
| Memory 模块 | 对话上下文管理 |
| RAG 组件 | 知识检索增强 |

---

## 快速上手

```bash
# 安装
pip install langchain langchain-openai langchain-community

# 环境变量
export OPENAI_API_KEY=your_key

# 开始使用
python -c "import langchain; print(langchain.__version__)"
```

---

## 学习资源

- **官方文档**: https://python.langchain.com/
- **API 参考**: https://api.python.langchain.com/
- **教程**: https://github.com/gptengwei/langchain-tutorials

---

## 适合人群

- 想快速构建 AI 应用的开发者
- 需要 RAG 知识库的企业团队
- 想学习 Agent 开发的数据工程师

---

*学习方案由 AI 生成 · 2026-04-10*
