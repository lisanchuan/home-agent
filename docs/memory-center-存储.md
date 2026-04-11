# Family Memory Center — 数据存储设计

> 版本：1.0 | 日期：2026-04-09

---

## 一、存储选型

### 1.1 选择依据

| 需求 | 选择 | 原因 |
|------|------|------|
| 数据规模 | **SQLite** | 中等规模（500-5000条），不需要完整数据库服务器 |
| 向量检索 | **ChromaDB（本地）** | 轻量、支持本地部署、低延迟 |
| 备份 | **JSON + 文件** | 跨平台、人类可读 |

### 1.2 存储架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Family Memory Center                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                  │
│  │     SQLite      │    │    ChromaDB     │                  │
│  │  (结构化数据)    │    │   (向量索引)    │                  │
│  │                  │    │                  │                  │
│  │  - 知识节点      │    │  - 语义检索     │                  │
│  │  - 成员信息      │    │  - 相似度匹配   │                  │
│  │  - 元数据        │    │  - 全文索引     │                  │
│  └─────────────────┘    └─────────────────┘                  │
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                  │
│  │    JSON 文件     │    │   备份目录       │                  │
│  │   (家族档案)     │    │   (定期快照)     │                  │
│  └─────────────────┘    └─────────────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、SQLite 表结构

### 2.1 核心表

```sql
-- 知识节点表
CREATE TABLE knowledge_nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('fact', 'preference', 'habit', 'taboo')),
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    value TEXT,
    confidence REAL DEFAULT 0.5,
    visibility TEXT NOT NULL CHECK(visibility IN ('family_shared', 'member_shared', 'member_private')),
    owner_member_id TEXT,
    source TEXT DEFAULT 'learning',
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'pending_confirm', 'deprecated')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_triggered_at TEXT,
    trigger_count INTEGER DEFAULT 0,
    confirmed_at TEXT,
    confirmed_by TEXT,
    FOREIGN KEY (owner_member_id) REFERENCES members(id)
);

-- 知识版本历史表
CREATE TABLE knowledge_history (
    id TEXT PRIMARY KEY,
    knowledge_id TEXT NOT NULL,
    value TEXT NOT NULL,
    confidence REAL,
    changed_at TEXT NOT NULL,
    change_reason TEXT,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge_nodes(id)
);

-- 家庭成员表
CREATE TABLE members (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    relationship TEXT NOT NULL,
    role TEXT DEFAULT 'member' CHECK(role IN ('head', 'member', 'child')),
    is_minor INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 访问日志表
CREATE TABLE access_logs (
    id TEXT PRIMARY KEY,
    requester_id TEXT NOT NULL,
    requester_type TEXT NOT NULL,
    action TEXT NOT NULL,
    knowledge_id TEXT,
    result TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

-- 待确认队列
CREATE TABLE pending_confirmations (
    id TEXT PRIMARY KEY,
    knowledge_id TEXT,
    knowledge_type TEXT NOT NULL,
    knowledge_content TEXT NOT NULL,
    suggested_value TEXT,
    trigger_context TEXT,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

-- 衰减记录表
CREATE TABLE decay_records (
    id TEXT PRIMARY KEY,
    knowledge_id TEXT NOT NULL,
    old_confidence REAL NOT NULL,
    new_confidence REAL NOT NULL,
    decay_reason TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge_nodes(id)
);
```

### 2.2 索引

```sql
CREATE INDEX idx_knowledge_type ON knowledge_nodes(type);
CREATE INDEX idx_knowledge_category ON knowledge_nodes(category);
CREATE INDEX idx_knowledge_visibility ON knowledge_nodes(visibility);
CREATE INDEX idx_knowledge_owner ON knowledge_nodes(owner_member_id);
CREATE INDEX idx_knowledge_status ON knowledge_nodes(status);
CREATE INDEX idx_knowledge_confidence ON knowledge_nodes(confidence);
CREATE INDEX idx_access_logs_requester ON access_logs(requester_id);
CREATE INDEX idx_access_logs_timestamp ON access_logs(timestamp);
```

---

## 三、知识节点结构

### 3.1 节点JSON示例

```json
{
  "id": "kn_20260409_001",
  "type": "preference",
  "category": "diet",
  "content": "爸爸喜欢吃川菜",
  "value": " Sichuan cuisine",
  "confidence": 0.85,
  "visibility": "member_shared",
  "owner_member_id": "member_father",
  "source": "learning",
  "status": "active",
  "created_at": "2026-04-09T10:00:00+08:00",
  "updated_at": "2026-04-09T10:00:00+08:00",
  "last_triggered_at": "2026-04-09T10:00:00+08:00",
  "trigger_count": 3,
  "confirmed_at": "2026-04-09T12:00:00+08:00",
  "confirmed_by": "father",
  "history": [
    {
      "id": "kh_001",
      "value": "爸爸喜欢吃粤菜",
      "confidence": 0.7,
      "changed_at": "2026-03-01T10:00:00+08:00",
      "change_reason": "用户更新"
    }
  ]
}
```

---

## 四、ChromaDB 向量索引

### 4.1 Collection 设计

```python
# Collection: family_memory
# 用于语义检索家庭记忆

collection_config = {
    "name": "family_memory",
    "metadata": {
        "description": "家庭记忆语义索引"
    },
    "dimension": 1536,  # OpenAI embedding dimension
    "metric": "cosine"
}
```

### 4.2 Document 结构

```json
{
  "id": "vec_kn_20260409_001",
  "embedding": [0.123, -0.456, ...],  # 1536维向量
  "document": "爸爸喜欢吃川菜，偏好重口味",
  "metadata": {
    "knowledge_id": "kn_20260409_001",
    "type": "preference",
    "category": "diet",
    "visibility": "member_shared",
    "owner_member_id": "member_father",
    "confidence": 0.85
  }
}
```

### 4.3 检索示例

```python
# 查询："有什么饮食偏好"
results = collection.query(
    query_texts=["有什么饮食偏好"],
    n_results=5,
    where={
        "visibility": {"$in": ["family_shared", "member_shared"]},
        "owner_member_id": {"$eq": "member_father"}
    },
    include=["documents", "metadatas", "distances"]
)
```

---

## 五、文件存储结构

```
data/
├── memory/
│   ├── memory.db              # SQLite 数据库
│   ├── chroma/                # ChromaDB 向量数据库
│   │   ├── chroma.sqlite
│   │   └── index/
│   └── backup/                # 备份目录
│       ├── 2026-04-09_full.json
│       └── 2026-04-09_knowledge.json
├── profiles/                  # 家庭档案
│   └── {member_id}/
│       ├── profile.json
│       └── private.md
└── schema/
    └── family-profile.schema.json
```

---

## 六、写入流程

```
写入请求
    │
    ▼
┌──────────────────────────────────┐
│ 1. 基础验证                       │
│    - 权限检查                     │
│    - 格式检查                     │
└──────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────┐
│ 2. 冲突检测                       │
│    - 与现有知识是否冲突？          │
│    - 触发观察模式？               │
└──────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────┐
│ 3. 确认判断                       │
│    - 是否需要主动确认？            │
│    - 加入 pending_confirmations？  │
└──────────────────────────────────┘
    │
    ├── Yes ──→ 写入 pending ──→ 等待确认
    │
    └── No ──→ 正式写入
                   │
                   ├── SQLite（结构化数据）
                   ├── ChromaDB（向量索引）
                   └── 返回 knowledge_id
```

---

## 七、查询流程

```
查询请求
    │
    ▼
┌──────────────────────────────────┐
│ 1. 权限解析                       │
│    - 识别请求者身份                │
│    - 确定可访问范围                │
└──────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────┐
│ 2. 意图分类                       │
│    - 语义检索？关键词检索？         │
│    - 时间范围过滤？               │
└──────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────┐
│ 3. 混合检索                       │
│    - ChromaDB 语义检索             │
│    - SQLite 精确过滤              │
│    - 结果合并                      │
└──────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────┐
│ 4. 访问控制过滤                   │
│    - 移除无权访问的知识            │
│    - 敏感信息脱敏                  │
└──────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────┐
│ 5. 返回结果                       │
│    - 按相关性排序                  │
│    - 附带置信度                    │
└──────────────────────────────────┘
```
