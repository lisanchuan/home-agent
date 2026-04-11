# Family Memory Center — RAG 语义搜索设计

> 版本：1.0 | 日期：2026-04-09

---

## 一、设计目标

### 1.1 需求

- **语义搜索**：理解语义，不精确匹配也能找到
- **低延迟**：本地模型，响应要快
- **精准过滤**：按成员、类型、时间过滤

### 1.2 选型

| 组件 | 选择 | 原因 |
|------|------|------|
| Embedding 模型 | **text-embedding-3-small** | OpenAI API，本地调用，低延迟 |
| 向量数据库 | **ChromaDB** | 轻量、本地、支持元数据过滤 |
| 部署方式 | **本地** | 数据不出本地，保护隐私 |

---

## 二、语义搜索流程

### 2.1 整体流程

```
用户查询："爸爸最近有什么饮食上的变化？"
     │
     ▼
┌─────────────────────────────────────────┐
│         Query Understanding             │
│  - 意图识别：查询偏好/习惯变化          │
│  - 实体识别：成员=爸爸                  │
│  - 时间限定：最近                        │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│         Retrieval (RAG)                 │
│  - 语义向量检索                         │
│  - 关键词过滤                           │
│  - 时间范围过滤                         │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│         Re-ranking                      │
│  - 相关性重排                           │
│  - 去重                                │
│  - 质量筛选                            │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│         Context Assembly                │
│  - 拼接相关记忆                        │
│  - 添加引用标注                        │
└─────────────────────────────────────────┘
     │
     ▼
     返回结果
```

### 2.2 Query Understanding 详解

```python
class QueryUnderstanding:
    """解析用户查询，提取关键信息"""
    
    def parse(self, query: str) -> QueryIntent:
        # 意图识别
        intent = self.recognize_intent(query)
        # 实体识别
        entities = self.extract_entities(query)
        # 时间解析
        time_range = self.parse_time(query)
        # 成员识别
        member = self.identify_member(query)
        
        return QueryIntent(
            intent=intent,
            entities=entities,
            time_range=time_range,
            member=member,
            original_query=query
        )

# 识别结果示例
query = "爸爸最近有什么饮食上的变化？"
result = query_understanding.parse(query)
# QueryIntent(
#     intent="preference_change",
#     entities=["饮食", "偏好"],
#     time_range="recent",
#     member="father",
#     original_query=query
# )
```

---

## 三、混合检索策略

### 3.1 检索流程

```python
async def hybrid_retrieve(query: QueryIntent, requester: Requester) -> List[Memory]:
    results = []
    
    # Step 1: 语义向量检索
    semantic_results = await semantic_search(
        query_text=query.original_query,
        filters={
            "visibility": get_visible_scopes(requester),
            "owner_member_id": query.member.id if query.member else None
        },
        top_k=20
    )
    results.extend(semantic_results)
    
    # Step 2: 关键词检索（补充）
    if query.entities:
        keyword_results = keyword_search(
            keywords=query.entities,
            filters={"visibility": get_visible_scopes(requester)},
            top_k=10
        )
        results.extend(keyword_results)
    
    # Step 3: 去重和合并
    results = deduplicate_and_merge(results)
    
    # Step 4: 重排序
    results = rerank(results, query)
    
    return results[:10]
```

### 3.2 语义检索

```python
# ChromaDB 语义检索
def semantic_search(
    query_text: str,
    filters: dict,
    top_k: int = 20
) -> List[SearchResult]:
    
    # 获取embedding
    embedding = get_embedding(query_text)
    
    # ChromaDB 查询
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=filters,
        include=["documents", "metadatas", "distances"]
    )
    
    # 转换为统一格式
    return [
        SearchResult(
            knowledge_id=meta["knowledge_id"],
            content=doc,
            score=1 - distance,  # cosine distance -> similarity
            metadata=meta
        )
        for doc, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
    ]
```

### 3.3 关键词检索

```python
# SQLite FTS5 全文搜索
def keyword_search(
    keywords: List[str],
    filters: dict,
    top_k: int = 10
) -> List[SearchResult]:
    
    # 构建FTS查询
    fts_query = " OR ".join(f'"{kw}"' for kw in keywords)
    
    # SQLite FTS 查询
    sql = """
        SELECT k.*, k.content as snippet
        FROM knowledge_nodes k
        JOIN knowledge_fts fts ON k.id = fts.knowledge_id
        WHERE fts MATCH ?
        AND k.visibility = ?
        ORDER BY rank
        LIMIT ?
    """
    
    # 执行查询
    results = db.execute(sql, [fts_query, filters["visibility"], top_k])
    
    return [
        SearchResult(
            knowledge_id=row["id"],
            content=row["content"],
            score=0.8,  # 关键词匹配，给固定分数
            metadata={"type": row["type"], "category": row["category"]}
        )
        for row in results
    ]
```

---

## 四、重排序策略

### 4.1 重排序算法

```python
def rerank(results: List[SearchResult], query: QueryIntent) -> List[SearchResult]:
    """对检索结果进行重排序"""
    
    scored_results = []
    
    for result in results:
        score = 0.0
        factors = []
        
        # 1. 语义相关性（来自向量检索）
        semantic_score = result.score * 0.4
        score += semantic_score
        factors.append(("语义相关", semantic_score))
        
        # 2. 时间新鲜度
        time_score = calculate_time_freshness(result, query) * 0.2
        score += time_score
        factors.append(("时间新鲜度", time_score))
        
        # 3. 类型匹配
        type_score = calculate_type_match(result, query) * 0.15
        score += type_score
        factors.append(("类型匹配", type_score))
        
        # 4. 置信度
        confidence_score = result.metadata.get("confidence", 0.5) * 0.15
        score += confidence_score
        factors.append(("置信度", confidence_score))
        
        # 5. 触发次数（越常用越可靠）
        trigger_score = min(result.metadata.get("trigger_count", 0) / 10, 1.0) * 0.1
        score += trigger_score
        factors.append(("触发次数", trigger_score))
        
        scored_results.append((score, result, factors))
    
    # 按总分排序
    scored_results.sort(key=lambda x: x[0], reverse=True)
    
    return [r for _, r, _ in scored_results]
```

### 4.2 时间新鲜度计算

```python
def calculate_time_freshness(result: SearchResult, query: QueryIntent) -> float:
    """计算时间新鲜度分数"""
    
    last_triggered = result.metadata.get("last_triggered_at")
    if not last_triggered:
        return 0.5  # 默认分数
    
    days_since = (now() - parse_date(last_triggered)).days
    
    if query.time_range == "recent":
        # "最近"：30天内满分，30-90天递减
        if days_since <= 30:
            return 1.0
        elif days_since <= 90:
            return 1.0 - (days_since - 30) / 60
        else:
            return 0.3
    
    elif query.time_range == "all":
        # "全部"：均匀分布
        return 0.8 if days_since < 365 else 0.6
    
    else:
        return 0.5
```

---

## 五、上下文组装

### 5.1 组装 Prompt

```python
def assemble_context(results: List[SearchResult], query: QueryIntent) -> str:
    """将检索结果组装成上下文"""
    
    context_parts = ["【相关记忆】\n"]
    
    for i, result in enumerate(results, 1):
        member = result.metadata.get("owner_member_id", "unknown")
        knowledge_type = result.metadata.get("type", "unknown")
        confidence = result.metadata.get("confidence", 0)
        
        context_parts.append(
            f"{i}. [{member}] {result.content}\n"
            f"   类型：{knowledge_type} | 置信度：{confidence:.0%}\n"
        )
    
    context = "\n".join(context_parts)
    
    # 添加回答提示
    prompt = f"""基于以下记忆回答用户问题。如果记忆不足以回答，直接说明不知道，不要编造。

用户问题：{query.original_query}

{context}

回答："""
    
    return prompt
```

### 5.2 使用示例

```python
# 查询流程
query = query_understanding.parse("爸爸最近有什么饮食上的变化？")
results = await hybrid_retrieve(query, requester)
context = assemble_context(results, query)

# 发送给 LLM
response = await llm.generate(context)
```

---

## 六、性能优化

### 6.1 缓存策略

| 缓存级别 | 内容 | TTL |
|---------|------|-----|
| **Query Cache** | 相同查询的检索结果 | 5分钟 |
| **Embedding Cache** | 相同文本的 embedding | 24小时 |
| **Member Cache** | 成员基础信息 | 1小时 |

### 6.2 批量索引

新知识写入时，不立即更新向量索引，而是批量处理：

```python
class BatchIndexer:
    """批量索引，避免频繁写入"""
    
    def __init__(self, batch_size: int = 100, flush_interval: int = 300):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.pending = []
        self.last_flush = time.time()
    
    def add(self, knowledge: KnowledgeNode):
        self.pending.append(knowledge)
        
        if len(self.pending) >= self.batch_size:
            self.flush()
        elif time.time() - self.last_flush > self.flush_interval:
            self.flush()
    
    def flush(self):
        # 批量更新 ChromaDB
        embeddings = get_embeddings([k.content for k in self.pending])
        
        collection.add(
            embeddings=embeddings,
            documents=[k.content for k in self.pending],
            metadatas=[k.to_metadata() for k in self.pending],
            ids=[f"vec_{k.id}" for k in self.pending]
        )
        
        self.pending.clear()
        self.last_flush = time.time()
```

### 6.3 异步处理

```python
# 非阻塞写入
async def write_knowledge(knowledge: KnowledgeNode):
    # 立即写入 SQLite
    await db.write(knowledge)
    
    # 异步更新向量索引（不阻塞主流程）
    asyncio.create_task(indexer.add(knowledge))
```

---

## 七、本地部署配置

### 7.1 ChromaDB 配置

```python
import chromadb
from chromadb.config import Settings

# 本地持久化
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./data/memory/chroma",
    anonymized_telemetry=False
))

# 创建 Collection
collection = chroma_client.get_or_create_collection(
    name="family_memory",
    metadata={"description": "家庭记忆语义索引"}
)
```

### 7.2 Embedding 模型选择

```python
# 推荐：OpenAI text-embedding-3-small
# - 维度：1536（可压缩到384）
# - 价格：$0.02/1M tokens
# - 延迟：本地 API ~100ms

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 384  # 压缩到384维，提速
```
