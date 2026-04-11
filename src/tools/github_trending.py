#!/usr/bin/env python3
"""
GitHub Trending AI 分析器
生成中文 GitHub AI 周报（Trending + Deep Dive 整合版）
"""

import subprocess
import json
import sys
import os
import re
from datetime import datetime, timedelta

OUTPUT_DIR = "/Users/lisanchuan1/.openclaw/workspace/data/github_trending"
REPORT_FILE = f"{OUTPUT_DIR}/latest.md"
DATA_FILE = f"{OUTPUT_DIR}/repos.json"

AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "ml",
    "deep learning", "neural", "llm", "gpt", "transformer",
    "nlp", "cv", "computer vision", "reinforcement learning",
    "generative", "diffusion", "stable diffusion", "langchain",
    "agent", "rag", "vector db", "embedding", "hugging face",
    "openai", "claude", "gemini", "ollama", "vllm", "llama",
    "skill", "claude code", "cursor", "copilot", "codex",
    "autogpt", "crewai", "dify", "anything llm", "openwebui",
    "Nous", "Qwen", "DeepSeek", "Groq", "Mistral"
]

EXCLUDE_KEYWORDS = [
    "public-api", "free api", "programming book", "system design",
    "algorithm", "tutorial", "cheatsheet", "awesome list",
    "youtube downloader", "video download"
]

# 翻译短语映射（按长度降序排列，避免部分匹配）
PHRASES = [
    # 高优先级短语（越长越往前）
    ("a web interface for", "的一个 Web 界面，用于"),
    ("web interface for", "的 Web 界面，用于"),
    ("Web Interface for", "Web 界面，用于"),
    ("User-friendly AI Interface", "用户友好的 AI 界面，支持"),
    ("AI Interface for", "AI 界面，用于"),
    ("self-hostable", "可自托管的"),
    ("open-source", "开源"),
    ("artificial intelligence", "人工智能"),
    ("machine learning", "机器学习"),
    ("deep learning", "深度学习"),
    ("large language model", "大语言模型"),
    ("language model", "语言模型"),
    ("multimodal model", "多模态模型"),
    ("vision language model", "视觉语言模型"),
    ("foundation model", "基础模型"),
    ("generative AI", "生成式 AI"),
    ("diffusion model", "扩散模型"),
    ("stable diffusion", "Stable Diffusion"),
    ("text-to-image", "文生图"),
    ("image-to-image", "图生图"),
    ("image generation", "图像生成"),
    ("text generation", "文本生成"),
    ("speech recognition", "语音识别"),
    ("speech synthesis", "语音合成"),
    ("autonomous agent", "自主智能体"),
    ("autonomous agents", "自主智能体"),
    ("agent framework", "智能体开发框架"),
    ("agent engineering", "智能体工程"),
    ("agent orchestration", "智能体编排"),
    ("multi-agent", "多智能体"),
    ("vector database", "向量数据库"),
    ("vector search", "向量检索"),
    ("retrieval-augmented", "检索增强"),
    ("REST API", "REST API"),
    ("GraphQL API", "GraphQL API"),
    ("GPU-accelerated", "GPU 加速"),
    ("computer vision", "计算机视觉"),
    ("natural language processing", "自然语言处理"),
    ("named entity recognition", "命名实体识别"),
    ("knowledge base", "知识库"),
    ("knowledge graph", "知识图谱"),
    ("sentiment analysis", "情感分析"),
    ("text classification", "文本分类"),
    ("fine-tuning", "微调"),
    ("knowledge graph", "知识图谱"),
    # 中等优先级
    ("command-line", "命令行"),
    ("production-ready", "生产就绪"),
    ("battle-tested", "经过验证"),
    ("easy-to-use", "简单易用"),
    ("easy to use", "简单易用"),
    ("state-of-the-art", "最先进"),
    ("cutting-edge", "前沿技术"),
    ("conversational AI", "对话 AI"),
    ("conversational", "对话式"),
    ("building and deploying", "构建和部署"),
    ("build and deploy", "构建和部署"),
    ("cloud native", "云原生"),
    ("privacy-preserving", "隐私保护"),
    ("self-hosted", "自托管"),
    ("serverless", "无服务器"),
    ("graphical user interface", "图形界面"),
    ("graph/nodes interface", "图形化节点界面"),
    ("orchestration", "编排"),
    ("orchestrate", "编排"),
    # 工具/框架/平台
    ("framework for", "框架，用于"),
    ("framework to", "框架，用于"),
    ("library for", "工具库，用于"),
    ("tool for", "工具，用于"),
    ("tools for", "工具，用于"),
    ("platform for", "平台，用于"),
    ("platform to", "平台，用于"),
    ("API for", "API，用于"),
    ("API to", "API，用于"),
    ("web API", "Web API"),
    # 基础词
    ("generative", "生成式"),
    ("agents", "智能体"),
    ("agent", "智能体"),
    ("embedding", "嵌入向量"),
    ("transformer", "Transformer"),
    ("neural network", "神经网络"),
    ("pretrained", "预训练"),
    ("pre-trained", "预训练"),
    ("inference", "推理"),
    ("batch inference", "批量推理"),
    ("deployment", "部署"),
    ("deploying", "部署"),
    ("deploy", "部署"),
    ("automation", "自动化"),
    ("automate", "自动化"),
    ("workflow", "工作流"),
    ("chatbot", "聊天机器人"),
    ("chat interface", "聊天界面"),
    ("web interface", "Web 界面"),
    ("collection of", "精选合集，包含"),
    ("awesome", "精选"),
    ("modular", "模块化"),
    ("scalable", "可扩展"),
    ("extensible", "可扩展"),
    ("lightweight", "轻量级"),
    ("performant", "高性能"),
    ("powerful", "强大"),
    ("simple to use", "简单易用"),
    ("llama", "LLaMA"),
    ("qwen", "Qwen"),
    ("deepseek", "DeepSeek"),
    ("groq", "Groq"),
    ("ollama", "Ollama"),
    ("vllm", "vLLM"),
    ("mistral", "Mistral"),
    ("claude", "Claude"),
    ("gemini", "Gemini"),
    ("cuda", "CUDA"),
    ("python", "Python"),
    ("rust", "Rust"),
    ("typescript", "TypeScript"),
    ("javascript", "JavaScript"),
    ("docker", "Docker"),
    ("kubernetes", "Kubernetes"),
    ("fine-tune", "微调"),
    ("training", "训练"),
    ("real-time", "实时"),
    ("privacy-first", "隐私优先"),
    ("local-first", "本地优先"),
    ("on-premise", "本地部署"),
    ("summarization", "摘要生成"),
    ("summarize", "摘要"),
    ("translation", "翻译"),
    ("hugging face", "Hugging Face"),
    ("openai", "OpenAI"),
    ("anthropic", "Anthropic"),
    ("no-code", "无代码"),
    ("low-code", "低代码"),
    ("GUI", "图形界面"),
]


def translate_en_to_zh(text):
    """把英文翻译成中文（规则映射 + 词边界替换）"""
    if not text:
        return ""

    result = text

    # 短语替换（精准匹配，避免子串干扰）
    for en, zh in PHRASES:
        result = result.replace(en, zh).replace(en.lower(), zh)

    # 词边界替换（保护短词不被误替换）
    # 只替换单独成词的，不替换嵌入在其他词里的
    result = re.sub(r'\bGUI\b', '图形界面', result)
    result = re.sub(r'\bUI\b', '界面', result)
    result = re.sub(r'\bapi\b', 'API', result)
    result = re.sub(r'\bLLM\b', '大语言模型', result)

    # 清理残留空格
    for _ in range(4):
        result = result.replace("  ", " ")

    return result.strip()


def translate_description(desc):
    """翻译 description"""
    if not desc:
        return "暂无描述"

    result = translate_en_to_zh(desc)
    if len(result) > 80:
        result = result[:80] + "…"
    return result


def gh_graphql(query, variables=None):
    """执行 GitHub GraphQL 查询"""
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    if variables:
        for k, v in variables.items():
            cmd.extend(["-f", f"{k}={v}"])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"GH API error: {result.stderr}")
        return None

    return json.loads(result.stdout)


def fetch_recent_repos(days=14, min_stars=500):
    """获取最近 N 天创建的高星项目"""
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    query = """
    query($search: String!) {
      search(query: $search, type: REPOSITORY, first: 50) {
        nodes {
          ... on Repository {
            nameWithOwner
            description
            primaryLanguage { name }
            stargazerCount
            pushedAt
            createdAt
            url
          }
        }
      }
    }
    """

    variables = {"search": f"created:>{date_from} stars:>{min_stars}"}
    data = gh_graphql(query, variables)
    if not data:
        return []

    return data.get("data", {}).get("search", {}).get("nodes", [])


def fetch_trending_repos(language=None):
    """获取 Trending 仓库"""
    query = """
    query($search: String!) {
      search(query: $search, type: REPOSITORY, first: 30) {
        nodes {
          ... on Repository {
            nameWithOwner
            description
            primaryLanguage { name }
            stargazerCount
            url
          }
        }
      }
    }
    """

    search = "stars:>1000"
    if language:
        search += f" language:{language}"

    variables = {"search": search}
    data = gh_graphql(query, variables)
    if not data:
        return []

    return data.get("data", {}).get("search", {}).get("nodes", [])


def filter_ai_repos(repos):
    """过滤 AI/ML 相关项目"""
    ai_repos = []
    for repo in repos:
        name = repo.get("nameWithOwner", "").lower()
        desc = (repo.get("description", "") or "").lower()
        text = f"{name} {desc}"

        if any(ex in text for ex in EXCLUDE_KEYWORDS):
            continue

        if not any(kw.lower() in text for kw in AI_KEYWORDS):
            continue

        ai_repos.append(repo)

    return ai_repos


def rank_repos(repos, fresh_weight=3):
    """加权排序：新项目优先"""
    now = datetime.now()

    def score(repo):
        stars = repo.get("stargazerCount", 0)
        pushed_str = repo.get("pushedAt")

        freshness = 0
        if pushed_str:
            try:
                pushed = datetime.fromisoformat(pushed_str.replace("Z", "+00:00"))
                days_old = (now - pushed).total_seconds() / 86400
                freshness = max(0, (7 - days_old) / 7) * stars * fresh_weight
            except:
                pass

        return stars + freshness

    return sorted(repos, key=score, reverse=True)


def get_repo_topics(owner, repo_name):
    """获取仓库 topic"""
    result = subprocess.run(
        ["gh", "api", f"/repos/{owner}/{repo_name}/topics"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout)
        return data.get("names", [])
    except:
        return []


def get_readme_snippet(owner, repo_name):
    """获取 README 开头（用于生成简介）"""
    try:
        result = subprocess.run(
            ["gh", "api", f"/repos/{owner}/{repo_name}/readme"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return None
        import base64
        data = json.loads(result.stdout)
        content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
        return content[:600].replace("#", "").replace("\n", " ").strip()
    except Exception:
        return None


def generate_trending_section(repos, top_n=10):
    """生成热门项目章节"""
    lines = ["## 🔥 热门 AI 项目\n"]

    sorted_repos = sorted(repos, key=lambda x: x.get("stargazerCount", 0), reverse=True)[:top_n]

    for i, repo in enumerate(sorted_repos, 1):
        name = repo.get("nameWithOwner", "")
        desc_raw = repo.get("description", "") or "无描述"
        desc = translate_description(desc_raw)
        lang = repo.get("primaryLanguage", {}).get("name", "") if repo.get("primaryLanguage") else ""
        stars = repo.get("stargazerCount", 0)
        url = repo.get("url", "")

        lines.append(f"### {i}. {name}")
        lines.append(f"- {desc}")
        lines.append(f"- ⭐ {stars:,} | {'语言: ' + lang if lang else '多语言'}")
        lines.append(f"- 🔗 {url}")
        lines.append("")

    return "\n".join(lines)


def generate_deepdive_section(repos, top_n=5):
    """生成深度分析章节"""
    lines = ["## 🧠 深度分析（Top 5）\n"]

    top_repos = repos[:top_n]

    for i, repo in enumerate(top_repos, 1):
        name = repo.get("nameWithOwner", "")
        owner, repo_name = name.split("/") if "/" in name else (name, name)
        desc_raw = repo.get("description", "") or "无描述"
        desc_zh = translate_description(desc_raw)
        stars = repo.get("stargazerCount", 0)
        lang = repo.get("primaryLanguage", {}).get("name", "") if repo.get("primaryLanguage") else ""
        topics = get_repo_topics(owner, repo_name)
        topics_str = " · ".join(topics[:5]) if topics else ""

        lines.append(f"### {i}. {name}")
        lines.append(f"- ⭐ {stars:,} | {'语言: ' + lang if lang else '多语言'}")
        lines.append(f"- {desc_zh}")
        if topics_str:
            lines.append(f"- 🏷️ {topics_str}")

        # 生成中文简介（翻译 README 片段）
        readme = get_readme_snippet(owner, repo_name)
        if readme:
            summary_zh = translate_en_to_zh(readme)
            if len(summary_zh) > 80:
                summary_zh = summary_zh[:80] + "…"
            lines.append(f"- 📖 {summary_zh}")

        lines.append("")

    return "\n".join(lines)


def generate_report(repos):
    """生成完整报告（整合版）"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    today_str = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# GitHub AI 周报",
        f"生成时间：{now}",
        f"共 {len(repos)} 个 AI 相关项目",
        ""
    ]

    lines.append(generate_trending_section(repos, top_n=10))
    lines.append("")
    lines.append(generate_deepdive_section(repos, top_n=5))
    lines.append("")
    lines.extend([
        "---",
        f"*由 AI 自动生成 · {now}*"
    ])

    return "\n".join(lines), today_str


def save_to_obsidian(content, date_str):
    """同步到 Obsidian Raw 目录"""
    obsidian_path = f"/Users/lisanchuan1/Library/Mobile Documents/iCloud~md~obsidian/Documents/docs/Raw/{date_str}-github-ai-weekly.md"

    try:
        with open(obsidian_path, "w") as f:
            f.write(content)
        print(f"✅ 已同步到 Obsidian：{obsidian_path}")
        return True
    except Exception as e:
        print(f"⚠️ Obsidian 同步失败：{e}")
        return False


def main():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("📡 获取 GitHub 热门仓库...")

    all_repos = []
    seen = set()

    print("  - 抓取近期高星项目...")
    recent = fetch_recent_repos(days=14, min_stars=500)
    for repo in recent:
        key = repo.get("nameWithOwner", "")
        if key and key not in seen:
            seen.add(key)
            all_repos.append(repo)

    print("  - 抓取 Python 分类热门...")
    python_repos = fetch_trending_repos(language="Python")
    for repo in python_repos:
        key = repo.get("nameWithOwner", "")
        if key and key not in seen:
            seen.add(key)
            all_repos.append(repo)

    print(f"  - 共获取 {len(all_repos)} 个仓库")

    print("🧠 AI 相关过滤...")
    ai_repos = filter_ai_repos(all_repos)
    print(f"  - AI 相关项目：{len(ai_repos)} 个")

    if not ai_repos:
        print("⚠️ 没有找到 AI 相关项目")
        return

    ranked_repos = rank_repos(ai_repos)

    report, date_str = generate_report(ranked_repos)

    with open(REPORT_FILE, "w") as f:
        f.write(report)
    print(f"✅ 报告已保存：{REPORT_FILE}")

    save_to_obsidian(report, date_str)

    print(f"\n{'='*50}")
    print(report)


if __name__ == "__main__":
    main()
