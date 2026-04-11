#!/usr/bin/env python3
"""
GitHub Trending AI 分析器
生成中文 GitHub AI 周报（Trending + Deep Dive 整合版）
"""

import subprocess
import json
import sys
import os
from datetime import datetime, timedelta

# OpenClaw API 调用（通过环境变量注入的 token）
OPENCLAW_API_TOKEN = os.environ.get("OPENCLAW_API_TOKEN", "")

OUTPUT_DIR = "/Users/lisanchuan1/.openclaw/workspace/data/github_trending"
REPORT_FILE = f"{OUTPUT_DIR}/latest.md"
DATA_FILE = f"{OUTPUT_DIR}/repos.json"

# AI 相关关键词
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

def translate_with_llm(text):
    """用 OpenClaw API 翻译 description（如果有 token）"""
    if not OPENCLAW_API_TOKEN or not text:
        return text
    
    prompt = f"将以下 GitHub 项目描述翻译成中文，保持简洁（不超过50字），只返回翻译结果：\n\n{text}"
    
    import urllib.request
    import urllib.parse
    
    data = json.dumps({
        "model": "minimax-m27-highspeed/MiniMax-M2.7-highspeed",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }).encode()
    
    req = urllib.request.Request(
        "http://localhost:18789/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {OPENCLAW_API_TOKEN}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"].strip()
    except:
        return text

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

def get_readme_summary(owner, repo_name):
    """获取 README 开头作为简介（用于 deep-dive）"""
    result = subprocess.run(
        ["gh", "api", f"/repos/{owner}/{repo_name}/readme"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        return None
    try:
        import base64
        data = json.loads(result.stdout)
        content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
        # 取前 500 字符
        return content[:500].replace("#", "").replace("\n", " ").strip()
    except:
        return None

def translate_description(desc):
    """翻译 description（备用：关键词替换）"""
    if not desc:
        return "暂无描述"
    
    # 常见术语映射
    term_map = {
        "Stable Diffusion": "Stable Diffusion 图像生成",
        "web UI": "Web 界面",
        "GUI": "图形界面",
        "API": "API 接口",
        "agents": "AI 智能体",
        "agent": "AI 智能体",
        "framework": "开发框架",
        "library": "工具库",
        "tool": "工具",
        "platform": "平台",
        "model": "模型",
        "models": "模型",
        "LLM": "大语言模型",
        "language model": "语言模型",
        "machine learning": "机器学习",
        "deep learning": "深度学习",
        "neural": "神经网络",
        "Generative": "生成式",
        "automation": "自动化",
        "workflow": "工作流",
        "RAG": "检索增强生成",
        "vector": "向量",
        "embedding": "嵌入",
        "transformer": "Transformer 架构",
    }
    
    result = desc
    for en, zh in term_map.items():
        result = result.replace(en, zh)
        result = result.replace(en.lower(), zh)
    
    # 简单清理
    result = result.strip()
    if len(result) > 100:
        result = result[:100] + "..."
    
    return result

def generate_trending_section(repos, top_n=10):
    """生成热门项目章节"""
    lines = ["## 🔥 热门 AI 项目\n"]
    
    sorted_repos = sorted(repos, key=lambda x: x.get("stargazerCount", 0), reverse=True)[:top_n]
    
    for i, repo in enumerate(sorted_repos, 1):
        name = repo.get("nameWithOwner", "")
        owner, repo_name = name.split("/") if "/" in name else (name, name)
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
    
    # 选最新最热的项目做深度分析
    top_repos = repos[:top_n]
    
    for i, repo in enumerate(top_repos, 1):
        name = repo.get("nameWithOwner", "")
        owner, repo_name = name.split("/") if "/" in name else (name, name)
        desc_raw = repo.get("description", "") or "无描述"
        desc = translate_description(desc_raw)
        stars = repo.get("stargazerCount", 0)
        lang = repo.get("primaryLanguage", {}).get("name", "") if repo.get("primaryLanguage") else ""
        topics = get_repo_topics(owner, repo_name)
        topics_str = " · ".join(topics[:5]) if topics else ""
        
        lines.append(f"### {i}. {name}")
        lines.append(f"- ⭐ {stars:,} | {'语言: ' + lang if lang else '多语言'}")
        lines.append(f"- {desc}")
        if topics_str:
            lines.append(f"- 🏷️ {topics_str}")
        
        # 简短介绍
        readme = get_readme_summary(owner, repo_name)
        if readme:
            lines.append(f"- 📖 {readme[:150]}...")
        
        lines.append("")
    
    return "\n".join(lines)

def generate_report(repos):
    """生成完整报告（整合版）"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    today_str = datetime.now().strftime("%Y-%m-%d")
    filename_date = today_str
    
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
    
    return "\n".join(lines), filename_date

def save_to_obsidian(content, date_str):
    """复制报告到 Obsidian Raw 目录"""
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
    
    # 加权排序
    ranked_repos = rank_repos(ai_repos)
    
    # 生成报告
    report, date_str = generate_report(ranked_repos)
    
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    print(f"✅ 报告已保存：{REPORT_FILE}")
    
    # 同步到 Obsidian
    save_to_obsidian(report, date_str)
    
    print(f"\n{'='*50}")
    print(report)

if __name__ == "__main__":
    main()
