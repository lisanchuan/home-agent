# Langflow 学习方案

## 项目概览
- **Stars**: 146,751
- **语言**: Python + React
- **定位**: 可视化 AI Flow 编辑器，拖拽构建 RAG/Agent 工作流
- **GitHub**: https://github.com/langflow-ai/langflow
- **学习优先级**: ⭐⭐⭐⭐⭐

---

## 核心理念

Langflow = **LangChain 的可视化前端**，让不懂代码的人也能构建复杂的 AI 工作流。

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Document   │────▶│   Loader    │────▶│   Embedding │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Answer    │◀────│   LLM       │◀────│   Vector DB │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 学习路径

### 第一阶段：快速体验（1天）

**用 Docker 运行：**
```bash
# 5分钟启动
docker run -p 7860:7860 langflowai/langflow

# 浏览器打开
open http://localhost:7860
```

**基础操作：**
1. 从左侧拖拽一个 "Chat Input" 节点
2. 拖拽一个 "OpenAI" 节点
3. 连接两个节点
4. 点击运行

### 第二阶段：理解架构（3-5天）

**三大核心模块：**

1. **lfx** - 核心引擎（Python）
   - Component 接口定义
   - Flow 执行引擎
   - Memory 管理

2. **backend** - FastAPI 后端
   - REST API
   - Flow 持久化
   - 用户认证

3. **frontend** - React 前端
   - React Flow 节点编辑
   - 组件面板
   - 属性配置面板

**关键代码：Component 接口**
```python
# lfx/src/lfx/interface/components.py
class Component:
    name: str
    description: str
    inputs: List[Field]
    outputs: List[Field]
    
    def process(self, inputs: Dict) -> Dict:
        """处理输入，返回输出"""
        raise NotImplementedError
```

### 第三阶段：构建 RAG Flow（3天）

**学习案例：构建一个本地知识库问答**

```
Step 1: 准备文档
- 收集 PDF/Word/TXT 文件
- 放到 data/ 目录

Step 2: 创建 Flow
1. Document Loader (PDF Loader)
2. Text Splitter (分块)
3. OpenAI Embeddings (向量化)
4. Vector Store (Chroma)
5. OpenAI Chat (生成答案)

Step 3: 测试
输入："这份文档的主要内容是什么？"
```

### 第四阶段：二次开发（5-7天）

**实战任务：创建一个自定义 Component**

```python
# my_components/weather.py
from lfx.interface import Component, Field
from typing import Dict, List

class WeatherComponent(Component):
    name = "Weather"
    description = "Get weather for a city"
    inputs = [
        Field(name="city", type="string", description="City name")
    ]
    outputs = [
        Field(name="temperature", type="string"),
        Field(name="condition", type="string")
    ]
    
    def process(self, inputs: Dict) -> Dict:
        city = inputs["city"]
        # 调用天气 API
        weather = get_weather(city)
        return {
            "temperature": weather["temp"],
            "condition": weather["condition"]
        }
```

---

## 对 OpenClaw 的借鉴

| Langflow 设计 | 借鉴点 |
|-------------|--------|
| React Flow 节点编辑器 | 可视化工作流设计 |
| Component 接口 | 标准化 Tool 定义 |
| lfx 核心引擎 | Flow 执行与状态管理 |
| RAG 组件 | 知识库构建模式 |

---

## 快速上手

```bash
# 方式1: Docker (推荐新手)
docker run -p 7860:7860 langflowai/langflow

# 方式2: 源码运行
git clone https://github.com/langflow-ai/langflow.git
cd langflow
pip install -e .
langflow run

# 浏览器打开
open http://127.0.0.1:7860
```

---

## 学习资源

- **官方文档**: https://langflow.org/
- **GitHub**: https://github.com/langflow-ai/langflow
- **示例 Flows**: https://github.com/langflow-ai/langflow/tree/main/examples

---

## 适合人群

- 想构建 AI 工作流的开发者
- 对 RAG/Agent 感兴趣的数据工程师
- 想做可视化 AI 界面的前端开发者

---

*学习方案由 AI 生成 · 2026-04-10*
