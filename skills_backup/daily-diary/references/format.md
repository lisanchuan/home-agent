# 日记 vs 其他日志文件

| 文件 | 触发 | 格式 | 用途 |
|------|------|------|------|
| memory/YYYY-MM-DD.md | 定时 23:00 / 手动触发 | 逐条含原始数据 | 回答「那天发生了什么」「为什么」 |
| TASK_LOG.md | 每任务完成后 | 单条记录 | 任务追踪 |
| ISSUE_LOG.md | 每次失败时 | 根因分析 | 问题追踪 |
| MEMORY.md | 定期维护 | 摘要精华 | 跨会话记忆 |

---

# 如何从 session 提取数据

## Session 文件位置
`~/.openclaw/agents/main/sessions/*.jsonl`

## 文件格式
JSONL，每行一个 message object：
```json
{"role":"user","content":"...","timestamp":1744502400000}
{"role":"assistant","content":"...","timestamp":1744502405000}
```

## 提取脚本思路

```python
import json
from pathlib import Path
from datetime import datetime

sessions_dir = Path.home() / ".openclaw/agents/main/sessions"
today = datetime.now().strftime("%Y-%m-%d")

for f in sessions_dir.glob("*.jsonl"):
    messages = []
    for line in f.read_text().splitlines():
        msg = json.loads(line)
        ts = msg.get("timestamp")
        if ts:
            dt = datetime.fromtimestamp(ts / 1000)
            if dt.strftime("%Y-%m-%d") == today:
                messages.append((dt, msg))
    
    # 按时间排序输出
    for dt, msg in sorted(messages):
        print(f"{dt.strftime('%H:%M')} [{msg['role']}] {msg['content'][:200]}")
```

## 判断用户要求是否有实质内容

```python
def is_meaningful(user_msg: str) -> bool:
    skip = ["好的", "知道了", "谢谢", "OK", "ok", "嗯", "好"]
    return not any(user_msg.strip().startswith(s) for s in skip)
```

---

# 原始数据记录原则

## 哪些要留

| 类型 | 留什么 |
|------|--------|
| URL | 完整 URL 原文 |
| 命令 | 完整命令原文 |
| JSON/数据 | 关键字段截取 |
| 错误信息 | 完整 error message |
| sub-agent sessionKey | 完整 key |

## 哪些不单独成条

- 纯对话（「好的」「知道了」「谢谢」「嗯」）
- 正常的心跳检测（无异常时）
