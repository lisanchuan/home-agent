"""Family Memory Center — Database Module"""
import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "memory"
DB_PATH = DATA_DIR / "memory.db"


def get_db() -> sqlite3.Connection:
    """Get database connection"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with schema"""
    from .schema import SCHEMA_SQL
    
    conn = get_db()
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def now_iso() -> str:
    """Get current time in ISO format"""
    return datetime.now().isoformat()


def gen_id(prefix: str = "kn") -> str:
    """Generate unique ID"""
    date_str = datetime.now().strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:8]
    return f"{prefix}_{date_str}_{short_uuid}"


# === Knowledge CRUD ===

def create_knowledge(
    content: str,
    knowledge_type: str,
    category: str,
    visibility: str,
    owner_member_id: Optional[str] = None,
    value: Optional[str] = None,
    confidence: float = 0.5,
    source: str = "learning"
) -> str:
    """Create a new knowledge node"""
    conn = get_db()
    try:
        kid = gen_id("kn")
        now = now_iso()
        
        conn.execute("""
            INSERT INTO knowledge_nodes
            (id, type, category, content, value, confidence, visibility,
             owner_member_id, source, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
        """, [kid, knowledge_type, category, content, value, confidence,
              visibility, owner_member_id, source, now, now])
        
        conn.commit()
        return kid
    finally:
        conn.close()


def get_knowledge(knowledge_id: str) -> Optional[Dict]:
    """Get knowledge by ID"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM knowledge_nodes WHERE id = ?", [knowledge_id]
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def query_knowledge(
    visibility: Optional[str] = None,
    owner_member_id: Optional[str] = None,
    knowledge_type: Optional[str] = None,
    category: Optional[str] = None,
    status: str = "active",
    limit: int = 100
) -> List[Dict]:
    """Query knowledge with filters"""
    conn = get_db()
    try:
        sql = "SELECT * FROM knowledge_nodes WHERE 1=1"
        params = []
        
        if visibility:
            sql += " AND visibility = ?"
            params.append(visibility)
        if owner_member_id:
            sql += " AND owner_member_id = ?"
            params.append(owner_member_id)
        if knowledge_type:
            sql += " AND type = ?"
            params.append(knowledge_type)
        if category:
            sql += " AND category = ?"
            params.append(category)
        if status:
            sql += " AND status = ?"
            params.append(status)
        
        sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def fts5_search(query: str, limit: int = 20) -> List[Dict]:
    """Full-text search using search_text column (FTS5 fallback)"""
    conn = get_db()
    try:
        # Use search_text column with LIKE
        sql = """
            SELECT * FROM knowledge_nodes
            WHERE status = 'active'
            AND (content LIKE ? OR category LIKE ? OR search_text LIKE ?)
            ORDER BY updated_at DESC
            LIMIT ?
        """
        like_pattern = f"%{query}%"
        rows = conn.execute(sql, (like_pattern, like_pattern, like_pattern, limit)).fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Search error: {e}")
        return []
    finally:
        conn.close()


def update_confidence(knowledge_id: str, new_confidence: float):
    """Update knowledge confidence"""
    conn = get_db()
    try:
        now = now_iso()
        conn.execute("""
            UPDATE knowledge_nodes
            SET confidence = ?, updated_at = ?
            WHERE id = ?
        """, [new_confidence, now, knowledge_id])
        conn.commit()
    finally:
        conn.close()


def increment_trigger(knowledge_id: str):
    """Increment trigger count"""
    conn = get_db()
    try:
        now = now_iso()
        conn.execute("""
            UPDATE knowledge_nodes
            SET trigger_count = trigger_count + 1,
                last_triggered_at = ?, updated_at = ?
            WHERE id = ?
        """, [now, now, knowledge_id])
        conn.commit()
    finally:
        conn.close()


def soft_delete_knowledge(knowledge_id: str, reason: str = "user_confirmed"):
    """Soft delete knowledge"""
    conn = get_db()
    try:
        # Get current data
        row = conn.execute(
            "SELECT * FROM knowledge_nodes WHERE id = ?", [knowledge_id]
        ).fetchone()
        
        if row:
            # Move to deleted_knowledge
            conn.execute("""
                INSERT INTO deleted_knowledge (id, knowledge_id, content, deleted_at, delete_reason)
                VALUES (?, ?, ?, ?, ?)
            """, [gen_id("del"), knowledge_id, row["content"], now_iso(), reason])
            
            # Remove from main table
            conn.execute("DELETE FROM knowledge_nodes WHERE id = ?", [knowledge_id])
        
        conn.commit()
    finally:
        conn.close()


# === Member CRUD ===

def create_member(
    name: str,
    relationship: str,
    role: str = "member",
    is_minor: bool = False,
    **kwargs
) -> str:
    """Create a new member"""
    conn = get_db()
    try:
        mid = gen_id("member")
        now = now_iso()
        
        conn.execute("""
            INSERT INTO members
            (id, name, relationship, role, is_minor, disclosure_level,
             allow_agent_proxy, allow_spouse_view, proxy_level, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            mid, name, relationship, role, int(is_minor),
            kwargs.get("disclosure_level", "normal"),
            int(kwargs.get("allow_agent_proxy", True)),
            int(kwargs.get("allow_spouse_view", True)),
            kwargs.get("proxy_level", "none"),
            now, now
        ])
        
        conn.commit()
        return mid
    finally:
        conn.close()


def get_member(member_id: str) -> Optional[Dict]:
    """Get member by ID"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM members WHERE id = ?", [member_id]
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_members() -> List[Dict]:
    """Get all members"""
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM members ORDER BY role, name").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


# === Pending Confirmations ===

def add_pending_confirmation(
    knowledge_type: str,
    knowledge_content: str,
    suggested_value: Optional[str] = None,
    trigger_context: Optional[str] = None,
    expires_hours: int = 72
) -> str:
    """Add pending confirmation request"""
    conn = get_db()
    try:
        pid = gen_id("pc")
        now = now_iso()
        expires = (datetime.now() + timedelta(hours=expires_hours)).isoformat()
        
        conn.execute("""
            INSERT INTO pending_confirmations
            (id, knowledge_type, knowledge_content, suggested_value,
             trigger_context, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [pid, knowledge_type, knowledge_content, suggested_value,
              trigger_context, now, expires])
        
        conn.commit()
        return pid
    finally:
        conn.close()


def get_pending_confirmations(limit: int = 20) -> List[Dict]:
    """Get pending confirmations"""
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT * FROM pending_confirmations
            WHERE expires_at > ?
            ORDER BY created_at DESC
            LIMIT ?
        """, [now_iso(), limit]).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def remove_pending_confirmation(confirmation_id: str):
    """Remove pending confirmation"""
    conn = get_db()
    try:
        conn.execute(
            "DELETE FROM pending_confirmations WHERE id = ?",
            [confirmation_id]
        )
        conn.commit()
    finally:
        conn.close()


# === Export / Import ===

def export_all_data() -> Dict[str, Any]:
    """Export all data for backup"""
    conn = get_db()
    try:
        knowledge = [dict(row) for row in
                     conn.execute("SELECT * FROM knowledge_nodes").fetchall()]
        members = [dict(row) for row in
                   conn.execute("SELECT * FROM members").fetchall()]
        history = [dict(row) for row in
                   conn.execute("SELECT * FROM knowledge_history").fetchall()]
        
        return {
            "knowledge_nodes": knowledge,
            "members": members,
            "knowledge_history": history,
            "exported_at": now_iso()
        }
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
