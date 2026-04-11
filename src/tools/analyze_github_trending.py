#!/usr/bin/env python3
"""
GitHub Trending AI 分析器 - 带完整数据存储
"""

import subprocess
import json
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
    "autogpt", "crewai", "dify", "openwebui",
    " Nous", "Qwen", "DeepSeek", "Groq", "Mistral",
    "browser-use", "browser agent", "sheet music"
]

EXCLUDE_KEYWORDS = [
    "public-api", "free api", "programming book", "system design",
    "algorithm", "tutorial", "cheatsheet", "awesome list",
    "youtube downloader", "video download"
]

# 价值评估
VALUE_TAGS = {
    "可直接提升效率": ["claude code", "cursor", "copilot", "skill", "anthropic skills", "oh-my-codex"],
    "值得关注的新方向": ["browser-use", "agent", "crewai", "dify"],
    "有潜力但需观望": ["langflow", "langchain"],
    "偏基础设施/框架": ["pytorch", "transformers", "huggingface"],
    "中文开发者友好": ["DeepSeek", "Qwen", " Nous", "openwebui", "dify"]
}

def gh_graphql(query, variables=None):
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    if variables:
        for k, v in variables.items():
            cmd.extend(["-f", f"{k}={v}"])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)

def fetch_recent_repos(days=14, min_stars=300):
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
    data = gh_graphql(query, variables={"search": search})
    if not data:
        return []
    return data.get("data", {}).get("search", {}).get("nodes", [])

def filter_ai_repos(repos):
    filtered = []
    for repo in repos:
        name = repo.get("nameWithOwner", "").lower()
        desc = (repo.get("description", "") or "").lower()
        text = f"{name} {desc}"
        if any(ex in text for ex in EXCLUDE_KEYWORDS):
            continue
        if not any(kw.lower() in text for kw in AI_KEYWORDS):
            continue
        filtered.append(repo)
    return filtered

def rank_repos(repos, fresh_weight=3):
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

def assess_value(repo):
    """评估项目对用户的价值"""
    name = repo.get("nameWithOwner", "").lower()
    desc = (repo.get("description", "") or "").lower()
    text = f"{name} {desc}"
    
    # 检查价值标签
    for category, keywords in VALUE_TAGS.items():
        if any(kw.lower() in text for kw in keywords):
            return category
    return "一般关注"

def generate_report(repos):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 分组
    by_value = {"可直接提升效率": [], "值得关注的新方向": [], "有潜力但需观望": [], "偏基础设施/框架": [], "中文开发者友好": [], "一般关注": []}
    
    for repo in repos:
        category = assess_value(repo)
        by_value.setdefault(category, []).append(repo)
    
    lines = [
        f"# GitHub AI 项目周报",
        f"生成时间：{now}",
        "",
        "---",
        ""
    ]
    
    # 价值分析
    lines.append("## 💡 价值分析\n")
    for category in ["可直接提升效率", "值得关注的新方向", "有潜力但需观望", "偏基础设施/框架", "中文开发者友好"]:
        items = by_value.get(category, [])
        if items:
            lines.append(f"### {category}（{len(items)} 个）")
            for repo in items[:5]:
                name = repo.get("nameWithOwner", "")
                desc = repo.get("description", "") or "无描述"
                stars = repo.get("stargazerCount", 0)
                url = repo.get("url", "")
                lines.append(f"- **{name}** ⭐{stars:,}  — {desc}")
                lines.append(f"  {url}")
            lines.append("")
    
    # 完整列表
    lines.append("---")
    lines.append("")
    lines.append("## 📋 完整列表（按热度排序）\n")
    for i, repo in enumerate(repos[:20], 1):
        name = repo.get("nameWithOwner", "")
        desc = repo.get("description", "") or "无描述"
        lang = repo.get("primaryLanguage", {}).get("name", "") if repo.get("primaryLanguage") else ""
        stars = repo.get("stargazerCount", 0)
        url = repo.get("url", "")
        lines.append(f"{i}. **[{name}]({url})** ⭐{stars:,} | {lang}")
        lines.append(f"   {desc}")
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
    
    all_repos = []
    seen = set()
    
    print("  - 抓取近期高星项目...")
    recent = fetch_recent_repos(days=14, min_stars=300)
    for repo in recent:
        key = repo.get("nameWithOwner", "")
        if key and key not in seen:
            seen.add(key)
            all_repos.append(repo)
    
    print("  - 抓取 Python 分类...")
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
    
    # 保存完整数据
    with open(DATA_FILE, "w") as f:
        json.dump({
            "fetched_at": datetime.now().isoformat(),
            "total": len(all_repos),
            "ai_repos": ai_repos  # 完整数据
        }, f, ensure_ascii=False, indent=2)
    
    # 加权排序
    ranked_repos = rank_repos(ai_repos)
    
    # 生成报告
    report = generate_report(ranked_repos)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    
    print(f"✅ 报告已保存：{REPORT_FILE}")
    print(f"✅ 数据已保存：{DATA_FILE}")
    print(f"\n{'='*50}")
    print(report)
    
    return report

if __name__ == "__main__":
    main()
