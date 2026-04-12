---
title: "OpenClaw ACP 协议：飞书远程调用 CloudCode"
source: "https://www.bilibili.com/video/BV1abXpBjEEF/"
platform: "bilibili"
date: "2026-04-12"
duration: "~10 min"
tags: [video-summary, OpenClaw, ACP, CloudCode]
---

# OpenClaw ACP 协议：飞书远程调用 CloudCode

本视频介绍了如何利用 OpenClaw 的 ACP（Agent Communication Protocol）协议，在飞书平台上远程调用 CloudCode 等专业编程 Agent。通过配置 ACP 插件，用户可以在飞书端直接指挥底层代码工具完成复杂的工程化开发任务，实现了专业编程 Agent 与多功能管理 Agent 的强强联合，极大地提升了移动端进行代码开发和工程化管理的灵活性与效率。

## 亮点

- OpenClaw 通过 ACP 协议实现了与 CloudCode 等专业编程 Agent 的深度联动，弥补了通用 Agent 在复杂工程化场景下的短板 [00:46]。
- 用户在更新 OpenClaw 至 0323 版本后，需安装 ACPX 插件并配置 `open-claw.json`，将 `default_agent` 指定为 `cloud-code` 或 `open-code` 以完成底层对接 [02:35]。
- 在飞书环境中使用时，通过 `!sap` 命令加上特定的 Session ID，可以精准地让底层代码 Agent 接手任务并进行持续的开发与优化 [04:35]。
- 相比于让通用 Agent 直接写代码，ACP 协议调用专业工具能提供更稳定的工程化输出，并有效避免模型在复杂任务中产生幻觉 [08:35]。
- 该方案打破了编程地点的限制，让开发者能够利用移动端的飞书远程操控电脑终端的编程 Agent，真正实现了多 Agent 协作的高级玩法 [09:35]。

## 思考

1. **在飞书中使用 ACP 调用 CloudCode 时，为什么不能直接使用 `!focus` 命令？**
   - 目前飞书插件版本对于持久化会话的绑定功能尚不支持，该命令主要针对 Discord 等平台设计。因此，在飞书上需要通过 `!sap` 命令携带 Session ID 来明确指定当前的对话上下文。

2. **为什么推荐通过显式的命令（如 `!sap`）来调用编程 Agent，而不是直接通过聊天让 OpenClaw 自己生成？**
   - 直接聊天可能导致模型出现"幻觉"，即模型误以为自己具备编写复杂工程的能力，从而导致任务执行失败。使用显式命令可以确保任务确切地分发给底层的专业编程 Agent，大幅提高了任务执行的确定性和成功率。

## 术语解释

- **ACP (Agent Communication Protocol)**: 一种代理通信协议，旨在实现不同 Agent 或命令行工具之间的标准化联动与任务分发。
- **Agent**: 在这里指代具备特定功能（如编程、聊天、任务管理）的 AI 智能体，OpenClaw 通过此架构实现多代理协同。
- **CloudCode**: 一款专注于工程化编程的 Agent，内置了针对复杂代码任务优化的提示词和协作团队功能，比通用模型更适合大型项目开发。
- **Session (会话)**: 指通过 ACP 开启的一个持续任务状态，允许开发者对同一个代码工程进行多次连续的指令操作和优化。

#OpenClaw #ACP协议 #CloudCode #AI编程 #飞书集成

---
*Summarized by [BibiGPT](https://bibigpt.co)*
