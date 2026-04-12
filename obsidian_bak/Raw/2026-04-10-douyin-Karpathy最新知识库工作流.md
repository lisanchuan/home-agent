---
uid: raw-karpathy-workflow-03
created: 2026-04-10
source: https://www.douyin.com/video/7624384063805099302
tags:
  - raw
  - video
  - douyin
  - Karpathy
  - 知识管理
---

# 视频笔记：Karpathy最新工作流：用AI编译个人知识库

## 原始信息
- **链接**：https://www.douyin.com/video/7624384063805099302
- **平台**：抖音
- **日期**：2026-04-10

## 视频摘要
Karpathy 分享了他近期构建的个人知识库工作流，核心逻辑在于将碎片化的论文、代码和文章通过"收集、编译、查询"三个步骤转化为系统化的 Wiki。该方案在处理约 40 万字量级的数据时，无需复杂的 RAG 向量检索，仅靠 LLM 自我维护的索引即可实现高效检索。

## 核心要点
- 三阶段工作流：收集原始资料 → LLM 编译为带反向链接的知识网络 → 交互式查询
- 40 万字规模下不需要 RAG，LLM 上下文能力足够
- 知识库自我进化：优秀查询结果归档回 Wiki
- 可直接生成 Markdown、幻灯片、图表，在 Obsidian 渲染

## 处理状态
- [x] 已分析
- [ ] 已提炼到 Wiki
- [ ] 已建立链接

## 相关链接
- [[Wiki/知识管理/Karpathy最新知识库工作流]]
