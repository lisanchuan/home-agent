# MEMORY.md - 贾维斯的长期记忆

_这是贾维斯 curated 的记忆精华，不是日志。_

---

## 用户信息

- **名字**：[待填写]
- **称呼**：[待填写]
- **时区**：Asia/Shanghai
- **角色**：全栈开发者 / 研究者
- **偏好**：简洁高效，不废话

---

## 技术背景

- **专长**：全栈开发，跨领域研究
- **常用语言**：[根据实际使用更新]
- **常用工具**：[根据实际使用更新]

---

## 项目上下文

_[随着使用，逐步记录重要项目信息]_

---

## 重要决策记录

_[记录重大技术决策，避免重复讨论]_

例：
- "2026-04 用户偏好使用 trash 而非 rm"
- "2026-04 用户选择 MiniMax 作为主要 LLM"

---

## 观察到的偏好

- 喜欢简洁的回复
- 代码优先，用代码说明问题
- 谨慎执行外部操作
- 喜欢先全局检查再行动（"你自己查一遍"）

---

## 规则全集

核心规则已归入 skill：`~/.openclaw/skills/rules/SKILL.md`

包含：子 agent 职责分离、URL 路由、Obsidian 存储范围、定时任务。

---

## ⚠️ 重要规则（必须遵守）

### 定时任务失败必须立即通知

**规则**：任何定时任务（Cron Job）执行失败，必须在发现后**第一时间**通知用户，不得隐瞒、不得延迟、不得忽略。

**触发条件**：
- Cron 任务状态变为 `error`
- 连续 `consecutiveErrors` > 0
- 任何 `lastRunStatus` 为 `error` 的任务

**通知方式**：主动发消息到微信，说明：
1. 哪个任务失败了（任务名 + ID）
2. 失败原因（错误信息）
3. 已经/将要采取的修复措施

**示例**：
> "⚠️ 定时任务失败：[每日复盘] 连续错误 5 次\n原因：Delivering to openclaw-weixin requires target\n修复：已补全 delivery.to 参数"

**这是硬规则**，不属于「谨慎操作需先确认」范畴——发现就要说，不需要等用户问。

---

## 学习记录 - 2026-04-07

### 今日完成
- ✅ OpenClaw 基础概念
- ✅ 贾维斯 SOUL.md 配置（简洁高效风格）
- ✅ USER.md / MEMORY.md 初始化
- ✅ GitHub CLI 配置
- ✅ 微信渠道连接（@tencent-weixin/openclaw-weixin）
- ✅ 自我进化系统搭建（Supervisor + Mentor）

### 待继续学习
- 多 Agent 配置（多个 Agent、路由规则）
- 安全设置（Sandbox、权限）
- 进阶工具（Heartbeat、Cron）

---

## 自我进化系统

### 系统架构

```
用户 → 贾维斯(Worker) → 执行任务
              ↓
         Supervisor (监控)
              ↓
         ISSUE_LOG / TASK_LOG
              ↓
         Mentor (复盘) → 每天 9:00 / 每周一 10:00
```

### 相关路径

- Supervisor：`~/.openclaw/agents/supervisor/agent/`
- Mentor：`~/.openclaw/agents/mentor/agent/`
- 日志：`~/.openclaw/agents/supervisor/workspace/`
- 复盘：`~/.openclaw/agents/mentor/workspace/reviews/`

### 已知问题

- ~~任务遗漏：给多个任务时只完成一个~~ ✅ 已改进
- ~~缺少检查：完成后跳过了验证步骤~~ ✅ 已改进
- **新发现**：微信图片防盗链导致抓取失败

---

## 改进记录 - 2026-04-08

### 基于复盘的改进

1. **添加需求澄清规则**：模糊任务必须先确认范围
2. **添加图片处理规范**：外部图片必须下载到本地
3. **添加进度汇报规范**：长时间任务要主动汇报

### 用户项目问题（待解决）

- **harmonica-music**：Docker 部署问题（已解决）
- **we-mp-rss + harmonica-music 融合**：微信图片防盗链问题
- **核心需求**：用户只要乐谱（图片/PDF），不要其他内容

---

## 改进记录 - 2026-04-12

### 返回按钮 history.back() 改造
- **问题**：详情页硬编码返回首页，不知道上一页
- **解决**：创建 `BackButton.tsx`，用 `window.history.back()` + fallback
- **教训**：下次遇到导航问题，先全局查所有路由再用 `grep -rn` 确认没有遗漏

### sheetmusic-identifier 批量更新
- **问题**：batch_update.py 跑太慢（OCR）
- **改进**：去掉 OCR，纯 PIL 尺寸分析，秒级完成
- **去重规则**：同页乐谱拆成多张时，按尺寸去重
- **结果**：79 篇成功，0 篇跳过

### 口琴详情页 Bug
- **问题**：sheet_images fallback 被删除导致口琴白屏
- **教训**：修改数据渲染逻辑前必须确认数据源多样性，尤克里里有 sheet_images，口琴只有 content

### Cron Job SIGKILL
- **问题**：每周大复盘 9:00 运行时被 SIGKILL
- **根因**：超时太短（被系统 kill）
- **修复**：增加 timeout 到 120s

---

## 待学习

_[记录用户想深入了解的话题]_

