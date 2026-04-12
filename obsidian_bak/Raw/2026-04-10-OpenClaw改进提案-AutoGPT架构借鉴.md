# OpenClaw 改进提案：参考 AutoGPT 架构

> 基于 AutoGPT 架构深度解析，对比 OpenClaw 现有能力，设计改进方案

---

## 一、OpenClaw vs AutoGPT 架构对比

### OpenClaw 现有架构

```
用户消息 → Gateway (WebSocket)
                ↓
        Agent Loop (pi-agent-core)
                ↓
        Hooks (before_tool_call / after_tool_call 等)
                ↓
        Tools (exec / browser / read / write / web_search / message...)
                ↓
        Skills (SKILL.md 注入系统提示词)
```

**核心组件：**
- Gateway：消息路由（WhatsApp/Telegram/Discord 等）
- Agent Loop：pi-agent-core 运行时
- Hooks：8 个生命周期钩子
- Tools：14+ 内置工具（分组：fs / runtime / web / messaging 等）
- Skills：SKILL.md 格式，可 gating

### AutoGPT 架构

```
用户任务 → ProtocolAgent
                ↓
        Component Pipeline（拓扑排序）
                ↓
    ┌───────────┼────────────┐
    ↓           ↓            ↓
Directive   Command      Message
Provider   Provider    Provider
    ↓           ↓            ↓
    └───────────┼────────────┘
                ↓
        Prompt Strategy（7 种推理策略）
                ↓
        LLM (GPT-4 / Clauel ...)
                ↓
        ActionResult (Success / Error / Interrupted)
```

**核心组件：**
- Component：每个功能独立组件（ActionHistory / Context / FileManager 等）
- Protocol：5 种协议（DirectiveProvider / CommandProvider / MessageProvider / AfterParse / AfterExecute）
- Pipeline：拓扑排序 + 重试机制
- Prompt Strategy：one_shot / plan_execute / rewoo / reflexion / ToT / LATS / multi_agent_debate

---

## 二、OpenClaw 缺少什么

| 功能                   | AutoGPT          | OpenClaw         | 差距                         |
| -------------------- | ---------------- | ---------------- | -------------------------- |
| **组件化 Tool**         | Component 类（可插拔） | Tools（静态函数）      | 缺少协议抽象和生命周期                |
| **Pipeline 执行**      | 拓扑排序 + 重试        | 无                | 工具串行调用，无依赖排序               |
| **推理策略**             | 7 种策略            | 只有 one_shot      | 复杂任务无自动拆分                  |
| **记忆压缩**             | LLM 自动压缩历史       | compaction（简单摘要） | AutoGPT 更智能                |
| **Plan-and-Execute** | 内置支持             | 无                | 复杂任务无法自动拆分                 |
| **Skill 系统**         | SkillComponent   | SKILL.md         | OpenClaw 已有，但无 Component 层 |

---

## 三、OpenClaw 现有可借鉴机制

### 3.1 Hook 系统（部分等同于 Protocol）

OpenClaw 已有 8 个钩子，接近 AutoGPT 的协议机制：

```
before_model_resolve   ← 相当于 AutoGPT 的 Model 选择阶段
before_prompt_build    ← 相当于 DirectiveProvider
before_agent_start     ← 相当于 BeforeExecute
before_agent_reply     ← 相当于 AfterParse（但它是阻止turn）
after_agent_end        ← 相当于 AfterExecute
before_tool_call       ← 工具级别拦截
after_tool_call
before_compaction
```

**差距：** Hook 是全局的，不能按 Component 隔离；Hook 不能修改 Agent 的中间状态。

### 3.2 Multi-Agent（部分等同于 Component 隔离）

OpenClaw 的多 Agent 架构：

```
Gateway
    ├── Agent A (workspace-A, sessions-A)
    ├── Agent B (workspace-B, sessions-B)
    └── Agent C (workspace-C, sessions-C)
```

**差距：** Agent 之间完全隔离，没有 Component 级别的组合能力。

### 3.3 Skills（已有的 SkillComponent 思路）

OpenClaw 的 Skill 系统本质上是 SkillComponent：

```
SKILL.md → 解析 frontmatter → 注入系统提示词 → Agent 决策何时调用
```

---

## 四、改进方案

### 方案 A：渐进改进（低风险）

**不改变核心架构，在现有体系上增强。**

#### A1. 引入 Plan-and-Execute 任务拆分

**现状：** 复杂任务一条 prompt 搞定，容易超时/失败。

**做法：** 在 `before_agent_start` Hook 中检测任务复杂度，自动切换策略。

```javascript
// 在 openclaw.json 中配置
{
  "agents": {
    "defaults": {
      "promptStrategy": "auto",  // auto / one_shot / plan_execute
      "planExecuteThreshold": 5    // 超过 N 个子任务自动用 plan_execute
    }
  }
}
```

**实现思路：**
1. 检测任务是否多步骤（关键词：先...然后.../第一步...第二步.../首先...接着...）
2. 复杂任务自动切换 plan_execute 模式
3. plan_execute 模式下，系统提示词注入"先制定计划再执行"指令

#### A2. 增强记忆压缩（参考 ActionHistoryComponent）

**现状：** OpenClaw compaction 是固定长度截断。

**做法：** 引入 LLM 压缩，保留更多语义。

```javascript
// 在 openclaw.json 中配置
{
  "memory": {
    "backend": "qmd",
    "compression": {
      "enabled": true,
      "llm": "gpt-4o-mini",
      "maxTokens": 1024,
      "preserveLastN": 4
    }
  }
}
```

#### A3. Skill Component 化

**现状：** SKILL.md 静态注入，无条件触发。

**做法：** Skills 支持按协议注册，动态启用。

```javascript
// skill 定义扩展
{
  "name": "github",
  "description": "搜索 GitHub 仓库",
  "protocols": ["CommandProvider", "MessageProvider"],  // 新增
  "triggers": ["github", "repository", "stars"]
}
```

---

### 方案 B：Component 系统（中等风险）

**引入类似 AutoGPT 的 Component Pipeline，但基于 OpenClaw 现有 Hook 机制。**

#### B1. 定义 Component 协议

```typescript
// 定义 5 种协议
interface DirectiveProvider {
  getDirectives(): Directive[];
}

interface CommandProvider {
  getCommands(): Command[];
}

interface MessageProvider {
  getMessages(): ChatMessage[];
}

interface AfterParse {
  afterParse(proposal: Proposal): void;
}

interface AfterExecute {
  afterExecute(result: ActionResult): void;
}
```

#### B2. 实现 Component 基类

```typescript
class AgentComponent {
  protocols: Protocol[];
  enabled: boolean = true;
  _run_after: Type<AgentComponent>[] = [];

  // 启用拓扑排序
  run_after(component: Type<AgentComponent>): this {
    this._run_after.push(component);
    return this;
  }
}
```

#### B3. 重构现有 Tools 为 Components

```typescript
// 文件系统 Component
class FileSystemComponent extends AgentComponent 
    implements CommandProvider, MessageProvider {
    
    protocols = [CommandProvider, MessageProvider];
    
    getCommands() {
        return [read_file, write_file, edit_file, ...];
    }
    
    getMessages() {
        // 可提供相关文件内容作为上下文
    }
}

// Web Component
class WebComponent extends AgentComponent 
    implements CommandProvider, DirectiveProvider {
    
    protocols = [CommandProvider, DirectiveProvider];
    
    getCommands() {
        return [web_search, web_fetch, ...];
    }
    
    getDirectives() {
        return ["优先使用官方文档", "搜索结果优先选择近期内容"];
    }
}
```

#### B4. Pipeline 执行器

```typescript
async function runPipeline(
    agent: Agent,
    methodName: string,
    components: AgentComponent[]
): Promise<any> {
    // 1. 拓扑排序
    const sorted = topologicalSort(components);
    
    // 2. 依次执行
    let result;
    for (const component of sorted) {
        if (!component.enabled) continue;
        const method = component[methodName];
        if (method) {
            result = await method.call(component, result);
        }
    }
    
    return result;
}
```

---

### 方案 C：完整引入 Prompt Strategy（高风险）

**彻底改造 Agent Loop，支持 7 种推理策略。**

#### C1. 定义 Strategy 接口

```typescript
interface PromptStrategy {
    buildPrompt(context: AgentContext): ChatPrompt;
    parseResponse(response: LLMResponse): Proposal;
    recordSuccess(result: ActionResult): void;
    recordFailure(error: string): boolean;  // returns: should replan?
    isComplete(): boolean;
    reset(): void;
}
```

#### C2. 实现 7 种策略

```typescript
class OneShotStrategy implements PromptStrategy {
    // 默认策略，一次完成
}

class PlanExecuteStrategy implements PromptStrategy {
    private plan: ExecutionPlan;
    private phase: 'planning' | 'executing' | 'replanning';
    
    // PLAN → EXECUTE → REPLAN（失败时）→ EXECUTE → ...
}

class ReWOOStrategy implements PromptStrategy {
    // Planner 输出 plan.txt
    // Executor 按计划执行，不需 LLM 思考
}

class ReflexionStrategy implements PromptStrategy {
    // 执行 + 自我反思 + 记忆
}

class TreeOfThoughtsStrategy implements PromptStrategy {
    // 多路径探索
}

class LATSStrategy implements PromptStrategy {
    // Tree + 自我评估 + Backtrack
}

class MultiAgentDebateStrategy implements PromptStrategy {
    // 多 Agent 辩论
}
```

#### C3. 策略选择器

```typescript
function selectStrategy(task: string, context: AgentContext): PromptStrategy {
    if (task.matches多步骤关键词()) {
        return new PlanExecuteStrategy();
    }
    if (task.matches创意关键词()) {
        return new TreeOfThoughtsStrategy();
    }
    if (context.has失败历史()) {
        return new ReflexionStrategy();
    }
    return new OneShotStrategy();
}
```

---

## 五、实施路线图

```
Phase 1: 基础增强（1-2 周）
├── A1. Plan-and-Execute 任务拆分
├── A2. 增强记忆压缩
└── A3. Skill 协议化

Phase 2: Component 系统（3-4 周）
├── B1. 定义 Component 协议
├── B2. 实现 Component 基类
├── B3. 重构 Tools → Components
└── B4. Pipeline 执行器

Phase 3: Prompt Strategy（4-6 周）
├── C1. Strategy 接口
├── C2. 实现 OneShot + PlanExecute
├── C3. 实现其他 5 种策略
└── C4. 策略自动选择器

Phase 4: 测试与优化（2-3 周）
├── 单元测试 Component Pipeline
├── 集成测试各策略
└── 性能优化
```

---

## 六、优先级建议

### 立即可做（1 周内）

**A1. Plan-and-Execute 任务拆分**

原因：
- 用户已有明确需求（复杂任务自动拆分）
- 实现相对简单（只需修改提示词策略）
- 效果显著（复杂任务成功率大幅提升）

### 短期（1-2 周）

**A2. 增强记忆压缩 + A3. Skill 协议化**

原因：
- 复用现有 Hook 机制，改动小
- 提升 Skill 系统的智能程度

### 中期（3-4 周）

**B1-B4. Component 系统**

原因：
- 为长期架构打好基础
- Tool 扩展更规范

### 长期（1-2 月）

**C1-C4. Prompt Strategy**

原因：
- 改动较大，需要更多测试
- 建议在 Component 系统稳定后再做

---

## 七、关键文件路径

| 文件 | 作用 |
|-----|------|
| `/opt/homebrew/lib/node_modules/openclaw/docs/concepts/agent-loop.md` | Agent 循环文档 |
| `/opt/homebrew/lib/node_modules/openclaw/docs/concepts/multi-agent.md` | 多 Agent 架构 |
| `/opt/homebrew/lib/node_modules/openclaw/docs/tools/skills.md` | Skills 系统 |
| `/opt/homebrew/lib/node_modules/openclaw/docs/tools/creating-skills.md` | 创建 Skill |
| `/opt/homebrew/lib/node_modules/openclaw/docs/automation/hooks.md` | Hook 系统 |
| `/tmp/auto_gpt_repo/classic/forge/forge/agent/base.py` | AutoGPT Component 基类 |
| `/tmp/auto_gpt_repo/classic/original_autogpt/autogpt/agents/prompt_strategies/` | 7 种推理策略 |

---

## 八、结论

OpenClaw 的 Gateway + Hook 架构已经很成熟，缺少的主要是：

1. **Component Pipeline**：Tool 层的可组合性
2. **Prompt Strategy**：复杂任务的推理能力
3. **智能记忆压缩**：长对话的 token 优化

**建议从 A1（Plan-and-Execute）开始，因为收益最高、风险最低。**

---

*由贾维斯分析生成 · 2026-04-10*
