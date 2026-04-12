---
name: rules
description: 贾维斯日常规则全集。子 agent 职责分离、Obsidian 存储范围、URL 路由、任务日志规范等核心规则。

Triggers: 规则,贾维斯规则,rules
---

# 贾维斯规则

## 子 Agent 职责分离

| 任务类型 | 处理方式 |
|---------|---------|
| 视频分析 | → bibi sub-agent（bibi skill） |
| 网页抓取/总结 | → web_fetch sub-agent |
| 写代码/修 Bug | → coding-agent sub-agent（Claude Code） |
| 运维操作（部署/重启/同步） | → sub-agent + 自动验证 |

**原则**：主 agent 不直接写代码，改代码全部由 sub-agent 执行。

## URL 路由规则

| URL 类型 | 处理方式 |
|---------|---------|
| 视频平台（YouTube/B站/抖音/TikTok/小宇宙等） | bibi sub-agent 分析 → 保存 Obsidian |
| 其他所有 URL | web_fetch sub-agent 抓取 → 保存 Obsidian |

## 任务日志规范（agents/）

### 核心原则

**日志写入是 completion 处理的强制步骤，不是可选项。**

sub-agent 完成后 → 主 agent 必须写日志 → 才能通知用户。三步顺序固定。

### 目录结构

```
agents/
  TASK_LOG.md          ← 所有任务汇总
  ISSUE_LOG.md         ← 问题汇总
  coding/              ← 写代码任务成果
    <date>-<task>.md  ← 每个代码任务的摘要
  bibi/                ← 视频分析成果
    <video-id>.md     ← 每个视频的分析结果
  ops/                 ← 运维操作记录
    <date>-<task>.md  ← 每次运维操作
```

### TASK_LOG 格式

```
**[时间]** [类型] [任务摘要] → [结果]
```

### Completion 处理流程（强制）

```
sub-agent 完成 → completion 事件
    ↓
1. 查 rules skill（当前任务类型）
2. 写入 agents/TASK_LOG.md
3. 写入对应子目录（coding/bibi/ops/other）
4. 通知用户
    ↑
三步顺序固定，日志未写完不能通知用户
```

### 任务类型写入指令（completion 时必读）

**coding 任务**：
- 写入 `TASK_LOG.md`：追加 `[coding] [任务摘要] → ✅/❌ 完成/失败`
- 写入 `agents/coding/<date>-<task>.md`：代码任务摘要

**bibi 任务**：
- 写入 `TASK_LOG.md`：追加 `[bibi] [视频标题] → ✅ 完成`
- 写入 `agents/bibi/<video-id>.md`：分析结果路径

**ops 任务**：
- 写入 `TASK_LOG.md`：追加 `[ops] [操作摘要] → ✅/❌`
- 写入 `agents/ops/<date>-<task>.md`：操作步骤 + 验证结果

**其他 sub-agent**：
- 写入 `TASK_LOG.md`：追加 `[other] [任务摘要] → [结果]`

### 与 memory 的关系

- `memory/detail/` = 对话里说了什么
- `agents/` = 说的事**实际做完了没有，怎么做的**

两者互相引用，不重复。

## Obsidian 存储范围

```
贾维斯/
  memory/
    YYYY-MM-DD.md           ← 今日总结 + 引用
    detail/
      YYYY-MM-DD.md         ← 完整逐条记录
  MEMORY.md                 ← 长期记忆精华
  agents/                   ← TASK_LOG、ISSUE_LOG
  BibiGPT/                  ← 视频分析结果
  WebNotes/                 ← 网页抓取总结
  GitHub/                   ← AI 周报
```

## 定时任务

| 任务 | 时间 | 触发方式 |
|------|------|---------|
| agents 同步到 Obsidian | 每天 22:30 | cron → isolated |
| TASK_LOG/ISSUE_LOG 补充检查 | 每天 22:55 | cron → isolated |
| 每日日记生成 | 每天 23:00 | cron → main session |
| 每日复盘 | 每天 09:00 | cron → isolated |
| 每周大复盘 | 每周一 10:00 | cron → isolated |
| GitHub AI 周报 | 每周一 09:00 | cron |
