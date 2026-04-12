# MiniMax Skills Repository

> **状态**：Beta — 活跃开发中

## 项目概述

**仓库**：[MiniMax-AI/skills](https://github.com/MiniMax-AI/skills)

面向 AI 编程工具的开发技能库，提供结构化、生产级质量的前端、全栈、Android、iOS 和着色器开发指导。

## 核心技能

### 开发类
| 技能 | 简介 |
|------|------|
| `frontend-dev` | React/Next.js + Tailwind，前端+UI动画+媒体资源生成 |
| `fullstack-dev` | REST API、认证、实时功能、数据库集成 |
| `android-native-dev` | Kotlin/Jetpack Compose，Material Design 3 |
| `ios-application-dev` | UIKit/SnapKit/SwiftUI，Apple HIG |
| `flutter-dev` | Widget模式、状态管理、导航 |
| `react-native-dev` | 组件、动画、导航、CI/CD |
| `shader-dev` | GLSL着色器，兼容ShaderToy |

### 媒体生成类
| 技能 | 简介 |
|------|------|
| `minimax-multimodal-toolkit` | TTS、音乐、视频、图片生成 |
| `minimax-music-gen` | 歌曲/纯音乐生成 |
| `gif-sticker-maker` | 照片转动画GIF |
| `minimax-pdf` | PDF生成/填写/重排 |
| `pptx-generator` | PowerPoint创建/编辑 |
| `minimax-xlsx` | Excel操作 |
| `minimax-docx` | Word文档创建/编辑 |
| `vision-analysis` | 图像分析/OCR |
| `minimax-music-playlist` | 智能歌单生成 |

## 安装支持

✅ Claude Code / ✅ Cursor / ✅ Codex / ✅ OpenCode / ❌ VS Code (无独立扩展) / ❌ OpenClaw (未支持)

## 与 OpenClaw 的关系

**结论：不兼容**

该仓库专为 Claude Code、Cursor、Codex、OpenCode 设计，是针对这些 AI 编程工具的插件/技能系统。

OpenClaw 使用的是 Skill（SKILL.md）机制，与 MiniMax Skills 的格式不同，不能直接复用。

## 价值评估

### 值得参考的场景：
- 技能设计规范（CONTRIBUTING.md、PR Review规则）
- 文档生成工具链（PDF/PPT/Excel/Word）的实现思路
- GLSL着色器的知识库

### 不能直接复用的：
- 技能文件格式（OpenClaw 不认这些 skill）
- 插件安装方式

## 参考链接

- 仓库：https://github.com/MiniMax-AI/skills
- 原始README：https://github.com/MiniMax-AI/skills/blob/main/README_zh.md

---
*抓取时间：2026-04-12*
