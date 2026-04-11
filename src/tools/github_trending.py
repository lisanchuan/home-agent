#!/usr/bin/env python3
"""
GitHub Trending AI 分析器
使用 GitHub GraphQL API 获取最新 AI/ML 项目
"""

import subprocess
import json
from datetime import datetime, timedelta

OUTPUT_DIR = "/Users/lisanchuan1/.openclaw/workspace/data/github_trending"
REPORT_FILE = f"{OUTPUT_DIR}/latest.md"
DATA_FILE = f"{OUTPUT_DIR}/repos.json"

# AI 相关关键词（用于过滤）
AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "ml",
    "deep learning", "neural", "llm", "gpt", "transformer",
    "nlp", "cv", "computer vision", "reinforcement learning",
    "generative", "diffusion", "stable diffusion", "langchain",
    "agent", "rag", "vector db", "embedding", "hugging face",
    "openai", "claude", "gemini", "ollama", "vllm", "llama",
    "skill", "claude code", "cursor", "copilot", "codex",
    "autogpt", "crewai", "dify", "anything llm", "openwebui",
    " Nous", "Qwen", "DeepSeek", "Groq", "Mistral"
]

# 排除项（误匹配）
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

def fetch_recent_repos(days=7, min_stars=500):
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
    
    variables = {
        "search": f"created:>{date_from} stars:>{min_stars}"
    }
    
    data = gh_graphql(query, variables)
    if not data:
        return []
    
    return data.get("data", {}).get("search", {}).get("nodes", [])

def fetch_trending_repos(language=None, since="weekly"):
    """获取 Trending 仓库（按 stars 排序）"""
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
    """过滤 AI/ML 相关项目，排除误匹配"""
    ai_repos = []
    for repo in repos:
        name = repo.get("nameWithOwner", "").lower()
        desc = (repo.get("description", "") or "").lower()
        text = f"{name} {desc}"
        
        # 排除误匹配
        if any(ex in text for ex in EXCLUDE_KEYWORDS):
            continue
        
        # 必须匹配 AI 关键词
        if not any(kw.lower() in text for kw in AI_KEYWORDS):
            continue
        
        ai_repos.append(repo)
    
    return ai_repos


def rank_repos(repos, fresh_weight=3):
    """
    加权排序：新项目优先
    fresh_weight: 新项目权重倍数
    """
    now = datetime.now()
    
    def score(repo):
        stars = repo.get("stargazerCount", 0)
        pushed_str = repo.get("pushedAt")
        
        # 计算新项目加成
        freshness = 0
        if pushed_str:
            try:
                pushed = datetime.fromisoformat(pushed_str.replace("Z", "+00:00"))
                days_old = (now - pushed).total_seconds() / 86400
                # 7天内新鲜项目有加成，14天以上无加成
                freshness = max(0, (7 - days_old) / 7) * stars * fresh_weight
            except:
                pass
        
        return stars + freshness
    
    return sorted(repos, key=score, reverse=True)

def generate_report(repos, title="GitHub AI 新项目速报"):
    """生成 Markdown 报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        f"# {title}",
        f"生成时间：{now}",
        f"共 {len(repos)} 个 AI 相关项目",
        "",
        "## 🔥 热门 AI 项目",
        ""
    ]
    
    # 按 stars 排序
    sorted_repos = sorted(repos, key=lambda x: x.get("stargazerCount", 0), reverse=True)
    
    for i, repo in enumerate(sorted_repos[:15], 1):
        name = repo.get("nameWithOwner", "")
        desc = repo.get("description", "") or "无描述"
        lang = repo.get("primaryLanguage", {}).get("name", "") if repo.get("primaryLanguage") else ""
        stars = repo.get("stargazerCount", 0)
        url = repo.get("url", "")
        
        lines.append(f"### {i}. {name}")
        lines.append(f"- {desc}")
        lines.append(f"- ⭐ {stars:,} | {'语言: ' + lang if lang else '多语言'}")
        lines.append(f"- {url}")
        lines.append("")
    
    lines.extend([
        "---",
        f"*由 AI 自动生成 · {now}*"
    ])
    
    return "\n".join(lines)

def main():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("📡 获取 GitHub 热门仓库...")
    
    # 获取所有语言的热门项目
    all_repos = []
    seen = set()
    
    # 先获取近期高星项目
    print("  - 抓取近期高星项目...")
    recent = fetch_recent_repos(days=14, min_stars=500)
    for repo in recent:
        key = repo.get("nameWithOwner", "")
        if key and key not in seen:
            seen.add(key)
            all_repos.append(repo)
    
    # 获取 Python 分类热门
    print("  - 抓取 Python 分类...")
    python_repos = fetch_trending_repos(language="Python")
    for repo in python_repos:
        key = repo.get("nameWithOwner", "")
        if key and key not in seen:
            seen.add(key)
            all_repos.append(repo)
    
    print(f"  - 共获取 {len(all_repos)} 个仓库")
    
    # 过滤 AI 相关
    print("🧠 AI 相关过滤...")
    ai_repos = filter_ai_repos(all_repos)
    print(f"  - AI 相关项目：{len(ai_repos)} 个")
    
    # 原始数据
    raw_data = {
        "fetched_at": datetime.now().isoformat(),
        "total": len(all_repos),
        "ai_repos_count": len(ai_repos)
    }
    with open(DATA_FILE, "w") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)
    
    # 加权排序：新项目优先
    ranked_repos = rank_repos(ai_repos)
    
    # 生成报告
    report = generate_report(ranked_repos)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    
    print(f"✅ 报告已保存：{REPORT_FILE}")
    print(f"\n{'='*50}")
    print(report)
    
    return report

if __name__ == "__main__":
    main()
