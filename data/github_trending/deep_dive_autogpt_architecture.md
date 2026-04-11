# AutoGPT 架构深度解析报告

> 学习时间：2026-04-10 | 源码：classic/forge + classic/original_autogpt

---

## 一、整体架构

```
用户输入任务
     ↓
ProtocolAgent.create_task()
     ↓
Agent.execute_step()
     ├→ propose_action()     ← LLM 思考下一步
     ├→ complete_and_parse() ← 调用 LLM
     └→ execute()            ← 执行命令
```

AutoGPT 分两层：

| 层 | 仓库 | 职责 |
|---|------|------|
| **Forge** | classic/forge | 基础框架：BaseAgent、Component 系统、Command 规范 |
| **Agent** | classic/original_autogpt | 具体实现：7 种推理策略、完整组件集 |

---

## 二、Forge 核心：Component 系统

### 2.1 为什么需要 Component？

传统 Agent 把所有逻辑写在一个类里 → 难以扩展、难以测试。

AutoGPT 的方案：**每个功能独立成 Component，可插拔、可排序**。

### 2.2 Component 本质

```python
class ActionHistoryComponent(
    MessageProvider,      # 提供消息
    AfterParse,          # LLM 响应后触发
    AfterExecute,         # 执行后触发
    ConfigurableComponent
):
    def get_messages(self) -> Iterator[ChatMessage]:
        ...

    def after_parse(self, proposal):
        ...

    def after_execute(self, result):
        ...
```

每个 Component 实现一组**协议方法**（Protocol），Agent 在关键节点自动调用。

### 2.3 协议（Protocol）体系

| 协议 | 触发时机 | 用途 |
|-----|---------|------|
| **DirectiveProvider** | propose_action 前 | 提供资源、约束、最佳实践 |
| **CommandProvider** | propose_action 前 | 提供可用命令列表 |
| **MessageProvider** | propose_action 前 | 提供历史消息 |
| **AfterParse** | LLM 响应后 | 解析后处理（如存历史） |
| **AfterExecute** | 命令执行后 | 执行后处理 |

### 2.4 Pipeline 执行机制

```python
async def run_pipeline(self, protocol_method, *args):
    # 拓扑排序保证执行顺序
    # 重试机制（最多3次）
    # 遇到 EndpointPipelineError 从头重试
    for component in self.components:  # 已排序
        if isinstance(component, protocol_class):
            result = component.{protocol_method}(*args)
```

**拓扑排序**确保依赖顺序。比如 `ContextComponent` 需要先于 `ActionHistoryComponent` 运行：
```python
self.watchdog = WatchdogComponent(...).run_after(ContextComponent)
```

### 2.5 核心 Component 一览

| Component | 职责 |
|----------|------|
| **SystemComponent** | 提供 finish 命令，系统提示 |
| **TodoComponent** | 多步骤任务管理 |
| **ActionHistoryComponent** | 消息历史压缩与管理 |
| **ContextComponent** | 上下文管理 |
| **FileManagerComponent** | 文件读写 |
| **CodeExecutorComponent** | Docker 沙箱代码执行 |
| **WebSearchComponent** | 网页搜索 |
| **WebPlaywrightComponent** | 浏览器自动化 |
| **ImageGeneratorComponent** | 图片生成 |
| **HTTPClientComponent** | HTTP 请求 |
| **GitOperationsComponent** | Git 操作 |
| **SkillComponent** | Skill 系统（SKILL.md 支持） |

---

## 三、Agent 核心流程

### 3.1 propose_action → execute 循环

```python
async def execute_step(self, task_id, step_request):
    # 1. 创建 step
    step = await self.db.create_step(...)

    # 2. LLM 思考
    proposal = await self.propose_action()

    # 3. LLM 执行
    output = await self.execute(proposal)

    # 4. 记录结果
    if isinstance(output, ActionSuccessResult):
        step.output = str(output.outputs)
    else:
        step.output = output.reason

    return step
```

### 3.2 propose_action 详解

```python
async def propose_action(self):
    # 收集 directives（资源、约束、最佳实践）
    resources = await self.run_pipeline(DirectiveProvider.get_resources)
    constraints = await self.run_pipeline(DirectiveProvider.get_constraints)

    # 收集 commands
    self.commands = await self.run_pipeline(CommandProvider.get_commands)

    # 收集 messages（历史）
    await self.history.prepare_messages()  # 压缩
    messages = await self.run_pipeline(MessageProvider.get_messages)

    # 构建 prompt
    prompt = self.prompt_strategy.build_prompt(
        messages=messages,
        task=self.state.task,
        ai_directives=directives,
        commands=function_specs_from_commands(self.commands),
    )

    # 调用 LLM
    output = await self.complete_and_parse(prompt)
    return output
```

### 3.3 并行工具执行

```python
async def _execute_tools_parallel(self, tools):
    # asyncio.gather 并行执行
    results = await asyncio.gather(
        *[execute_single(tool) for tool in tools]
    )
    # 合并结果
```

### 3.4 ActionResult 类型

```python
ActionSuccessResult(outputs=...)     # 成功
ActionErrorResult(reason=...)        # 失败
ActionInterruptedByHuman(feedback=...) # 用户拒绝
```

---

## 四、七种推理策略（Prompt Strategies）

### 4.1 策略一览

| 策略 | 核心理念 | 适用场景 |
|-----|---------|---------|
| **one_shot** | 单次完成 | 简单任务（默认） |
| **plan_execute** | 计划 → 执行 →  replan | 复杂多步骤任务 |
| **rewoo** | Planner 与 Executor 分离 | 高效长任务 |
| **reflexion** | 执行 + 自我反思 | 需要自我改进 |
| **tree_of_thoughts** | 多路径探索 | 需要创意解决 |
| **lats** | Tree + 自我评估 + Backtrack | 高风险任务 |
| **multi_agent_debate** | 多 Agent 辩论 | 需要多角度思考 |

### 4.2 Plan-and-Execute（重点）

**模式**：
```
PLANNING → EXECUTING → (REPLANNING if failed) → EXECUTING → ...
```

```python
class ExecutionPlan:
    goal: str
    steps: list[PlannedStep]
    current_step_index: int
    completed_steps: list[str]
    failed_attempts: int

    def advance_step(self, result_summary):
        # 标记当前步骤完成，前进到下一步
    def mark_step_failed(self, error):
        # 失败后判断是否需要 replan
```

**优势**：96.3% 准确率（Routine 论文），可预测、可干预。

### 4.3 ReWOO（分离 Planner）

```
Planner: 制定计划，输出 "plan.txt"
Executor: 按计划执行，不需 LLM 思考
```

**优势**：Planner 只调用一次，Executor 可批量执行。

### 4.4 Reflexion（自我反思）

```python
class ReflexionStrategy:
    # 每次执行后，让 LLM 反思：
    # "这次做得好吗？下次如何改进？"
    # 反思结果存入记忆，影响下次决策
```

---

## 五、Command 系统

### 5.1 Command 定义

```python
class Command(Generic[P, CO]):
    def __init__(self,
        names: list[str],           # 命令名（支持别名）
        description: str,
        method: Callable,            # 实际执行函数
        parameters: list[CommandParameter],
    ):
```

### 5.2 命令发现机制

```python
class Agent:
    async def run_pipeline(self, CommandProvider.get_commands):
        for component in self.components:
            if hasattr(component, 'get_commands'):
                commands.extend(component.get_commands())
```

Component 的 `get_commands()` 返回该 Component 提供的命令。

### 5.3 Tool 调用流程

```
LLM 返回: {"use_tool": {"name": "read_file", "arguments": {"path": "a.txt"}}}
     ↓
Agent 查找: for command in reversed(commands):
               if "read_file" in command.names:
                   command(**tool.arguments)
```

---

## 六、ActionHistory（记忆系统）

### 6.1 消息压缩

对话历史太长怎么办？AutoGPT 用 LLM 自动压缩：

```python
class ActionHistoryComponent:
    full_message_count: int = 4  # 保留最近 4 条原始消息
    max_tokens: int = 1024       # 压缩后的最大长度

    async def prepare_messages(self):
        # 1. 保留最近 N 条原始消息
        # 2. 更早的消息用 LLM 生成摘要
```

### 6.2 Episodic Memory

```python
class EpisodicActionHistory:
    episodes: list[Episode]  # 每个 episode = 一次任务
    # 支持跨 episode 记忆
```

---

## 七、Skill 系统（SKILL.md 支持）

```python
class SkillComponent:
    def __init__(self, skill_directories=[
        app_config.workspace / ".autogpt/skills",
        Path.home() / ".autogpt/skills",
    ]):
```

**加载流程**：
1. 扫描 skill_directories
2. 解析每个 SKILL.md 的 frontmatter
3. Skill 激活时，读取 SKILL.md body
4. 按需加载 scripts/、references/

---

## 八、对 OpenClaw 的借鉴

### 8.1 高优先级借鉴

| AutoGPT 设计 | OpenClaw 可借鉴 |
|-------------|---------------|
| **Component Pipeline** | Tool/技能的可插拔架构 |
| **Prompt Strategy 模式** | 不同的任务用不同推理策略 |
| **Plan-and-Execute** | 复杂任务自动拆分 |
| **ActionHistory 压缩** | 长对话的 token 节省 |
| **SkillComponent** | 已有，正在优化 |

### 8.2 具体改进建议

**1. 引入 Plan-and-Execute 策略**

```python
# OpenClaw 任务拆分
if 任务复杂度 > 阈值:
    strategy = PlanExecuteStrategy()
else:
    strategy = OneShotStrategy()
```

**2. Component 化 Tool 系统**

```python
class FileToolComponent(BaseComponent):
    def get_commands(self):
        return [read_file, write_file, delete_file, ...]

class WebToolComponent(BaseComponent):
    def get_commands(self):
        return [search, fetch, screenshot, ...]
```

**3. 引入执行预算**

```python
config.cycle_budget = 10  # 最多执行 10 步
# 或
config.cycle_budget = None  # 无限制
```

### 8.3 行动计划

```
Phase 1: 研究 (1-2天)
├── 完整运行 AutoGPT 体验流程
├── 尝试 plan_execute 策略
└── 理解各 Component 职责

Phase 2: 设计 (2-3天)
├── 设计 OpenClaw 的 Component 接口
├── 定义 Tool Component 规范
└── 设计任务拆分策略

Phase 3: 实现 (5-7天)
├── 实现基础 Component 基础设施
├── 迁移现有 Tool 到 Component
└── 实现 Plan-and-Execute 策略

Phase 4: 测试 (3-5天)
├── 单元测试 Component
├── 集成测试 Pipeline
└── 实际任务测试
```

---

## 九、快速实验

```bash
# 1. 克隆 AutoGPT
git clone https://github.com/Significant-Gravitas/AutoGPT.git
cd AutoGPT

# 2. 安装
pip install -e autogpt

# 3. 配置 API Key
export OPENAI_API_KEY=your_key

# 4. 运行（one_shot 模式）
autogpt "帮我写一个快排序"

# 5. 切换策略
export AUTOGPT_PROMPT_STRATEGY=plan_execute
```

---

## 十、关键源码文件

| 文件 | 作用 |
|-----|------|
| `forge/agent/base.py` | BaseAgent、Component 基础设施 |
| `forge/agent/components.py` | AgentComponent 基类 |
| `forge/command/command.py` | Command 定义 |
| `original_autogpt/agents/agent.py` | 完整 Agent 实现 |
| `original_autogpt/agents/prompt_strategies/*.py` | 7 种推理策略 |
| `forge/components/action_history/` | 记忆系统 |
| `forge/components/skills/` | Skill 系统 |

---

## 总结

AutoGPT 的核心贡献：

1. **Component 系统**：可插拔、拓扑排序、Pipeline 执行
2. **Prompt Strategy 模式**：不同任务用不同推理策略
3. **Plan-and-Execute**：可预测、可干预的复杂任务执行
4. **7 种推理策略覆盖**：one_shot / plan_execute / rewoo / reflexion / ToT / LATS / debate

**OpenClaw 的差距**：
- 目前只有简单的 Tool 概念，没有 Component Pipeline
- 只有 one_shot 策略，没有任务拆分
- 没有记忆压缩机制
- 没有 Skill 系统（刚引入）

**下一步**：基于 AutoGPT 的 Component 设计，重构 OpenClaw 的 Tool 系统。

---

*由贾维斯分析生成 · 2026-04-10*
