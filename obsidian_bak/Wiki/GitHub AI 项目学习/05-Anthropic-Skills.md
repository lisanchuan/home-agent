# Anthropic Skills 学习方案

## 项目概览
- **Stars**: 114,042
- **语言**: Markdown + Python/Bash Scripts
- **定位**: AI Skill 系统规范与示例，让 AI 学会使用工具
- **GitHub**: https://github.com/anthropics/skills
- **学习优先级**: ⭐⭐⭐⭐⭐（直接关联 OpenClaw 技能系统）

---

## 核心理念

> "Transform AI from a general-purpose agent into a specialized agent equipped with procedural knowledge"

**Skill = AI 的专项能力包**，让 AI 在特定领域做到专家水平。

## 学习路径

### 第一阶段：理解 Skill 架构（1-2天）

**一个 Skill 的结构：**
```
skill-name/
├── SKILL.md           # 必须：定义文件
├── scripts/           # 可选：可执行脚本
├── references/        # 可选：参考资料
└── assets/           # 可选：资源文件
```

**SKILL.md 结构：**
```yaml
---
name: pdf
description: >
  当用户想处理 PDF 文件时使用这个技能，包括读取、提取、合并、
  分割、OCR 等。触发词：PDF、PDF转Word、合并PDF、分割PDF。
---

# PDF 处理指南

## 快速开始
[使用说明]

## 详细用法
[代码示例]
```

### 第二阶段：三级加载机制（2-3天）

**渐进式加载，节省 Token：**

| 层级 | 内容 | 加载时机 |
|-----|------|---------|
| **L1** | name + description | 始终在 context |
| **L2** | SKILL.md body | skill 激活时 |
| **L3** | scripts/references | 按需加载 |

**学习案例：创建 PDF Skill**

```yaml
# SKILL.md frontmatter（L1 + L2）
---
name: pdf
description: >
  当用户提到 PDF 相关操作时使用：
  - "PDF 转 Word"
  - "合并 PDF"
  - "提取 PDF 文字"
  - "PDF 加密"
  - "PDF 解密"
  ...

# 详细指令（L2）
---

## 合并 PDF
使用 PyPDF2：
```python
from PyPDF2 import PdfMerger
merger = PdfMerger()
for pdf in ['a.pdf', 'b.pdf']:
    merger.append(pdf)
merger.write("merged.pdf")
```
```

### 第三阶段：Script 编写（3-4天）

**把重复操作写成脚本：**

```python
# scripts/rotate_pdf.py
"""
PDF 旋转脚本
用法: python rotate_pdf.py input.pdf --angle 90 --output output.pdf
"""
import argparse
from PyPDF2 import PdfReader, PdfWriter

def rotate_pdf(input_path, angle, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        page.rotate(rotation=int(angle))
        writer.add_page(page)
    
    with open(output_path, 'wb') as f:
        writer.write(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--angle", default=90)
    parser.add_argument("--output", default="output.pdf")
    args = parser.parse_args()
    rotate_pdf(args.input, args.angle, args.output)
```

### 第四阶段：创建自己的 Skill（3-5天）

**实战任务：创建一个"口琴谱分析 Skill"**

```yaml
# harmonica-beginner/SKILL.md
---
name: harmonica-beginner
description: >
  当用户想学习口琴或需要口琴谱时使用这个技能。
  包括：
  - "口琴入门"
  - "口琴谱"
  - "口琴教程"
  - "适合新手的口琴曲"
  - "口琴指法"
  - "口琴压音技巧"
---

# 口琴学习助手

## 初学者资源
[口琴选购建议]
[基础乐理]
[口琴谱怎么看]

## 练习曲目推荐
1. 小星星
2. 玛丽有只小羊羔
3. 欢乐颂
```

---

## Skill 创建方法论

**六步流程（来自 skill-creator skill）：**

```
1. Capture Intent     → 理解用户真正想要什么
2. Interview & Research → 追问细节，研究领域知识
3. Write SKILL.md     → 编写技能定义
4. Create Test Cases  → 建立测试用例
5. Run Eval           → 运行评估
6. Iterate            → 根据反馈迭代
```

---

## 对 OpenClaw 的直接借鉴

**这是最值得参考的 OpenClaw 技能系统来源：**

| Anthropic Skills | OpenClaw 对应 |
|-----------------|--------------|
| name + description | name + description |
| scripts/ | scripts/ |
| references/ | references/ |
| 三级加载 | 目前全量加载 |
| skill-creator | — |
| eval-viewer | — |

---

## 快速上手

```bash
# 克隆仓库
git clone https://github.com/anthropics/skills.git

# 查看现有 skills
ls skills/

# 看一个完整的 skill 示例
cat skills/pdf/SKILL.md
cat skills/docx/SKILL.md

# 看规范文档
cat spec/agent-skills-spec.md
```

---

## 学习资源

- **GitHub**: https://github.com/anthropics/skills
- **规范文档**: `spec/agent-skills-spec.md`
- **模板**: `template/SKILL.md`

---

## 适合人群

- 想构建 AI 技能系统的开发者
- 想给 OpenClaw 创建自定义技能的用户
- 想理解 AI Agent 工具调用机制的工程师

---

*学习方案由 AI 生成 · 2026-04-10*
