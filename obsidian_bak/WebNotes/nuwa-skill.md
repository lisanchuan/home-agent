# 女娲 (nuwa-skill) — 认知蒸馏框架

> **GitHub**: https://github.com/alchaincyf/nuwa-skill  
> **作者**: 花叔 Huashu（独立开发者，代表作：小猫补光灯）  
> **许可证**: MIT  
> **状态**: ⭐ 活跃项目

---

## 项目描述

**女娲** 是一个 Claude Code Skill，用于将任何公众人物的**思维方式**蒸馏成可运行的 AI Skill。

核心理念：
> 「你想蒸馏的下一个员工，何必是同事」  
> 既然能蒸馏人，为何只蒸馏身边的同事？去蒸馏乔布斯、芒格、费曼、马斯克。

**不是角色扮演，是认知架构提取。**

---

## 核心功能

1. **蒸馏任意人物** — 输入名字，自动完成调研→提炼→验证全流程
2. **内置 13 个人物 Skill + 1 个主题 Skill** — 可独立安装使用
3. **五层认知提取**：
   - 怎么说话（表达DNA）
   - 怎么想（心智模型）
   - 怎么判断（决策启发式）
   - 什么不做（反模式）
   - 知道局限（诚实边界）

---

## 技术栈 / 依赖

- **平台**: Claude Code / [skills.sh](https://skills.sh) 生态
- **安装方式**: `npx skills add alchaincyf/nuwa-skill`
- **技术实现**: 基于 AI Agent 多路并行采集 + 三重验证提炼
- **输出格式**: SKILL.md（符合 Claude Code Skill 规范）

---

## 工作原理

1. **六路并行采集** — 著作、播客/访谈、社交媒体、批评者视角、决策记录、人生时间线，6个Agent同时跑
2. **三重验证提炼** — 跨领域验证 + 预测力验证 + 排他性验证
3. **构建Skill** — 3-7个心智模型 + 5-10条决策启发式 + 表达DNA + 价值观与反模式 + 诚实边界
4. **质量验证** — 用此人公开回答过的问题测试方向一致性

---

## 已蒸馏人物（13人）

| 人物 | 领域 | 仓库 |
|------|------|------|
| 🔥 Paul Graham | 创业/写作/产品/人生哲学 | [paul-graham-skill](https://github.com/alchaincyf/paul-graham-skill) |
| 🔥 张一鸣 | 产品/组织/全球化/人才 | [zhang-yiming-skill](https://github.com/alchaincyf/zhang-yiming-skill) |
| 🔥 Karpathy | AI/工程/教育/开源 | [karpathy-skill](https://github.com/alchaincyf/karpathy-skill) |
| 🔥 Ilya Sutskever | AI安全/scaling/研究品味 | [ilya-sutskever-skill](https://github.com/alchaincyf/ilya-sutskever-skill) |
| 🔥 MrBeast | 内容创造/YouTube方法论 | [mrbeast-skill](https://github.com/alchaincyf/mrbeast-skill) |
| 🔥 特朗普 | 谈判/权力/传播/行为预判 | [trump-skill](https://github.com/alchaincyf/trump-skill) |
| ⭐ 乔布斯 | 产品/设计/战略 | [steve-jobs-skill](https://github.com/alchaincyf/steve-jobs-skill) |
| 马斯克 | 工程/成本/第一性原理 | [elon-musk-skill](https://github.com/alchaincyf/elon-musk-skill) |
| 芒格 | 投资/多元思维/逆向思考 | [munger-skill](https://github.com/alchaincyf/munger-skill) |
| 费曼 | 学习/教学/科学思维 | [feynman-skill](https://github.com/alchaincyf/feynman-skill) |
| Naval | 财富/杠杆/人生哲学 | [naval-skill](https://github.com/alchaincyf/naval-skill) |
| 塔勒布 | 风险/反脆弱/不确定性 | [taleb-skill](https://github.com/alchaincyf/taleb-skill) |
| 张雪峰 | 教育/职业规划/阶层流动 | [zhangxuefeng-skill](https://github.com/alchaincyf/zhangxuefeng-skill) |
| X导师 | X/Twitter运营全栈 | [x-mentor-skill](https://github.com/alchaincyf/x-mentor-skill) |

---

## 与 OpenClaw 的兼容性分析

### ⚠️ 平台绑定

女娲是 **Claude Code 原生 Skill**，安装方式为 `npx skills add`，与 Claude Code 的 skills.sh 生态深度绑定。

### ❌ OpenClaw 兼容性：**不直接兼容**

原因：
1. **Skill 格式不同** — Claude Code 的 SKILL.md 格式与 OpenClaw 的 `SKILL.md` 规范不同
2. **安装机制不同** — `npx skills add` 是 Claude Code 特有的命令
3. **运行时依赖** — 女娲依赖 Claude Code 的 Agent 框架和指令注入机制

### ✅ 可迁移的内容

以下内容可以**参考或迁移**到 OpenClaw：

- **方法论** (`references/extraction-framework.md`) — 认知蒸馏的流程和验证标准
- **心智模型结构** — 五层认知提取框架
- **人物知识库** — 13个人的认知框架数据（JSON/Markdown格式）

### 🔄 可能的集成方式

1. **作为知识库使用** — 将各人物的心智模型文档导入 OpenClaw 作为参考资料
2. **参考方法论构建 OpenClaw Skill** — 将女娲的五层提取法复用到 OpenClaw Skill 创作中
3. **WebNotes 备份** — 定期同步更新人物库到 Obsidian

---

## 诚实边界（女娲自己标注的局限）

- **蒸馏不了直觉** — 框架能提取，灵感不能
- **捕捉不了突变** — 截止到调研时间的快照
- **公开表达 ≠ 真实想法** — 只能基于公开信息

---

## 总结评价

| 维度 | 评分 | 说明 |
|------|------|------|
| 概念创新 | ⭐⭐⭐⭐⭐ | 认知蒸馏理念独特，不是角色扮演 |
| 工程完整度 | ⭐⭐⭐⭐⭐ | 方法论 + 工具 + 13个具体Skill |
| OpenClaw 兼容性 | ⭐⭐ | 平台绑定，不直接可用 |
| 知识价值 | ⭐⭐⭐⭐⭐ | 13位人物的心智模型有极高参考价值 |
| 可持续性 | ⭐⭐⭐⭐ | MIT 许可，活跃维护 |

### 是否值得在 OpenClaw 中使用？

**部分值得**：
- ✅ 方法论值得借鉴（skill-creator 可参考）
- ✅ 人物心智模型可作为知识库
- ❌ 原生 Skill 无法直接安装使用

**建议**：将 `extraction-framework.md` 和各人物视角文档作为研究素材，而非直接集成的 Skill。

---

*最后更新: 2026-04-12*
