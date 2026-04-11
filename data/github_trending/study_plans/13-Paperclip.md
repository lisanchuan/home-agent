# Paperclip AI 公司编排平台 - 系统性学习方案

## 项目概览
- **GitHub**: https://github.com/paperclip-ui/paperclip
- **定位**: 多 AI Agent 编排平台，模拟公司管理模式
- **Stars**: 4.7 万+（上线一个月）
- **技术栈**: TypeScript + Next.js + SQLite/PostgreSQL
- **学习优先级**: ⭐⭐⭐⭐⭐

---

## 核心理念

**Paperclip 不是"更多 AI 员工"，而是"公司管理制度"**

解决多 Agent 系统四大难题：
| 难题 | Paperclip 方案 |
|------|---------------|
| 并发冲突 | Ticket 工单系统，明确 Owner |
| 状态断裂 | Heartbeat 定时唤醒 + 上下文续接 |
| 成本失控 | 预算治理（Governance）+ 成本看板 |
| 逻辑黑箱 | Trace 审计日志，全程可溯源 |

---

## 视频学习路径（4 部系列）

### 视频 1：入门介绍
**BV1heDGBLECh** - "AI时代，用Paperclip打造零人公司"

核心概念：
- CEO/CTO/工程师 角色定义
- AI 自主任务拆解
- MCP 协议集成
- 安装：`npx paperclip`

### 视频 2：本地一键运行
**BV1mtP1zvErw** - "本地一键运行零人工 AI 公司"

关键功能：
- 图形化界面创建 Agent 组织
- 实时看板监控工作状态
- 成本统计面板（每美元消耗）
- 未来方向：运维 Agent → 一键部署

### 视频 3：Claude Code 集成
**BV1dNXUBZEJS** - "Claude Code + Paperclip 全自动 AI 公司"

核心机制：
- **Heartbeat 心跳机制**：定时唤醒，24/7 不间断工作
- **Skills 技能库**：GitHub 链接导入，赋予 Agent 专业能力
- **公司模板**：JStack 架构，一键生成复杂团队
- Claude Code 项目关联，理解业务语境

### 视频 4：架构设计理念 ⭐
**BV1wJPdzQEJe** - "让多 Agents 系统像公司一样运转"

这是最重要的一部，建议优先看：

**四大核心机制：**

```
1. 目标链路 (Goal Chain)
   └─ 约束 Agent 执行方向，防止局部最优导致整体跑偏

2. Ticket 工单系统
   └─ 替代聊天记录，明确 Owner/状态/上下文

3. Heartbeat 心跳
   └─ 定时触发，Agent 自动检查工单推进进度

4. Governance 治理
   └─ 高风险操作审批拦截，预算封顶 + 预警
```

---

## 快速启动

```bash
# 安装（需要 Node.js 18+）
npx paperclip

# 启动后访问 http://localhost:3000
```

**首次配置：**
1. 创建公司，设置预算
2. 招聘 CEO Agent（定义角色 + 选择模型）
3. 让 CEO 自主任命 CTO
4. CTO 招募工程师

---

## 核心概念详解

### 1. 组织架构 (Organization)

```
公司
├── CEO        # 战略决策，目标分解
├── CTO        # 技术架构，任务分配
├── 工程师     # 执行具体任务
├── QA         # 测试验证
└── 运维       # 部署上线
```

每个 Agent 可配置：
- 模型（Claude Code / GPT-4 / 本地模型）
- 指令（instructions）
- 技能包（Skills）
- 预算上限

### 2. Ticket 工单系统

**替代聊天窗口的结构化任务单元：**

```
Ticket #123: 新增用户登录功能
├── Owner: @cto
├── Status: in_progress
├── Priority: high
├── Created: 2024-03-26
├── Context: [相关代码片段 + 设计文档]
└── Subtasks:
    ├── [done] 设计数据库 Schema
    ├── [in_progress] 实现 API
    └── [todo] 编写测试
```

**vs 聊天记录：**
| 聊天 | Ticket |
|------|--------|
| "帮我看看这个 bug" | 明确的 Owner + 状态 |
| 上下文分散 | 集中管理 |
| 无法追踪进度 | 实时看板 |

### 3. Heartbeat 心跳机制

**让 Agent 自动持续工作：**

```
配置心跳频率：每 4 小时
    ↓
到达触发时间
    ↓
Agent 自动唤醒
    ↓
检查工单列表
    ↓
推进下一个任务
    ↓
完成或继续等待
```

**适用场景：**
- 需要 24/7 运行的后台任务
- 跨多天的长周期项目
- 需要定期检查数据的任务

### 4. Skills 技能库

**模块化的 Agent 能力扩展：**

```bash
# 导入方式：粘贴 GitHub 仓库链接
https://github.com/paperclip-skills/frontend-design
```

内置 Skills：
- 前端设计
- 代码安全审计
- 数据库优化
- API 集成

### 5. Governance 治理

**预算控制：**
- 每个 Agent 设置月度预算上限
- 超支自动暂停
- 实时成本看板

**审批流程：**
```
高风险操作（如删除资源、支付）→ 触发审批 → 用户确认 → 执行
```

---

## 实战练习路径

### Level 1：跑通基础流程（1-2 小时）

1. 安装 Paperclip
2. 创建公司，配置 CEO
3. 让 CEO 自主招聘 CTO
4. 通过 CEO 下达一个简单任务
5. 观察工单流转和执行

**验证目标：** 理解 Agent 协作的基本概念

### Level 2：配置完整团队（2-3 小时）

1. 导入公司模板（JStack 架构）
2. 配置多个 Agent（CEO/CTO/工程师/QA）
3. 设置 Heartbeat 频率
4. 配置预算上限
5. 发起一个需要多 Agent 协作的任务

**验证目标：** 掌握团队配置和任务分配

### Level 3：集成现有工具（3-4 小时）

1. 关联 Claude Code 项目
2. 导入需要的 Skills
3. 配置 Governance 审批流程
4. 运行一个完整项目周期

**验证目标：** 能将 Paperclip 融入日常工作流

---

## 与 OpenClaw 的对比

| 维度 | OpenClaw | Paperclip |
|------|----------|-----------|
| Agent 数量 | 单 Agent 为主 | 多 Agent 协作 |
| 任务管理 | 对话式 | Ticket 工单 |
| 持续运行 | 需要外部 Cron | 内置 Heartbeat |
| 成本控制 | 无 | 预算治理 |
| 可观测性 | 有限 | Trace 审计 |

### OpenClaw 可借鉴

1. **工单系统**：结构化任务替代对话
2. **Heartbeat**：定时检查机制
3. **治理机制**：预算 + 审批
4. **多 Agent 协作**：Supervisor/Mentor 分工

---

## 参考资源

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/paperclip-ui/paperclip |
| 官网 | https://paperclip.dev |
| 博主 @五里墩茶社 | B站收藏夹 "AI时代，用Paperclip打造零人公司" |

---

## 下一步

1. **看视频 4**（BV1wJPdzQEJe）— 架构理念最重要
2. **安装 Paperclip** — `npx paperclip`
3. **跑通第一个任务** — 理解基本流程
4. **配置完整团队** — 实战练习

要我现在帮你安装 Paperclip 试试吗？
