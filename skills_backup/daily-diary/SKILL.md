---
name: daily-diary
description: 贾维斯每日日记生成。每天 23:00 定时或手动触发，读取当天所有 session 历史，生成逐条记录和总结。不在每次对话时触发。

Triggers: 写日记,今天有什么,今天的记录,生成日记,daily diary
---

# Daily Diary Skill

## 目录结构

```
memory/
  YYYY-MM-DD.md              ← 今日总结 + 逐条引用
  detail/
    YYYY-MM-DD.md            ← 完整逐条记录
```

## 执行步骤

### 第一步：检查点
1. 找 main session 文件：`ls -t ~/.openclaw/agents/main/sessions/*.jsonl | grep -v checkpoint | head -1`
2. 读**最后10行**确认有今天的 timestamp（文件跨多天，要看尾部）
3. 找不到今天记录 → 发预警，不写空白日记

### 第二步：生成逐条记录
读取当天 session 历史，按格式生成每条记录：

```markdown
**时间**：YYYY-MM-DD HH:mm（从 session 原始 timestamp 提取）
**用户要求**：[user message 原文]
**原始数据**：[URL、命令、错误信息等能留则留]
**我的行动**：[实质行动]
**结果**：✅/❌/🔄进行中
```

**过滤**：
- 纯对话不单独成条（好的/知道了/谢谢/HEARTBEAT_OK）
- 系统正常响应不单独成条

### 第三步：生成总结
基于逐条记录，生成审视性总结：

```markdown
## 今日总结

### 核心工作
[今天主要做了什么，1-3句话]

### 决策记录
- [决策1]：为什么这样选
- [决策2]：为什么这样选

### 问题记录
- [问题1]：根因 + 下次怎么避免
- [问题2]：根因 + 下次怎么避免

### 规则建立
- 今天新建立了 xxx 规则
- 今天新创建了 xxx skill

### 教训
- [踩过的坑1]
- [踩过的坑2]

### 未完成
- [事项1]：卡在什么问题上
- [事项2]：下一步要做什么
```

### 第三步补充：引用 agents/TASK_LOG
1. 读取 `~/.openclaw/agents/supervisor/workspace/TASK_LOG.md`
2. 找出当天（YYYY-MM-DD）的条目
3. 在总结「核心工作」后面加一行：
   ```markdown
   ### 任务执行记录（来自 agents/TASK_LOG）
   [当天 TASK_LOG 的条目原文]
   ```
4. 如果有 coding/ops 子目录当天的任务，也补充链接

### 第四步：写入文件

1. `memory/detail/YYYY-MM-DD.md` → 完整逐条记录
2. `memory/YYYY-MM-DD.md` → 今日总结 + 逐条记录引用

格式：
```markdown
# YYYY-MM-DD 日记

## 今日总结
[总结内容]

> 📋 详细记录：memory/detail/YYYY-MM-DD.md
```

### 第五步：同步 Obsidian
- `memory/YYYY-MM-DD.md` → `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/docs/贾维斯/memory/YYYY-MM-DD.md`
- `memory/detail/YYYY-MM-DD.md` → `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/docs/贾维斯/memory/detail/YYYY-MM-DD.md`

## 自检
- [ ] 逐条记录时间全部从 session 原始 timestamp 提取？
- [ ] 原始数据留了（URL、命令、错误信息）？
- [ ] 纯对话过滤了？
- [ ] 总结有审视角度（根因分析，不只是流水账）？
- [ ] 未完成事项列了？
- [ ] 两个文件都写了？
- [ ] Obsidian 两个文件都同步了？
