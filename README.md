# Family Memory Center

> 家庭智能体系统的中央知识库

## 功能

- **三层记忆分类**：家庭共享、成员共享、成员私有
- **RAG 语义搜索**：ChromaDB 向量检索 + SQLite 全文搜索
- **多成员支持**：完全独立的成员记忆空间
- **渐进学习**：被动观察 + 主动确认
- **完整备份**：增量/全量备份、时间点恢复

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                        外部调用层                             │
├─────────────────────────────────────────────────────────────┤
│  主Agent │ 领域Agent │ 用户查询接口 │ 备份恢复接口            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       查询引擎层                             │
├─────────────────────────────────────────────────────────────┤
│  Query Understanding → 混合检索 → 重排序 → 访问控制           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       存储引擎层                             │
├─────────────────────────────────────────────────────────────┤
│         SQLite（结构化数据）│ ChromaDB（向量检索）           │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 初始化

```bash
python -m src.memory.cli init
```

### 添加知识

```bash
python -m src.memory.cli add \
  --content "全家人都不吃香菜" \
  --type preference \
  --category diet \
  --visibility family_shared
```

### 搜索

```bash
python -m src.memory.cli search --query "饮食偏好"
```

### 列出知识

```bash
python -m src.memory.cli list --visibility family_shared
```

### 列出成员

```bash
python -m src.memory.cli members
```

### 导出数据

```bash
python -m src.memory.cli export
```

## 项目结构

```
.
├── docs/                    # 设计文档
├── data/                    # 数据目录
│   ├── memory/
│   │   ├── memory.db       # SQLite 数据库
│   │   ├── chroma/         # ChromaDB 向量索引
│   │   └── backup/         # 备份目录
│   ├── schemas/
│   └── profiles/
└── src/
    └── memory/
        ├── __init__.py      # 主模块
        ├── database.py      # 数据库操作
        ├── schema.py        # 表结构
        ├── access_control.py # 访问控制
        ├── cli.py           # CLI 工具
    └── rag/
        ├── __init__.py
        └── vector_store.py   # 向量存储
```

## 设计文档

| 文档 | 说明 |
|------|------|
| [memory-center设计.md](docs/memory-center设计.md) | 整合文档 |
| [memory-center-架构.md](docs/memory-center-架构.md) | 定位与架构 |
| [memory-center-存储.md](docs/memory-center-存储.md) | SQLite + ChromaDB |
| [memory-center-RAG.md](docs/memory-center-RAG.md) | 语义搜索 |
| [memory-center-多成员.md](docs/memory-center-多成员.md) | 多成员支持 |
| [memory-center-备份恢复.md](docs/memory-center-备份恢复.md) | 备份恢复 |

## 使用示例

```python
from src.memory import MemoryCenter

# 初始化
mc = MemoryCenter.initialize()

# 创建实例
mc = MemoryCenter(requester_id="agent_main", requester_type="agent")

# 添加知识
kid = mc.add_knowledge(
    content="每周五晚上是家庭电影夜",
    knowledge_type="habit",
    category="family_time",
    visibility="family_shared",
    confidence=0.8
)

# 搜索
results = mc.search(
    query="家庭活动安排",
    scope=["family_shared", "member_shared"],
    n_results=5
)

# 查询
all_family = mc.query(visibility="family_shared")

# 获取成员
members = mc.get_members()

# 导出备份
data = mc.export()
```
