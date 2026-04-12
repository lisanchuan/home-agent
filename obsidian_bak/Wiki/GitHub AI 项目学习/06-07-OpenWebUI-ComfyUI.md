# Open WebUI + ComfyUI 学习方案

## 项目概览

| 项目 | Stars | 语言 | 定位 |
|-----|-------|-----|------|
| **Open WebUI** | 130,987 | Python | AI 聊天界面，支持 Ollama/OpenAI |
| **ComfyUI** | 108,275 | Python | 节点式 Diffusion 工作流 |

**关联性**：都是**AI 界面层**，一个做聊天，一个做绘图。可以用同一套思维理解。

---

## Open WebUI 学习方案

### 核心理念

> "User-friendly AI Interface"

**本质**：给 Ollama（本地 LLM）做一个 ChatGPT 级别的 Web 界面。

### 学习路径

#### 第一阶段：快速部署（1天）

```bash
# Docker 部署
docker run -d -p 3000:8080 \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# 或用 Ollama 一起
docker run -d -p 11434:11434 ollama/ollama
docker run -d -p 3000:8080 ghcr.io/open-webui/open-webui:main
```

#### 第二阶段：理解架构（3-4天）

**核心模块：**
```
open-webui/
├── backend/
│   ├── api/          # FastAPI 路由
│   ├── models/      # 模型管理
│   ├── services/    # 核心服务
│   └── main.py
└── frontend/        # React 前端
```

**关键设计：**
- 支持多模型（Ollama、OpenAI、Azure）
- RAG 知识库支持
- 聊天历史管理
- 多用户协作

#### 第三阶段：二次开发（5-7天）

**实战任务：添加自定义 API 端点**

```python
# backend/api/v1/custom.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/my-tool")
async def my_tool(text: str):
    # 自定义工具逻辑
    return {"result": text.upper()}
```

---

## ComfyUI 学习方案

### 核心理念

> "The most powerful and modular diffusion model GUI"

**本质**：用**节点图**而非代码来构建 Diffusion 工作流。

### 学习路径

#### 第一阶段：界面熟悉（1-2天）

**基础操作：**
1. 双击空白处 → 搜索节点
2. 右键 → 管理节点
3. Ctrl + 拖拽 → 连接节点

**基础节点：**
- Load Checkpoint（加载模型）
- CLIP Text Encode（输入提示词）
- KSampler（采样生成）
- Save Image（保存结果）

#### 第二阶段：工作流理解（3-4天）

**典型工作流：**
```
Checkpoint (模型)
    ↓
CLIP Text Encode (正面提示词)
    ↓
KSampler (采样器) ← 需要负面提示词
    ↓
VAE Decode
    ↓
Save Image
```

**学习案例：图生图（img2img）**

```
Load Image → VAE Encode → KSampler → VAE Decode → Save Image
     ↑
CLIP Text Encode (提示词)
```

#### 第三阶段：自定义节点开发（5-7天）

**实战任务：创建自定义节点**

```python
# my_node.py
import torch
from nodes import Node

class ImageBlur(Node):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "radius": ("INT", {"default": 5, "min": 1, "max": 50}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "blur"
    
    def blur(self, image, radius):
        # 使用 torchvision 进行模糊
        from torchvision import transforms
        blur = transforms.GaussianBlur(radius)
        result = blur(image)
        return (result,)
```

---

## 关联学习：构建 AI 画图 + 聊天系统

**组合方案：用 Open WebUI + ComfyUI 构建完整 AI 平台**

```
用户聊天 → Open WebUI (对话)
              ↓
         检测到画图需求
              ↓
         调用 ComfyUI API 生成图片
              ↓
         返回图片给用户
```

```python
# Open WebUI 后端调用 ComfyUI
import aiohttp

async def generate_with_comfy(prompt: str):
    # 构建 ComfyUI 工作流
    workflow = {...}
    
    # 提交到 ComfyUI
    async with aiohttp.ClientSession() as session:
        await session.post("http://localhost:8188/prompt", json=workflow)
```

---

## 对 OpenClaw 的借鉴

| 项目 | 借鉴点 |
|-----|--------|
| **Open WebUI** | Web 界面设计、模型管理、RAG 知识库 |
| **ComfyUI** | 节点式工作流、模块化架构、自定义节点开发 |

**可以借鉴**：ComfyUI 的节点图思维可以用在 OpenClaw 的 Tool 编排上。

---

## 快速上手

**Open WebUI：**
```bash
# Docker 最简单
docker run -d -p 3000:8080 ghcr.io/open-webui/open-webui:main
```

**ComfyUI：**
```bash
# 下载 portable 版
# Windows: 下载 exe 运行
# 或源码
git clone https://github.com/Comfy-Org/ComfyUI.git
pip install -r requirements.txt
python main.py
```

---

## 适合人群

- 想部署本地 AI 聊天界面的开发者
- 想学习 Diffusion 模型工作流的工程师
- 想构建 AI 画图 + 聊天混合应用的团队

---

*学习方案由 AI 生成 · 2026-04-10*
