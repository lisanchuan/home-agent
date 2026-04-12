# CLI-Anything

> 让所有软件都能被 Agent 驱动

**项目地址**：https://github.com/HKUDS/CLI-Anything  
**文档**：https://github.com/HKUDS/CLI-Anything/blob/main/README_CN.md

---

## 是什么

CLI-Anything 是连接 AI Agent 与全世界软件的桥梁。通过一行命令，将任意有代码库的软件自动生成为完整的 CLI 接口，让 Agent（Claude Code、OpenClaw、Cursor、Codex 等）能够以结构化、可预测的方式操控专业软件。

**核心理念**：今天的软件为人而生，明天的用户是 Agent。

---

## 核心能力

### 一行命令生成完整 CLI

```
/cli-anything <软件路径或仓库>
```

7 阶段全自动流水线：
1. **分析** — 扫描源码，将 GUI 操作映射到 API
2. **设计** — 规划命令分组、状态模型、输出格式
3. **实现** — 构建 Click CLI（REPL、JSON 输出、撤销/重做）
4. **规划测试** — 生成 TEST.md（单元测试 + 端到端测试计划）
5. **编写测试** — 实现完整测试套件
6. **文档** — 更新 TEST.md，写入测试结果
7. **发布** — 生成 setup.py，安装到 PATH

### 优化已有 CLI

```
/cli-anything:refine <软件路径> [聚焦方向]
```

通过差距分析扩展功能覆盖面，增量、非破坏性。

---

## 支持的平台

| 平台 | 安装方式 |
|------|---------|
| Claude Code | 插件市场：`/plugin marketplace add HKUDS/CLI-Anything` |
| OpenClaw | 复制 SKILL.md 到 `~/.openclaw/skills/cli-anything/` |
| OpenCode | 复制命令到 `~/.config/opencode/commands/` |
| Codex | 运行安装脚本 |
| GitHub Copilot CLI | `copilot plugin install` |
| Qodercli | 运行 setup 脚本 |

---

## 实测软件（15 款）

| 软件 | 领域 | 测试数 |
|------|------|--------|
| GIMP | 图像编辑 | 107 |
| Blender | 3D 建模与渲染 | 208 |
| Inkscape | 矢量图形 | 202 |
| Audacity | 音频制作 | 161 |
| LibreOffice | 办公套件 | 158 |
| OBS Studio | 直播与录制 | 153 |
| Kdenlive | 视频剪辑 | 155 |
| Shotcut | 视频剪辑 | 154 |
| Openscreen | 屏幕录像 | 101 |
| Zoom | 视频会议 | 22 |
| Draw.io | 图表绘制 | 138 |
| Zotero | 文献管理 | 新增 |
| AnyGen | AI 内容生成 | 50 |
| Sketch | UI 设计 | 19 |

**总计：1,628 项测试，100% 通过**

---

## 使用方式

```bash
# 进入交互式 REPL
cli-anything-<软件名>

# JSON 模式供 Agent 消费
cli-anything-<软件名> --json <命令>

# 子命令模式
cli-anything-<软件名> project new --width 1920 --height 1080 -o poster.json
```

---

## 设计原则

- **真实软件集成** — CLI 生成合法项目文件，交给真实应用渲染
- **Agent 原生设计** — 内置 `--json` 参数，Agent 通过 `--help` 和 `which` 发现能力
- **零妥协** — 没有兜底，没有降级，后端缺失时测试直接失败
- **持久化状态** — 支持撤销/重做，统一 REPL 交互界面
- **多层验证** — 单元测试 + 端到端测试 + CLI 子进程验证

---

## 方法论（HARNESS.md）

关键经验：
- **必须用真实软件**：生成合法项目文件 → 调用真实后端
- **渲染鸿沟**：GUI 特效在渲染时才应用，不能用简陋导出工具替代
- **输出验证**：永远不要因为退出码为 0 就信任导出成功

---

## 适用场景

- 把专业软件变成 Agent 原生工具（GIMP、Blender、LibreOffice）
- 替代脆弱的 GUI 自动化（无需截图、点击像素）
- 自动生成评测 Benchmark（纯代码与终端操作）
- 整合零碎的 Web 服务 API 成统一 CLI
