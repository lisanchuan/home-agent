# 【BibiGPT】AI 一键总结：[Claude Code 从 0 到 1 全攻略：MCP / SubAgent / Agent Skill / Hook / 图片 / 上下文处理/ 后台任务](https://bibigpt.co/video/BV14rzQB9EJj)

![](https://i1.hdslb.com/bfs/archive/c4653ea34ff39b4edb01130b2482f81d150f673e.jpg)

## 摘要
本视频详细讲解了 Claude Code 编程 Agent 的全方位实战流程。从基础的环境搭建、三种运行模式（默认、自动、规划）的切换，到进阶的功能定制，如 MCP（模型上下文协议）集成、上下文压缩、`.clinerules`（视频中以 `cloud.md` 代称）项目配置、Hook 自动格式化、以及 Agent Skill 和 Sub Agent 的高效应用。通过这些工具，用户能够将 Claude Code 打造为具备生产力的开发助手，实现复杂项目的自动化重构与协同管理。


### 亮点
- 💡 Claude Code 提供了三种核心模式：默认模式（谨慎询问）、自动模式（全权执行）和规划模式（仅讨论方案），通过 `Shift + Tab` 即可循环切换 [03:07]。
- 🛠️ 配合 `dangerously-skip-permissions` 参数虽然能极大提升自动化效率，但会赋予 Agent 极高的终端权限，使用时需评估安全风险 [07:22]。
- 🖼️ 使用 MCP 集成 Figma 工具，可以让 Claude Code 获取精准的设计上下文，从而更高效地还原设计稿的间距与样式 [15:58]。
- ⚙️ 通过 `.clinerules`（视频中称为 `cloud.md`）文件，可以为项目设定全局规则或注意事项，确保 Agent 在每次对话中都能遵循既定偏好 [18:50]。
- 🤖 Agent Skill 适合处理与上下文关联紧密的轻量级任务，而 Sub Agent 则拥有独立的上下文空间，最适合处理需要重度计算或审查的复杂工作 [24:45]。


#ClaudeCode #AI编程 #生产力工具 #MCP #开发实战


### 思考 
1. **Agent Skill 和 Sub Agent 的主要区别是什么？**
  - 两者核心区别在于对上下文的处理方式。Agent Skill 会共享当前主对话的上下文，适合处理轻量且需要上下文背景的任务（如生成每日总结）；Sub Agent 则会开启独立的对话窗口，拥有隔离的工具和记忆，非常适合处理重型任务（如代码审核），避免主对话被琐碎中间过程撑爆。
- 2. **如果 Claude Code 在重构项目后，我想回滚到之前的状态，应该怎么做？**
  - 可以通过输入 `[Esc][Esc]` 唤起回滚点菜单，选择特定时间点的快照进行恢复。需要注意的是，Claude Code 只能回滚它自身创建或修改的文件，对于通过终端命令（如 `mkdir`）生成的额外文件，建议配合 Git 进行版本管理以实现精准回滚。


### 术语解释
- **MCP (Model Context Protocol)**: 一种允许大模型与外界工具（如 Figma、数据库、GitHub）进行标准化通信的协议，极大扩展了 Agent 的能力边界。
- **Hook**: Claude Code 的功能点，允许在特定动作（如工具执行前后）自动触发一段自定义逻辑，例如利用 `Prettier` 在文件修改后自动格式化代码。
- **Sub Agent**: 具备独立上下文和工具集的子智能体，能够独立完成特定任务，保持主工作流的整洁与高效。
- **Plugin**: Claude Code 的插件体系，将 Skill、Sub Agent 和配置打包成“全家桶”，通过一键安装即可为项目赋予一套完整的解决方案。



## 视频章节总结 ｜ 🤖Claude Code从0到1：全功能实战攻略，彻底吃透AI编程Agent！

本视频提供了一份从入门到实践的Claude Code（一种编程Agent）全攻略，旨在帮助开发者将其应用于生产环境。视频首先介绍了Claude Code的环境搭建、登录认证（支持多种模型接入）及基础交互模式（默认、自动、规划模式）。随后，通过重构待办应用案例，深入讲解了如何处理复杂任务，包括通过终端命令进行文件操作、利用Plan Mode制定详细开发计划、以及如何利用Ctrl+G在VS Code中编辑需求。视频还详细演示了后台任务管理、代码回滚操作及如何通过图片或MCP工具与Figma设计稿进行精准交互。最后，作者介绍了上下文压缩、Cloud.md文件、Hook功能、Agent Skill以及Sub Agent的应用场景与区别，并展示了Plugin（插件）如何一键安装高级能力，极大地提升开发效率和代码质量。本教程内容丰富，实战性强，是全面掌握Claude Code的宝贵资源。

### [00:00](https://bibigpt.co/content/2f37036f-727c-4669-ac2c-37fe976a4cc7?t=0.000) - 🚀快速上手：环境搭建与基础交互

![章节截图 00:00](https://bibigpt-apps.chatvid.ai/screenshots/bilibili.com/BV14rzQB9EJj/0.jpg)

本章介绍了Claude Code的安装流程，包括通过官方命令进行安装，以及两种登录认证方式：订阅制和API Key。特别强调了Claude Code支持接入国产大模型。随后，通过创建一个代办应用，演示了Claude Code的三种核心交互模式：默认模式（谨慎确认）、自动模式（自动执行）和规划模式（讨论方案），并详细说明了它们各自的使用场景和切换方法（Shift+Tab）。

### [05:41](https://bibigpt.co/content/2f37036f-727c-4669-ac2c-37fe976a4cc7?t=341.000) - 🛠️复杂任务：项目重构与终端控制

![章节截图 05:41](https://bibigpt-apps.chatvid.ai/screenshots/bilibili.com/BV14rzQB9EJj/341.jpg)

本章以将简单的HTML代办应用重构为React+TypeScript+Vite架构为例，深入讲解了复杂任务的处理。内容包括如何在Claude Code中直接执行终端命令（如`open`），以及如何利用规划模式（Plan Mode）在进行重大架构修改前讨论和确定详细方案。此外，还介绍了通过Ctrl+G键在VS Code中便捷编辑长文本需求的方法，并展示了如何根据生成的计划选择执行模式或继续修改计划。

### [09:55](https://bibigpt.co/content/2f37036f-727c-4669-ac2c-37fe976a4cc7?t=595.640) - 🔄高效操作：后台任务与代码回滚

![章节截图 09:55](https://bibigpt-apps.chatvid.ai/screenshots/bilibili.com/BV14rzQB9EJj/595.64.jpg)

本章讲解了在项目开发中管理后台任务和进行代码回滚的关键技巧。演示了如何处理Claude Code在执行终端命令（如`npm install`）时的权限确认，并介绍了危险模式`dangerously-skip-permissions`的利弊。通过`npm run dev`启动开发服务器的案例，展示了如何使用Ctrl+B将任务放置后台运行，并通过`/tasks`命令查看和关闭任务。此外，还详细演示了如何使用两下ESC进入回滚页面，选择回滚点（代码和对话），以及回滚的局限性（终端命令生成的文件无法回滚）。

### [19:05](https://bibigpt.co/content/2f37036f-727c-4669-ac2c-37fe976a4cc7?t=1145.300) - 🖼️精准还原：图片与MCP工具交互

![章节截图 19:05](https://bibigpt-apps.chatvid.ai/screenshots/bilibili.com/BV14rzQB9EJj/1145.3.jpg)

本章聚焦于如何让Claude Code根据设计稿进行页面还原。首先介绍了通过拖拽或Ctrl+V粘贴图片，让Claude Code识别图片内容进行代码修改的方法。随后，引出了更为精确的MCP（Model Communication Protocol）机制。通过安装Figma MCP Server并进行认证，演示了如何让Claude Code调用Figma的MCP工具（如`get design context`、`get screenshot`）来获取设计稿的详细信息，从而实现高还原度的页面开发。

### [24:49](https://bibigpt.co/content/2f37036f-727c-4669-ac2c-37fe976a4cc7?t=1489.430) - 📦上下文管理：压缩与Cloud.md

![章节截图 24:49](https://bibigpt-apps.chatvid.ai/screenshots/bilibili.com/BV14rzQB9EJj/1489.43.jpg)

本章探讨了如何高效管理Claude Code的上下文信息，以优化性能和token消耗。介绍了`/compact`命令用于压缩上下文内容，并展示了压缩后的精简结果。同时，讲解了`/clear`命令用于清空所有上下文。更重要的是，详细介绍了Cloud.md文件的作用，它允许用户自定义项目或用户级别的预设信息、需求和注意事项，使Claude Code在每次启动时都能加载这些预设，提升工作的连贯性和准确性。

### [29:47](https://bibigpt.co/content/2f37036f-727c-4669-ac2c-37fe976a4cc7?t=1787.010) - 🔗高级扩展：Hook与Agent Skill

![章节截图 29:47](https://bibigpt-apps.chatvid.ai/screenshots/bilibili.com/BV14rzQB9EJj/1787.01.jpg)

本章深入讲解了Claude Code的两种高级扩展能力。Hook功能允许用户在特定时机（如工具使用前后、失败时）执行自定义逻辑，视频以实现代码自动格式化（通过Prettier）为例进行了详细演示，并介绍了Hook的保存级别（本地、项目、用户）。Agent Skill则是一个动态加载的Prompt，用于向大模型提供特定任务的说明书，视频通过创建“日报总结”Agent Skill，展示了如何让Claude Code遵循预设格式生成内容，并说明了主动调用Agent Skill的方法。

### [35:55](https://bibigpt.co/content/2f37036f-727c-4669-ac2c-37fe976a4cc7?t=2155.540) - 🤝协同工作：Sub Agent与Plugin

![章节截图 35:55](https://bibigpt-apps.chatvid.ai/screenshots/bilibili.com/BV14rzQB9EJj/2155.54.jpg)

本章介绍了Sub Agent和Plugin这两大协同工作利器。Sub Agent是一个拥有独立上下文、工具和Skill的独立Agent，适用于处理与主对话上下文关联小但影响大的任务（如代码审核），视频演示了如何创建和配置Sub Agent。最后，Plugin被描述为“全家桶安装包”，它将一系列Skill、Sub Agent、Hook等能力打包，实现一键安装。通过安装“Frontend Design”插件，展示了Plugin如何赋能Claude Code，让其生成更具现代审美的前端界面。

#BibiGPT https://bibigpt.co