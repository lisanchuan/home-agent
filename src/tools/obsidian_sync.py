"""Obsidian sync tool - save webpage/article as Obsidian note"""
import sys
import re
from pathlib import Path
from datetime import datetime
from html import unescape

VAULT_PATH = Path("/Users/lisanchuan1/Library/Mobile Documents/iCloud~md~obsidian/Documents/docs")


def fetch_webpage(url: str) -> dict:
    """Fetch URL and extract content using web_fetch approach"""
    from urllib.request import urlopen
    
    with urlopen(url, timeout=15) as resp:
        html_content = resp.read().decode('utf-8', errors='replace')
    
    # Extract title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else "Untitled"
    title = unescape(title).replace('_哔哩哔哩_bilibili', '').replace('- 哔哩哔哩', '').strip()
    
    # Remove scripts and styles
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL|re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL|re.IGNORECASE)
    
    # Try to extract description
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    description = desc_match.group(1) if desc_match else ""
    
    return {"title": title, "description": description, "url": url}


def html_to_markdown_simple(html: str) -> str:
    """Simple HTML to markdown conversion"""
    # Remove scripts and styles
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)
    
    # Convert HTML elements to markdown
    text = html
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<a[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.IGNORECASE)
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.IGNORECASE)
    text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.IGNORECASE)
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.IGNORECASE)
    text = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', text, flags=re.IGNORECASE)
    
    # Strip remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    text = unescape(text)
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def save_as_obsidian_note(title: str, content: str, url: str = None, tags: list = None) -> str:
    """Save content as Obsidian markdown note"""
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title).strip()
    if not safe_title:
        safe_title = "untitled"
    
    filename = f"{safe_title}.md"
    filepath = VAULT_PATH / filename
    
    # Handle duplicates
    counter = 1
    while filepath.exists():
        filename = f"{safe_title}_{counter}.md"
        filepath = VAULT_PATH / filename
        counter += 1
    
    # Frontmatter
    now = datetime.now().isoformat()
    tag_str = ', '.join(f'"{t}"' for t in (tags or ['webclip']))
    source_line = f"\nsource: {url}" if url else ""
    
    frontmatter = f"""---
created: {now}{source_line}
tags: [{tag_str}]
---

"""
    full_content = frontmatter + content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return str(filepath)


def process_video_as_article(url: str, video_info: dict = None) -> str:
    """Process video URL and save as formatted article"""
    if video_info is None:
        video_info = fetch_webpage(url)
    
    title = video_info.get("title", "Untitled")
    description = video_info.get("description", "")
    
    # Build article content
    content = f"""# {title}

## 视频信息

- **链接**：{url}
- **平台**：哔哩哔哩

## 内容摘要

{description if description else "（暂无描述）"}

## 要点笔记

（待补充）

---
*由 AI 自动整理 · {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    return save_as_obsidian_note(title, content, url, tags=["视频笔记", "bilibili"])


def process_url_as_article(url: str, title: str = None, content: str = None) -> str:
    """Process URL and save as article"""
    if title is None:
        info = fetch_webpage(url)
        title = info.get("title", "Untitled")
        if content is None:
            content = info.get("description", "")
    
    article = f"# {title}\n\n"
    if content:
        article += f"{content}\n\n"
    article += f"---\n*来源：{url}*\n"
    
    return save_as_obsidian_note(title, article, url, tags=["webclip"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python obsidian_sync.py video <url>")
        print("  python obsidian_sync.py article <url> [title]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    url = sys.argv[2]
    
    try:
        if cmd == "video":
            path = process_video_as_article(url)
        else:
            title = sys.argv[3] if len(sys.argv) > 3 else None
            path = process_url_as_article(url, title)
        print(f"Saved: {path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
