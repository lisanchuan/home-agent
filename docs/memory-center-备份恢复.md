# Family Memory Center — 备份与恢复设计

> 版本：1.0 | 日期：2026-04-09

---

## 一、设计目标

### 1.1 需求

- **完整备份**：支持全部数据的备份
- **增量备份**：只备份变化的部分
- **恢复功能**：支持指定时间点恢复
- **导出功能**：支持 JSON/CSV 格式导出
- **隐私保护**：备份文件加密存储

### 1.2 备份策略

| 类型 | 频率 | 内容 | 保留时间 |
|------|------|------|---------|
| **每日增量** | 每天 | 当日新增/修改的知识 | 7天 |
| **每周全量** | 每周日 | 全部知识 | 4周 |
| **每月归档** | 每月初 | 上月全量 + 变化知识 | 12个月 |
| **版本快照** | 重要操作前 | 手动触发 | 永久 |

---

## 二、备份类型

### 2.1 全量备份（Full Backup）

```json
{
  "backup_id": "backup_20260409_001",
  "type": "full",
  "created_at": "2026-04-09T00:00:00+08:00",
  "scope": "all",
  "data": {
    "knowledge_nodes": [...],
    "members": [...],
    "knowledge_history": [...],
    "settings": {...}
  },
  "checksum": "sha256:abc123...",
  "encrypted": true,
  "encryption_key_id": "key_001"
}
```

### 2.2 增量备份（Incremental Backup）

```json
{
  "backup_id": "backup_20260409_002",
  "type": "incremental",
  "created_at": "2026-04-09T12:00:00+08:00",
  "based_on": "backup_20260409_001",
  "changes": {
    "added": [...],
    "modified": [...],
    "deleted": ["kn_xxx"]
  },
  "checksum": "sha256:def456..."
}
```

### 2.3 版本快照（Version Snapshot）

```json
{
  "snapshot_id": "snapshot_20260409_003",
  "type": "snapshot",
  "created_at": "2026-04-09T14:30:00+08:00",
  "trigger": "manual",
  "reason": "Before major agent update",
  "data": {
    "knowledge_nodes": [...],
    "metadata": {
      "total_count": 1234,
      "by_type": {...},
      "by_visibility": {...}
    }
  }
}
```

---

## 三、备份存储

### 3.1 存储目录结构

```
data/
├── memory/
│   └── backup/
│       ├── full/
│       │   ├── 2026-04-07_full.json.gz
│       │   ├── 2026-04-08_full.json.gz
│       │   └── 2026-04-09_full.json.gz
│       ├── incremental/
│       │   ├── 2026-04-09_000_incremental.json.gz
│       │   ├── 2026-04-09_001_incremental.json.gz
│       │   └── ...
│       ├── snapshot/
│       │   ├── snapshot_20260401_001.json.gz
│       │   ├── snapshot_20260409_003.json.gz
│       │   └── ...
│       └── metadata/
│           ├── backup_manifest.json
│           └── restore_points.json
```

### 3.2 备份清单（Manifest）

```json
{
  "manifest_version": "1.0",
  "last_updated": "2026-04-09T00:00:00+08:00",
  "backups": [
    {
      "id": "backup_20260409_001",
      "type": "full",
      "created_at": "2026-04-09T00:00:00+08:00",
      "file": "2026-04-09_full.json.gz",
      "size": 1234567,
      "checksum": "sha256:abc123...",
      "knowledge_count": 1234
    },
    {
      "id": "backup_20260409_002",
      "type": "incremental",
      "created_at": "2026-04-09T12:00:00+08:00",
      "based_on": "backup_20260409_001",
      "file": "2026-04-09_000_incremental.json.gz",
      "size": 12345,
      "checksum": "sha256:def456...",
      "changes_count": 12
    }
  ],
  "retention": {
    "incremental_days": 7,
    "full_weeks": 4,
    "snapshot_months": 12
  }
}
```

---

## 四、备份流程

### 4.1 定时备份（Cron）

```python
# 每日增量备份 - 凌晨2点
0 2 * * * python /path/to/memory/backup.py --type incremental

# 每周全量备份 - 周日凌晨3点
0 3 * * 0 python /path/to/memory/backup.py --type full

# 每月归档 - 每月1日凌晨4点
0 4 1 * * python /path/to/memory/backup.py --type monthly
```

### 4.2 备份脚本逻辑

```python
async def backup(type: str, based_on: str = None):
    """备份主流程"""
    
    backup_id = generate_backup_id()
    created_at = now()
    
    if type == "full":
        # 全量备份
        data = await export_all_data()
        backup_data = {
            "backup_id": backup_id,
            "type": "full",
            "created_at": created_at,
            "scope": "all",
            "data": data
        }
    
    elif type == "incremental":
        # 增量备份
        last_backup = await get_last_backup()
        changes = await compute_changes_since(last_backup)
        backup_data = {
            "backup_id": backup_id,
            "type": "incremental",
            "created_at": created_at,
            "based_on": last_backup.id,
            "changes": changes
        }
    
    elif type == "snapshot":
        # 版本快照
        data = await export_all_data()
        backup_data = {
            "snapshot_id": backup_id,
            "type": "snapshot",
            "created_at": created_at,
            "trigger": "manual",
            "data": data
        }
    
    # 压缩
    compressed = gzip.compress(json.dumps(backup_data))
    
    # 加密
    encrypted = encrypt(compressed)
    
    # 写入文件
    filename = get_backup_filename(type, created_at)
    await write_backup_file(filename, encrypted)
    
    # 更新 manifest
    await update_manifest(backup_data)
    
    # 清理过期备份
    await cleanup_old_backups()
    
    return backup_id
```

### 4.3 变化计算

```python
async def compute_changes_since(last_backup: Backup) -> Changes:
    """计算自上次备份以来的变化"""
    
    last_timestamp = last_backup.created_at
    
    # 新增的知识
    added = await db.query("""
        SELECT * FROM knowledge_nodes
        WHERE created_at > ?
    """, [last_timestamp])
    
    # 修改的知识
    modified = await db.query("""
        SELECT * FROM knowledge_nodes
        WHERE updated_at > ? AND created_at <= ?
    """, [last_timestamp, last_timestamp])
    
    # 删除的知识（从历史表）
    deleted = await db.query("""
        SELECT * FROM deleted_knowledge
        WHERE deleted_at > ?
    """, [last_timestamp])
    
    return {
        "added": added,
        "modified": modified,
        "deleted": [d.id for d in deleted]
    }
```

---

## 五、恢复流程

### 5.1 恢复类型

| 类型 | 场景 | 恢复范围 |
|------|------|---------|
| **全量恢复** | 灾难性故障 | 全部数据 |
| **时间点恢复** | 指定日期的数据 | 到指定时间点的数据 |
| **选择性恢复** | 恢复特定知识 | 单个或多个知识节点 |

### 5.2 全量恢复

```python
async def restore_full(backup_id: str):
    """全量恢复"""
    
    # 1. 创建当前数据快照（安全备份）
    current_snapshot = await create_snapshot(
        trigger="pre_restore",
        reason=f"Before restoring {backup_id}"
    )
    
    # 2. 下载并解密备份
    backup_data = await load_backup(backup_id)
    
    # 3. 验证数据完整性
    if not verify_checksum(backup_data):
        raise BackupCorruptedError(backup_id)
    
    # 4. 停止写入（暂停服务）
    await pause_writes()
    
    try:
        # 5. 清空当前数据
        await clear_all_data()
        
        # 6. 恢复数据
        await import_data(backup_data["data"])
        
        # 7. 重建索引
        await rebuild_all_indexes()
        
    finally:
        # 8. 恢复写入
        await resume_writes()
    
    # 9. 验证恢复结果
    await verify_restored_data()
    
    return {
        "success": True,
        "restored_knowledge_count": len(backup_data["data"]["knowledge_nodes"]),
        "snapshot_id": current_snapshot.id
    }
```

### 5.3 时间点恢复

```python
async def restore_point_in_time(target_time: datetime):
    """恢复到指定时间点"""
    
    # 1. 找到最近的全量备份
    base_backup = await find_nearest_full_backup(target_time)
    
    # 2. 找到目标时间之后的所有增量备份
    incremental_backups = await find_incremental_backups(
        start=base_backup.created_at,
        end=target_time
    )
    
    # 3. 依次应用增量
    data = base_backup.data
    for inc in incremental_backups:
        data = apply_changes(data, inc.changes)
        
        # 检查是否已经达到目标时间
        if inc.created_at >= target_time:
            break
    
    # 4. 创建预恢复快照
    await create_snapshot(trigger="pre_restore", reason=f"Before PIT restore to {target_time}")
    
    # 5. 执行恢复
    await restore_data(data)
    
    return {"success": True, "target_time": target_time}
```

### 5.4 选择性恢复

```python
async def restore_knowledge(knowledge_ids: List[str], backup_id: str = None):
    """选择性恢复特定知识"""
    
    # 如果未指定备份，使用最新备份
    if not backup_id:
        backup_id = await get_latest_backup_id()
    
    # 获取备份数据
    backup_data = await load_backup(backup_id)
    
    # 筛选目标知识
    target_knowledge = [
        k for k in backup_data["data"]["knowledge_nodes"]
        if k["id"] in knowledge_ids
    ]
    
    if not target_knowledge:
        raise KnowledgeNotFoundError(knowledge_ids)
    
    # 创建预恢复快照
    await create_snapshot(trigger="pre_restore", reason="Before selective restore")
    
    # 恢复指定知识
    for knowledge in target_knowledge:
        await restore_knowledge_node(knowledge)
    
    # 更新向量索引
    await update_vector_index(target_knowledge)
    
    return {
        "success": True,
        "restored_count": len(target_knowledge)
    }
```

---

## 六、导出功能

### 6.1 JSON 导出

```python
async def export_to_json(
    scope: str = "all",
    include_history: bool = True,
    include_private: bool = False
) -> str:
    """导出为 JSON 格式"""
    
    data = await collect_export_data(scope, include_history, include_private)
    
    # 格式化输出
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    return json_str
```

### 6.2 CSV 导出

```python
async def export_to_csv(scope: str = "all") -> str:
    """导出为 CSV 格式（仅知识节点）"""
    
    knowledge = await collect_knowledge_nodes(scope)
    
    # CSV 字段
    fields = [
        "id", "type", "category", "content", "value",
        "confidence", "visibility", "owner_member_id",
        "status", "created_at", "updated_at"
    ]
    
    # 生成 CSV
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    
    for k in knowledge:
        writer.writerow({f: k.get(f) for f in fields})
    
    return output.getvalue()
```

### 6.3 导出选项

| 选项 | 说明 |
|------|------|
| `scope` | `all` / `family_shared` / `member_shared` / `member_private` |
| `include_history` | 是否包含历史版本 |
| `include_private` | 是否包含私有记忆（需要额外确认） |
| `format` | `json` / `csv` |

---

## 七、安全措施

### 7.1 加密

```python
from cryptography.fernet import Fernet

class BackupEncryption:
    """备份加密"""
    
    def __init__(self, key_path: str):
        with open(key_path, "rb") as f:
            self.key = f.read()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: bytes) -> bytes:
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        return self.cipher.decrypt(encrypted_data)
```

### 7.2 校验

```python
import hashlib

def compute_checksum(data: bytes) -> str:
    """计算 SHA-256 校验和"""
    return hashlib.sha256(data).hexdigest()

async def verify_backup(backup_path: str) -> bool:
    """验证备份完整性"""
    with open(backup_path, "rb") as f:
        data = f.read()
    
    # 解密
    decrypted = encryption.decrypt(data)
    
    # 解压
    decompressed = gzip.decompress(decrypted)
    
    # 解析 JSON
    backup_data = json.loads(decompressed)
    
    # 验证校验和
    expected = backup_data["checksum"]
    actual = compute_checksum(decompressed)
    
    return expected == actual
```

---

## 八、清理策略

### 8.1 自动清理

```python
async def cleanup_old_backups():
    """清理过期备份"""
    
    manifest = await load_manifest()
    now = datetime.now()
    
    # 增量备份：保留7天
    incremental_cutoff = now - timedelta(days=7)
    
    # 全量备份：保留4周
    full_cutoff = now - timedelta(weeks=4)
    
    # 快照：保留12个月
    snapshot_cutoff = now - timedelta(days=365)
    
    # 标记待删除
    to_delete = []
    
    for backup in manifest["backups"]:
        created = parse_datetime(backup["created_at"])
        
        if backup["type"] == "incremental" and created < incremental_cutoff:
            to_delete.append(backup)
        elif backup["type"] == "full" and created < full_cutoff:
            to_delete.append(backup)
        elif backup["type"] == "snapshot" and created < snapshot_cutoff:
            to_delete.append(backup)
    
    # 执行删除
    for backup in to_delete:
        await delete_backup_file(backup["file"])
        manifest["backups"].remove(backup)
    
    await save_manifest(manifest)
```

### 8.2 保留规则总结

| 备份类型 | 保留时间 | 备注 |
|---------|---------|------|
| 增量备份 | 7天 | 每天备份 |
| 全量备份 | 4周 | 每周备份 |
| 版本快照 | 12个月 | 手动触发 |
| 灾备快照 | 永久 | 重大变更前 |
