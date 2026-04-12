#!/usr/bin/env python3
"""
GitHub Trending AI 分析器
生成中文 GitHub AI 周报（Trending + Deep Dive 整合版）
"""

import subprocess
import json
import os
import urllib.request
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ── MiniMax API 配置 ──────────────────────────────────────────────
MINIMAX_API_KEY = "sk-cp-ChtXE5BJLzAv9LVPJXtL0eKh3pqAK5_xlQOyf-mSt7MHCQaD8ykHVFC8UaYlEoZhi6PpSb1SL08lmBhWUaTzGSS_tzed9x20ksd_5kAGr55NPrau5BPX_0s"
MINIMAX_BASE_URL = "https://api.minimaxi.com/v1"
MINIMAX_MODEL = "MiniMax-M2.7-highspeed"

# ── 输出路径 ──────────────────────────────────────────────────────
OUTPUT_DIR = "/Users/lisanchuan1/.openclaw/workspace/data/github_trending"
REPORT_FILE = f"{OUTPUT_DIR}/latest.md"
DATA_FILE = f"{OUTPUT_DIR}/repos.json"

# ── AI 关键词过滤 ─────────────────────────────────────────────────
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

# ── LLM 翻译 ─────────────────────────────────────────────────────
# 线程安全的缓存
_translate_cache = {}
_cache_lock = threading.Lock()

def llm_translate(desc, readme="", cache_key=None):
    """用 MiniMax 把 description（+ 可选 README）翻译成中文，带缓存"""
    # 缓存键：只用 desc，避免重复调用
    if cache_key is None:
        cache_key = desc

    with _cache_lock:
        if cache_key in _translate_cache:
            return _translate_cache[cache_key]

    prompt = f"""你是一个 GitHub 项目描述翻译专家。请将以下 GitHub 项目的描述翻译成中文，要求：
1. 简洁流畅，符合中文表达习惯
2. 不超过 60 字
3. 只返回翻译结果，不解释

项目描述：{desc}"""
    if readme:
        prompt += f"\n\nREADME 摘要：\n{readme[:300]}"

    payload = json.dumps({
        "model": MINIMAX_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.3
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{MINIMAX_BASE_URL}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            translation = result["choices"][0]["message"]["content"].strip()
            with _cache_lock:
                _translate_cache[cache_key] = translation
            return translation
    except Exception as e:
        print(f"    [LLM 翻译失败: {e}]")
        return None


# ── GitHub API ────────────────────────────────────────────────────
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
    """获取 README 开头"""
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


def fetch_repo_metadata(repo):
    """并行获取单个 repo 的额外 metadata（topics + readme），返回 (repo, topics, readme)"""
    name = repo.get("nameWithOwner", "")
    if "/" not in name:
        return (repo, [], None)
    owner, repo_name = name.split("/", 1)
    topics = get_repo_topics(owner, repo_name)
    readme = get_readme_snippet(owner, repo_name)
    return (repo, topics, readme)


# ── 报告生成 ─────────────────────────────────────────────────────
def generate_trending_section(repos, top_n=10):
    """生成热门项目章节（并发翻译）"""
    lines = ["## 🔥 热门 AI 项目\n"]

    sorted_repos = sorted(repos, key=lambda x: x.get("stargazerCount", 0), reverse=True)[:top_n]

    # 并发翻译
    desc_raws = {r.get("nameWithOwner", ""): r.get("description", "") or "" for r in sorted_repos}
    translations = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_name = {executor.submit(llm_translate, desc): name for name, desc in desc_raws.items()}
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                translations[name] = future.result()
            except Exception:
                translations[name] = None

    for i, repo in enumerate(sorted_repos, 1):
        name = repo.get("nameWithOwner", "")
        desc_raw = desc_raws.get(name, "")
        lang = repo.get("primaryLanguage", {}).get("name", "") if repo.get("primaryLanguage") else ""
        stars = repo.get("stargazerCount", 0)
        url = repo.get("url", "")

        desc_zh = translations.get(name) or (desc_raw[:80] + "…" if desc_raw else "暂无描述")

        lines.append(f"### {i}. {name}")
        lines.append(f"- {desc_zh}")
        lines.append(f"- ⭐ {stars:,} | {'语言: ' + lang if lang else '多语言'}")
        lines.append(f"- 🔗 {url}")
        lines.append("")

    return "\n".join(lines)


def generate_deepdive_section(repos, top_n=5):
    """生成深度分析章节（并发获取 metadata 和翻译）"""
    lines = ["## 🧠 深度分析（Top 5）\n"]

    top_repos = repos[:top_n]

    # 并发获取所有 metadata
    metadata_results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_name = {executor.submit(fetch_repo_metadata, repo): repo.get("nameWithOwner", "") for repo in top_repos}
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                metadata_results[name] = future.result()
            except Exception as e:
                metadata_results[name] = (None, [], None)

    # 并发翻译所有描述
    desc_raws = {}
    for repo in top_repos:
        name = repo.get("nameWithOwner", "")
        desc_raws[name] = repo.get("description", "") or ""

    # 两种翻译任务并发跑
    translate_futures = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 基础翻译
        for name, desc in desc_raws.items():
            translate_futures[executor.submit(llm_translate, desc, "", name)] = (name, "desc")
        # README 增强翻译
        for name, result in metadata_results.items():
            _, _, readme = result
            if readme:
                desc = desc_raws.get(name, "")
                key = f"{name}_readme"
                translate_futures[executor.submit(llm_translate, desc, readme, key)] = (name, "readme")

    translations = {}
    for future in as_completed(translate_futures):
        name, kind = translate_futures[future]
        try:
            result = future.result()
            if kind == "desc":
                translations[(name, "desc")] = result
            else:
                translations[(name, "readme")] = result
        except Exception:
            pass

    for i, repo in enumerate(top_repos, 1):
        name = repo.get("nameWithOwner", "")
        desc_raw = desc_raws.get(name, "")
        stars = repo.get("stargazerCount", 0)
        lang = repo.get("primaryLanguage", {}).get("name", "") if repo.get("primaryLanguage") else ""

        _, topics, readme = metadata_results.get(name, (None, [], None))
        topics_str = " · ".join(topics[:5]) if topics else ""

        desc_zh = translations.get((name, "desc")) or (desc_raw[:80] + "…" if desc_raw else "暂无描述")
        summary_zh = translations.get((name, "readme"))

        lines.append(f"### {i}. {name}")
        lines.append(f"- ⭐ {stars:,} | {'语言: ' + lang if lang else '多语言'}")
        lines.append(f"- {desc_zh}")
        if topics_str:
            lines.append(f"- 🏷️ {topics_str}")
        if summary_zh:
            lines.append(f"- 📖 {summary_zh}")
        lines.append("")

    return "\n".join(lines)


def generate_report(repos):
    """生成完整报告"""
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
