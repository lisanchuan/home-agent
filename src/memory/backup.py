"""Family Memory Center — Backup & Restore Module"""
import json
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from .database import get_db, export_all_data


class BackupManager:
    """Backup and restore for Family Memory Center"""
    
    def __init__(self, data_dir: str = "./data/memory"):
        self.data_dir = Path(data_dir)
        self.backup_dir = self.data_dir / "backup"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_full(self, label: Optional[str] = None) -> str:
        """Create full backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"full_{timestamp}"
        if label:
            name = f"full_{label}_{timestamp}"
        
        backup_path = self.backup_dir / name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Backup SQLite database
        db_path = self.data_dir / "memory.db"
        if db_path.exists():
            shutil.copy2(db_path, backup_path / "memory.db")
        
        # Backup ChromaDB
        chroma_path = self.data_dir / "chroma"
        if chroma_path.exists():
            shutil.copytree(chroma_path, backup_path / "chroma", dirs_exist_ok=True)
        
        # Export JSON metadata
        data = export_all_data()
        metadata = {
            "type": "full_backup",
            "timestamp": timestamp,
            "knowledge_count": len(data.get("knowledge", [])),
            "members_count": len(data.get("members", []))
        }
        with open(backup_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Clean old backups (keep last 10)
        self._clean_old_backups(keep=10)
        
        return str(backup_path)
    
    def backup_incremental(self) -> str:
        """Create incremental backup (just database changes since last backup)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"incr_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Export current state as JSON
        data = export_all_data()
        with open(backup_path / "knowledge.json", "w") as f:
            json.dump(data["knowledge"], f, indent=2, ensure_ascii=False)
        
        # Save metadata
        metadata = {
            "type": "incremental_backup",
            "timestamp": timestamp,
            "knowledge_count": len(data.get("knowledge", []))
        }
        with open(backup_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        return str(backup_path)
    
    def restore(self, backup_path: str, restore_type: str = "full") -> bool:
        """Restore from backup"""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            print(f"Backup not found: {backup_path}")
            return False
        
        if restore_type == "full":
            # Restore SQLite
            db_backup = backup_path / "memory.db"
            if db_backup.exists():
                db_target = self.data_dir / "memory.db"
                shutil.copy2(db_backup, db_target)
            
            # Restore ChromaDB
            chroma_backup = backup_path / "chroma"
            if chroma_backup.exists():
                chroma_target = self.data_dir / "chroma"
                if chroma_target.exists():
                    shutil.rmtree(chroma_target)
                shutil.copytree(chroma_backup, chroma_target)
            
            return True
        
        elif restore_type == "incremental":
            # Load knowledge JSON and restore
            knowledge_file = backup_path / "knowledge.json"
            if not knowledge_file.exists():
                print("Knowledge data not found in backup")
                return False
            
            with open(knowledge_file) as f:
                knowledge_list = json.load(f)
            
            # Restore each knowledge item
            from .database import create_knowledge, get_db
            
            conn = get_db()
            for k in knowledge_list:
                # Check if exists
                existing = conn.execute(
                    "SELECT id FROM knowledge_nodes WHERE id = ?", (k["id"],)
                ).fetchone()
                
                if existing:
                    # Update
                    conn.execute("""
                        UPDATE knowledge_nodes 
                        SET content = ?, confidence = ?, updated_at = ?
                        WHERE id = ?
                    """, (k["content"], k.get("confidence", 0.5), datetime.now().isoformat(), k["id"]))
                else:
                    # Insert
                    create_knowledge(
                        content=k["content"],
                        knowledge_type=k.get("type", "fact"),
                        category=k.get("category", "uncategorized"),
                        visibility=k.get("visibility", "family_shared"),
                        owner_member_id=k.get("owner_member_id"),
                        value=k.get("value"),
                        confidence=k.get("confidence", 0.5),
                        source="restore"
                    )
            
            conn.commit()
            return True
        
        return False
    
    def list_backups(self) -> List[Dict]:
        """List all backups"""
        backups = []
        for b in sorted(self.backup_dir.iterdir(), reverse=True):
            if b.is_dir():
                meta_file = b / "metadata.json"
                if meta_file.exists():
                    with open(meta_file) as f:
                        meta = json.load(f)
                    backups.append({
                        "path": str(b),
                        "name": b.name,
                        **meta
                    })
                else:
                    backups.append({
                        "path": str(b),
                        "name": b.name,
                        "type": "unknown"
                    })
        return backups
    
    def delete_backup(self, backup_path: str) -> bool:
        """Delete a backup"""
        import shutil
        path = Path(backup_path)
        if path.exists() and path.parent == self.backup_dir:
            shutil.rmtree(path)
            return True
        return False
    
    def _clean_old_backups(self, keep: int = 10):
        """Clean old backups, keeping the most recent N"""
        backups = sorted(self.backup_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
        for old in backups[keep:]:
            shutil.rmtree(old)


# CLI commands for backup
def cmd_backup_full(args):
    """Create full backup"""
    from .backup import BackupManager
    bm = BackupManager()
    path = bm.backup_full(label=args.label)
    print(f"✓ Full backup created: {path}")


def cmd_backup_incr(args):
    """Create incremental backup"""
    from .backup import BackupManager
    bm = BackupManager()
    path = bm.backup_incremental()
    print(f"✓ Incremental backup created: {path}")


def cmd_restore(args):
    """Restore from backup"""
    from .backup import BackupManager
    bm = BackupManager()
    success = bm.restore(args.backup_path, restore_type=args.type)
    if success:
        print(f"✓ Restored from: {args.backup_path}")
    else:
        print(f"✗ Restore failed")


def cmd_list_backups(args):
    """List backups"""
    from .backup import BackupManager
    bm = BackupManager()
    backups = bm.list_backups()
    print(f"Found {len(backups)} backups:")
    for b in backups:
        print(f"  [{b['name']}] {b.get('type', 'unknown')} - {b.get('timestamp', 'no timestamp')}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    
    p = sub.add_parser("backup-full", help="Create full backup")
    p.add_argument("--label", help="Backup label")
    p.set_defaults(cmd=cmd_backup_full)
    
    p = sub.add_parser("backup-incr", help="Create incremental backup")
    p.set_defaults(cmd=cmd_backup_incr)
    
    p = sub.add_parser("restore", help="Restore from backup")
    p.add_argument("backup_path", help="Backup path")
    p.add_argument("--type", "-t", choices=["full", "incremental"], default="full")
    p.set_defaults(cmd=cmd_restore)
    
    p = sub.add_parser("list", help="List backups")
    p.set_defaults(cmd=cmd_list_backups)
    
    args = parser.parse_args()
    if hasattr(args, "cmd"):
        args.cmd(args)
