# 乐谱图片 HTML 特征分析

**分析日期**：2026-04-12
**数据来源**：wechat_songs.json（白熊音乐公众号，ukulele/guitar 曲谱文章）
**注意**：数据中 `content` 字段是已处理过的简化 HTML，不是微信公众号原始 HTML（无 wxw-img/rich_pages/data-* 等特征）

---

## 一、HTML 特征分析

### 1.1 content 字段结构

所有图片都使用统一包装格式：
```html
<p><img alt="图片" class="img-responsive img-fluid" loading="lazy" src="..."/></p>
```

特征：
- `class="img-responsive img-fluid"` — Bootstrap 响应式图片类
- `loading="lazy"` — 懒加载
- `alt` 值为 "图片"（通用占位符）或具体文件名（如 "周杰伦111.jpg"）
- 所有图片外层必包 `<p>` 标签

### 1.2 微信公众号原始 HTML（推测）

原始微信公众号后台导出的 HTML 通常带有：
- `class="wxw-img"` / `class="rich_pages"`
- `class="js_imgscale"`
- `data-type="image"`
- 内联 style 如 `width: xxxpx;`
- section 嵌套结构

但本数据集已经过预处理剥离这些特征。

---

## 二、图片分类与特征

### 2.1 乐谱图特征

| 特征 | 值 |
|------|-----|
| 位置 | 文章**中后段**，「弹唱谱」标注之后 |
| alt | "图片"（无具体描述） |
| 所在段落文本 | 前后有 "尤克里里弹唱 谱"、"吉他弹唱 谱"、"教学用谱" 等关键词 |
| 数量 | 通常连续出现多张（2-10张） |
| linked | 不带 `<a>` 链接 |
| title | 空 |

**典型上下文**：
```
1 尤克里里弹唱 谱(女&男)
<img alt="图片" ... src="..._005.jpg"/>   ← 乐谱图
2 吉他弹唱 谱(女&男)
<img alt="图片" ... src="..._006.jpg"/>   ← 乐谱图
```

### 2.2 非乐谱图特征

#### 类型A：专辑封面/歌手照片
| 特征 | 值 |
|------|-----|
| alt | 具体文件名如 "周杰伦太阳之子专辑封面.JPG"、"周杰伦111.jpg" |
| 位置 | 文章开头（歌曲介绍段落内） |
| 前后文本 | 歌名、歌手名、专辑描述 |
| 数量 | 1-2张 |

#### 类型B：广告/推荐卡片（嵌入链接）
| 特征 | 值 |
|------|-----|
| 结构 | `<a>...<img.../></a>`（图片在链接内）|
| alt | "图片" 或 "IMG_1586.JPG" |
| 前后文本 | "曲谱大合集｜戳图直达"、"更多Taylor Swift歌单" |
| 位置 | 文章**后半段**穿插，或末尾推荐区 |

#### 类型C：微信公众号 Logo/结尾装饰
| 特征 | 值 |
|------|-----|
| alt | "图片" |
| 位置 | 文章**末尾**（"LIVE BETTER WITH UKULELE" 附近） |
| linked | 不带链接 |
| 前后文本 | 固定标语文字 |

#### 类型D：视频封面/占位图
| 特征 | 值 |
|------|-----|
| alt | "undefined" 或 "image.png" |
| title | "undefined" 或 "image.png" |
| 位置 | 不固定，通常在商品推荐区前后 |
| 数量 | 1-2张 |

---

## 三、图片过滤规则设计

### 3.1 核心过滤策略（伪代码）

```python
def is_sheet_music(img_tag, prev_text, next_text, p_index, total_p):
    # ── 规则1：广告链接图（图片在<a>标签内）→ 排除 ──
    if is_inside_anchor(img_tag):
        return False, "广告/推荐链接图"

    # ── 规则2：alt/title 为 undefined 或 .png → 排除 ──
    if alt in ("undefined", "image.png") or title == "undefined":
        return False, "视频封面/占位图"

    # ── 规则3：alt 有具体文件名（包含 .jpg/.JPG）→ 排除（专辑封面/歌手图）──
    if ".jpg" in alt or ".JPG" in alt:
        return False, "专辑封面/歌手照片"

    # ── 规则4：文章首尾区域（前10% / 后15%）→ 排除装饰图 ──
    position_ratio = p_index / total_p
    if position_ratio < 0.10 or position_ratio > 0.85:
        return False, "首尾装饰区"

    # ── 规则5：前后文本含乐谱关键词 → 保留 ──
    sheet_keywords = ["弹唱谱", "吉他弹唱谱", "尤克里里弹唱谱",
                      "教学用谱", "曲谱", "谱(女", "谱(男",
                      "吉他弹唱 谱", "尤克里里弹唱 谱"]
    context = (prev_text + next_text).lower()
    if any(kw in context for kw in sheet_keywords):
        return True, "乐谱图"

    # ── 规则6：alt="图片" + 不在首尾 + 前后无广告关键词 → 保守保留 ──
    ad_keywords = ["戳图直达", "微信小店", "往期热门", "点击图片直达",
                    "购琴", "同款琴", "bilibili", "曲谱大合集"]
    if not any(kw in context for kw in ad_keywords):
        return True, "疑似乐谱图（需人工确认）"

    return False, "其他图"
```

### 3.2 CSS 选择器（基于原始 HTML）

```css
/* 保留：独立段落中的乐谱类图片 */
p:not(:has(a)) > img[alt="图片"][class~="img-responsive"] {
    /* 需要配合位置 + 上下文文本过滤 */
}

/* 排除：链接内的图片（广告推荐）*/
a > img { display: none; }

/* 排除：特定的占位图 */
img[alt="undefined"], img[title="undefined"] { display: none; }

/* 排除：.jpg/.JPG 命名的具体文件图 */
img[alt*=".jpg"], img[alt*=".JPG"] { display: none; }
```

### 3.3 正则匹配

```python
# 匹配所有独立（非链接内）图片
IMG_PATTERN = re.compile(
    r'<p(?:\s[^>]*)?>(?!<a )<img'
    r'[^>]+alt="([^"]*)"[^>]*src="([^"]+\.jpg)"[^>]*/></p>',
    re.DOTALL
)

# 匹配广告/推荐链接图（排除）
AD_IMG_PATTERN = re.compile(
    r'<a [^>]+><img[^>]+alt="([^"]*)"[^>]*/></a>',
    re.DOTALL
)

# 匹配带具体文件名的非乐谱图（排除）
NAMED_IMG_PATTERN = re.compile(
    r'<img[^>]+alt="([^"]*\.jpe?g[^"]*)"',
    re.IGNORECASE
)
```

---

## 四、验证测试（3张图）

基于 Record 3 数据：

| # | src | alt | 前后文 | 判定 | 实际 |
|---|-----|-----|--------|------|------|
| 1 | `..._005.jpg` | "图片" | 前："弹奏难度 (中等) 1 尤克里里弹唱 谱(女&男)" 后："2 吉他弹唱 谱(女&男)" | ✅ 乐谱图 | 乐谱图 ✓ |
| 2 | `..._011.jpg` | "IMG_1586.JPG" | 前："周杰伦新专辑《太阳之子》曲谱大合集｜戳图直达" (在`<a>`内) | ❌ 排除 | 广告卡片 ✓ |
| 3 | `..._004.jpg` | "周杰伦111.jpg" | 前："以第一人称声音演出这幅...六张插画组成的故事" | ❌ 排除 | 歌手照片 ✓ |

---

## 五、总结

**主要发现**：

1. **content 已预处理** — 不是微信公众号原始 HTML，无法通过 `wxw-img`/`rich_pages` 等特征区分
2. **乐谱图核心特征**：`alt="图片"` + 不在 `<a>` 内 + 出现在「X弹唱谱」标注附近
3. **排除规则优先级**：
   - P0：`<a>` 内图片 → 广告（**必须排除**）
   - P1：`alt` 包含 `.jpg`/.JPG → 歌手/专辑图（**必须排除**）
   - P2：`alt/title="undefined"` → 占位图（**必须排除**）
   - P3：首尾区域 → 装饰图（**倾向排除**）
4. **保留策略**：通过上下文文本中的 "弹唱谱"、"曲谱" 等关键词定位乐谱区

**推荐实现**：正则预过滤 + 上下文关键词双重验证，准确率预计 > 90%。
