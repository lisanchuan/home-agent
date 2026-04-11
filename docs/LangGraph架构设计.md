# home-agent LangGraph 架构设计

> 基于 LangGraph 的多 Agent 协调框架
> 版本：1.0 | 日期：2026-04-11

---

## 一、为什么用 LangGraph

现有设计（多 Agent 动态派生）的核心问题：

| 问题 | 原因 | LangGraph 解决 |
|------|------|---------------|
| 状态分散 | 每个 Agent 独立管理状态 | 中心 State Schema |
| 流程不可控 | Agent 自行决定下一步 | 显式边（edges） |
| 循环不可检测 | 无迭代上限 | StateGraph 内置计数器 |
| 无法暂停/恢复 | 无检查点机制 | LangGraph Checkpointer |

---

## 二、整体架构

```
用户请求 → Router → 主 Graph
                    │
              ┌─────┼─────┐
              ▼     ▼     ▼
         WorkAgent  LifeAgent  LearnAgent
              │     │     │
              ▼     ▼     ▼
         Supervisor → MemoryWriter → 回复用户
```

### 核心组件

```
src/
├── graph/
│   ├── state.py          # HomeAgentState 定义
│   ├── nodes.py          # 各节点函数
│   ├── edges.py          # 条件边逻辑
│   └── builder.py        # 构建 StateGraph
├── agents/
│   ├── base.py           # Agent 基类
│   ├── router.py         # 路由 Agent
│   ├── work.py           # 工作助手
│   ├── life.py           # 生活助手
│   ├── learn.py          # 学习助手（集成 RAG）
│   └── supervisor.py     # 审查 Agent
├── memory/               # 复用现有 Family Memory Center
│   ├── vector_store.py
│   ├── learning.py
│   └── ...
└── cli.py                # 命令行入口
```

---

## 三、State Schema（核心）

```python
from typing import TypedDict, Annotated, Literal
from typing import Optional

class HomeAgentState(TypedDict):
    # === 路由层 ===
    intent: str                    # "work" | "life" | "learn" | "finance" | "memory" | "unknown"
    route_confidence: float        # 路由置信度 (0-1)

    # === 请求层 ===
    user_message: str              # 用户原始消息
    context_history: list[str]     # 最近 5 条对话历史

    # === 计划层 ===
    plan: list[str]                # 分解步骤（可选，复杂任务时）
    current_step: int              # 当前执行到哪步

    # === 执行层 ===
    current_agent: str             # 当前负责的子Agent
    agent_results: dict            # {agent_name: {"summary": str, "confidence": float, "learnings": list}}
    supervisor_feedback: str       # 审查意见
    needs_revision: bool           # 是否需要重写

    # === 输出层 ===
    final_response: str            # 最终回复
    learnings_to_save: list[dict]  # 待存入记忆的新知识

    # === 控制层 ===
    iteration_count: int           # 循环次数（防死循环）
    max_iterations: int            # 最大循环次数
    needs_approval: bool           # 是否需要用户确认
    approval_context: str          # 确认的具体内容
    error_message: str             # 错误信息
```

---

## 四、节点定义

### 4.1 Router（入口）

```python
def router_node(state: HomeAgentState) -> dict:
    """
    输入：user_message
    输出：intent + route_confidence
    
    用 LLM 做意图分类，提取关键实体
    """
```

**分类规则**：
- `work` - 工作任务、项目、会议、技术
- `life` - 日常、家庭、健康、出行
- `learn` - 知识问答、学习、研究
- `finance` - 预算、消费、理财
- `memory` - 查找记忆、回忆（如"上次说的那家餐厅"）
- `unknown` - 无法分类

### 4.2 Delegator（派发）

```python
def delegator_node(state: HomeAgentState) -> dict:
    """
    根据 intent 设置 current_agent
    如果需要多 Agent 协作，设置 plan
    """
```

### 4.3 子 Agent 节点

每个子 Agent 结构一致：

```python
def agent_node(state: HomeAgentState, agent_name: str, agent_prompt: str) -> dict:
    """
    1. 加载 agent_prompt + 相关记忆
    2. 检索 RAG 知识库
    3. 生成回复
    4. 提取 learnings
    5. 评估 confidence
    """
```

| Agent | Prompt | 记忆加载 |
|-------|--------|---------|
| WorkAgent | 工作助手 | 工作档案 + 项目上下文 |
| LifeAgent | 生活助手 | 家庭档案 + 偏好库 |
| LearnAgent | 学习助手 | 知识库 + RAG 向量 |
| FinanceAgent | 财务助手 | 消费档案 |
| MemoryAgent | 记忆检索 | 全量记忆库 |

### 4.4 Supervisor（审查）

```python
def supervisor_node(state: HomeAgentState) -> dict:
    """
    检查子 Agent 输出：
    - 回答是否准确？
    - 置信度够不够？
    - 有没有遗漏关键信息？
    
    输出：
    - supervisor_feedback
    - needs_revision
    """
```

### 4.5 MemoryWriter（记忆写入）

```python
def memory_writer_node(state: HomeAgentState) -> dict:
    """
    将 learnings_to_save 写入 Family Memory Center
    复用现有 memory/learning.py
    """
```

---

## 五、边（条件路由）

```
START → Router
Router → 路由置信度 > 0.7 ? Delegator : clarify_node
Delegator → current_agent node
Agent node → Supervisor
Supervisor → needs_revision ? 回退到 Agent : MemoryWriter
MemoryWriter → needs_approval ? approval_node : END
approval_node → 用户拒绝 ? Agent : MemoryWriter → END
```

### 循环控制

```python
def should_revise(state: HomeAgentState) -> str:
    if state["needs_revision"] and state["iteration_count"] < state["max_iterations"]:
        return "revise"
    return "continue"
```

---

## 六、复用现有代码

| 现有模块 | LangGraph 中使用方式 |
|---------|-------------------|
| `memory/vector_store.py` | LearnAgent 检索 |
| `memory/learning.py` | MemoryWriter 写入 |
| `memory/schema.py` | State 中 learnings 格式 |
| `memory/backup.py` | 节点：backup_node |
| `rag/query.py` | 子 Agent 知识检索 |

**不需要重写的**：
- 向量存储
- 学习机制
- 记忆管理
- 备份恢复

**需要新建的**：
- Graph 编排（state + nodes + edges）
- Agent 封装（LLM 调用 + prompt）
- CLI 入口

---

## 七、实施计划

### Phase 1：Graph 骨架（1-2天）
- [ ] 定义 HomeAgentState
- [ ] 实现 Router 节点
- [ ] 实现 1 个子 Agent（LearnAgent）
- [ ] 实现基础边逻辑
- [ ] CLI 测试

### Phase 2：全 Agent 接入（2-3天）
- [ ] WorkAgent / LifeAgent / FinanceAgent
- [ ] Supervisor 审查
- [ ] MemoryWriter 集成
- [ ] 循环控制 + 迭代上限

### Phase 3：高级功能（后续）
- [ ] 人类确认节点（暂停/恢复）
- [ ] Checkpointer（状态持久化）
- [ ] 多步计划分解
- [ ] Agent 间通信

---

## 八、对比 DeerFlow

| | home-agent LangGraph | DeerFlow |
|--|---------------------|----------|
| 目标 | 家庭助手（持续运行） | 研究助手（单次任务） |
| 状态 | 持久化，跨对话 | 任务结束即丢弃 |
| 记忆 | 家庭档案 + 向量库 | 无 |
| 学习 | 被动 + 主动 | 无 |
| 多Agent | 领域专家 | 搜索/写作/审查 |
| 人类交互 | 确认、审批、闲聊 | 单次提问 |

**结论**：LangGraph 是工具，DeerFlow 是产品。我们用 LangGraph 造的是 home-agent 这个产品。
