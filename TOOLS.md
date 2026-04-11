# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Video Analysis

- **BibiGPT** 是视频分析专用 skill，所有涉及视频分析的请求都使用它
- 安装路径：`~/.openclaw/skills/bibi/SKILL.md`
- 命令：`bibi summarize "<URL>" --json`
- 支持平台：YouTube、B站、其他视频/音频
- 使用场景：总结视频、提取字幕、章节分析、术语解释

## Obsidian Sync

- 路径：`/Users/lisanchuan1/Library/Mobile Documents/iCloud~md~obsidian/Documents/docs`
- 工具：`src/tools/obsidian_sync.py`
- 流程：视频 → BibiGPT 分析 → 整理成文章 → 保存到 Obsidian

## 贾维斯记忆库

- **Obsidian Vault**：`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/docs/贾维斯/`
- **目录结构**：
  - `memory/` - 每日记忆（2026-04-08 起）
  - `agents/` - TASK_LOG、ISSUE_LOG
  - `MEMORY.md` - 长期记忆
- **同步**：通过 iCloud 自动同步到各设备
- **查看**：在 Obsidian 中打开 vault 即可
