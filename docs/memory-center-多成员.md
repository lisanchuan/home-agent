# Family Memory Center — 多成员记忆设计

> 版本：1.0 | 日期：2026-04-09

---

## 一、设计目标

### 1.1 需求

每个家庭成员有**完全独立的记忆空间**，包括：
- 私有记忆（只有自己能看到）
- 共享记忆（家庭成员之间共享）
- 家庭共享（全体成员共有）

### 1.2 设计原则

```
┌─────────────────────────────────────────────────────────────┐
│  1. 成员隔离：每个成员的私有记忆完全隔离                      │
│  2. 最小权限：只授予完成任务所需的最小权限                  │
│  3. 可配置：成员可调整自己的记忆共享范围                    │
│  4. 代理机制：成员可指定代理人访问自己的私有记忆            │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、成员模型

### 2.1 成员类型

| 类型 | 说明 | 权限 |
|------|------|------|
| **户主（head）** | 家庭主要决策者 | 读写所有家庭共享 + 成员共享 + 子女私有（可选）|
| **成员（member）** | 普通成年成员 | 读写自己的共享/私有 + 家庭共享 |
| **子女（child）** | 未成年成员 | 读写自己的共享/私有 + 家庭共享 |
| **管家Agent** | 主Agent代理 | 读写所有记忆（代理权限） |

### 2.2 成员数据结构

```json
{
  "id": "member_father",
  "name": "爸爸",
  "relationship": "父亲",
  "role": "head",
  "is_minor": false,
  "preferences": {
    "disclosure_level": "normal",  // 披露级别：full/normal/minimal
    "allow_agent_proxy": true,
    "allow_spouse_view": true
  },
  "agent_ids": ["father_agent"],
  "created_at": "2026-01-01T00:00:00+08:00"
}
```

### 2.3 披露级别

| 级别 | 说明 | 对主Agent可见 |
|------|------|--------------|
| **full** | 所有记忆完整访问 | 是 |
| **normal** | 私密记忆不可见 | 仅共享记忆 |
| **minimal** | 仅必要信息 | 仅生存必需信息 |

---

## 三、记忆分类（按成员）

### 3.1 四类记忆

```
┌─────────────────────────────────────────────────────────────┐
│                     家庭共享记忆                             │
│         所有成员 + 所有 Agent 可读写                         │
│              例：家庭规则、共同日程                           │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐    ┌──────────────────────┐
│     爸爸的共享记忆     │    │     妈妈的共享记忆     │
│  爸爸 + 主Agent可读写  │    │  妈妈 + 主Agent可读写  │
│    例：工作信息        │    │    例：工作信息        │
└──────────────────────┘    └──────────────────────┘

┌──────────────────────┐    ┌──────────────────────┐
│     爸爸的私有记忆     │    │     妈妈的私有记忆     │
│    仅爸爸可读写        │    │    仅妈妈可读写        │
│  例：私人想法          │    │  例：私人财务          │
└──────────────────────┘    └──────────────────────┘
```

### 3.2 访问权限矩阵

| 记忆类型 | 户主 | 其他成年成员 | 子女 | 主Agent |
|---------|------|-------------|------|--------|
| 家庭共享 | RW | RW | R | RW |
| 成员共享（自己） | RW | - | - | RW |
| 成员共享（配偶） | R* | RW | - | RW |
| 成员共享（其他） | - | - | - | RW |
| 成员私有（自己） | RW | - | R* | RW（代理） |
| 成员私有（配偶） | R* | R* | - | RW（代理） |
| 成员私有（其他） | - | - | - | RW（代理） |

> R* = 需要对方同意的阅读权限

---

## 四、代理机制

### 4.1 代理场景

| 场景 | 代理人 | 权限范围 |
|------|-------|---------|
| 父母查看子女私有记忆 | 主Agent | 仅健康/安全相关 |
| 配偶临时访问 | 主Agent | 仅紧急情况 |
| 完全托孤 | 主Agent | 全部记忆 |

### 4.2 代理级别

```python
class ProxyLevel(Enum):
    # 完全托孤：主Agent可访问全部记忆
    FULL_TRUST = "full_trust"
    
    # 健康/安全：仅健康、安全相关记忆
    HEALTH_SAFETY = "health_safety"
    
    # 紧急情况：仅紧急情况下可访问
    EMERGENCY_ONLY = "emergency_only"
    
    # 无代理：不授权任何第三方
    NONE = "none"
```

### 4.3 代理配置

```json
{
  "member_id": "member_child",
  "proxy_config": {
    "level": "health_safety",
    "proxy_to": "main_agent",
    "allowed_categories": ["health", "safety", "emergency_contact"],
    "restricted_categories": ["personal", "diary", "social"],
    "expires_at": null,
    "approved_at": "2026-04-09T00:00:00+08:00"
  }
}
```

---

## 五、隐私保护

### 5.1 隐私层级

```python
class PrivacyLevel(Enum):
    # 家庭共享
    FAMILY = "family"
    
    # 成员共享（需要明确指定可见成员）
    MEMBER_SHARED = "member_shared"
    
    # 成员私有
    MEMBER_PRIVATE = "member_private"
    
    # 极度私密（连主Agent都无法访问，除非完全托孤）
    STRICTLY_PRIVATE = "strictly_private"
```

### 5.2 敏感信息标记

```json
{
  "id": "kn_20260409_001",
  "content": "儿子最近考试考砸了",
  "privacy_level": "strictly_private",
  "sensitivity_tags": ["education", "emotional"],
  "auto_protect": true
}
```

### 5.3 自动保护规则

| 信息类型 | 默认隐私级别 | 可调整 |
|---------|------------|--------|
| 健康/医疗 | **strictly_private** | 否 |
| 财务/收入 | **member_private** | 是 |
| 情感/关系 | **member_private** | 是 |
| 教育/成绩 | **strictly_private**（子女）/ member_private（成人）| 是 |
| 日程/位置 | **member_shared** | 是 |
| 偏好/习惯 | **member_shared** | 是 |

---

## 六、成员隔离实现

### 6.1 存储隔离

```
data/
├── memory/
│   ├── family_shared/       # 家庭共享记忆
│   │   └── memory.db
│   ├── members/             # 成员记忆目录
│   │   ├── father/
│   │   │   ├── shared.db    # 父亲的共享记忆
│   │   │   └── private.db   # 父亲的私有记忆
│   │   ├── mother/
│   │   │   ├── shared.db
│   │   │   └── private.db
│   │   └── child/
│   │       ├── shared.db
│   │       └── private.db
│   └── agent/               # Agent 代理记忆
│       └── proxy.db
└── chroma/
    ├── family_shared/       # 家庭共享向量索引
    └── members/             # 成员向量索引（隔离）
        ├── father/
        ├── mother/
        └── child/
```

### 6.2 访问控制实现

```python
class AccessController:
    """访问控制器"""
    
    def can_read(self, requester: Member, knowledge: KnowledgeNode) -> bool:
        visibility = knowledge.visibility
        
        if visibility == "family_shared":
            return True  # 所有人都可读
        
        if visibility == "member_shared":
            # 检查是否是拥有者或主Agent
            if knowledge.owner_member_id == requester.id:
                return True
            if requester.is_agent:
                return True
            # 检查是否是配偶（需要同意）
            if requester.is_spouse_of(knowledge.owner_member_id):
                return requester.spouse_consent
            return False
        
        if visibility == "member_private":
            # 检查是否是拥有者
            if knowledge.owner_member_id == requester.id:
                return True
            # 检查是否是主Agent代理
            if requester.is_agent:
                return self.check_proxy(requester, knowledge)
            return False
        
        return False
    
    def can_write(self, requester: Member, knowledge: KnowledgeNode) -> bool:
        # 只有主Agent和渐进学习机制可以写入
        if not requester.is_agent and requester.id != "learning_mechanism":
            return False
        
        visibility = knowledge.visibility
        
        if visibility == "family_shared":
            return True
        
        if visibility == "member_shared":
            return knowledge.owner_member_id == requester.id or requester.is_agent
        
        if visibility == "member_private":
            # 拥有者或代理主Agent
            return knowledge.owner_member_id == requester.id or requester.is_agent
        
        return False
```

---

## 七、成员管理

### 7.1 成员注册

```json
{
  "action": "register_member",
  "member": {
    "name": "儿子",
    "relationship": "子女",
    "role": "child",
    "is_minor": true,
    "preferences": {
      "disclosure_level": "minimal",
      "allow_agent_proxy": true,
      "allow_parents_view": false
    }
  }
}
```

### 7.2 成员注销（数据处理）

```json
{
  "action": "deregister_member",
  "member_id": "member_child",
  "data_handling": {
    "family_shared": "保留",
    "member_shared": "保留（转移给主Agent）",
    "member_private": "归档或删除（用户选择）"
  },
  "confirmation_required": true
}
```

---

## 八、查询路由

### 8.1 查询流程

```python
def query_with_member_context(
    query: str,
    requester: Member,
    scope: List[str]
) -> QueryResult:
    
    all_results = []
    
    # 根据 scope 确定检索范围
    if "family_shared" in scope:
        results = search("family_shared", query, requester)
        all_results.extend(results)
    
    if "member_shared" in scope:
        # 检索自己和其他允许查看的成员的共享记忆
        results = search("member_shared", query, requester)
        all_results.extend(results)
    
    if "member_private" in scope:
        # 只检索自己的私有记忆
        results = search("member_private", query, requester)
        all_results.extend(results)
    
    # 过滤和排序
    return filter_and_rank(all_results, requester)
```

### 8.2 查询示例

```
场景1：爸爸查询"今天有什么安排"
范围：family_shared + father_shared + mother_shared（如果是配偶）
结果：家庭共享日程 + 爸爸的日程 + 妈妈的共享日程

场景2：妈妈查询"老公最近在忙什么"
范围：family_shared + mother_shared（不包含 father_private）
结果：家庭共享日程 + 妈妈的日程（不包含老公私有日程）

场景3：子女查询"爸妈有什么安排"
范围：family_shared + child_shared
结果：家庭共享日程 + 子女自己的日程
（不包含父母的私人日程）
```
