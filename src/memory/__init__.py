"""Family Memory Center — Main Module"""
from .database import (
    init_db, get_db, create_knowledge, get_knowledge, query_knowledge,
    update_confidence, increment_trigger, soft_delete_knowledge,
    create_member, get_member, get_all_members,
    add_pending_confirmation, get_pending_confirmations, remove_pending_confirmation,
    export_all_data
)
from .access_control import AccessController
from .learning import LearningEngine, ConflictResolver
from .backup import BackupManager


class MemoryCenter:
    """Main interface for Family Memory Center"""
    
    def __init__(self, requester_id: str = "system", requester_type: str = "agent"):
        self.requester_id = requester_id
        self.requester_type = requester_type
        self.access = AccessController(requester_id, requester_type)
        self.learning = LearningEngine(requester_id, requester_type)
    
    # === Knowledge Operations ===
    
    def add_knowledge(
        self,
        content: str,
        knowledge_type: str,
        category: str,
        visibility: str,
        owner_member_id: str = None,
        value: str = None,
        confidence: float = 0.5,
        source: str = "manual"
    ) -> str:
        """Add new knowledge"""
        kid = create_knowledge(
            content=content,
            knowledge_type=knowledge_type,
            category=category,
            visibility=visibility,
            owner_member_id=owner_member_id,
            value=value,
            confidence=confidence,
            source=source
        )
        
        # Try to index in vector store
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from rag.vector_store import add_knowledge_vector
            add_knowledge_vector(
                knowledge_id=kid,
                content=content,
                metadata={
                    "knowledge_id": kid,
                    "type": knowledge_type,
                    "category": category,
                    "visibility": visibility,
                    "owner_member_id": owner_member_id,
                    "confidence": confidence
                }
            )
        except Exception:
            pass
        
        return kid
    
    def get(self, knowledge_id: str):
        return get_knowledge(knowledge_id)
    
    def search(self, query: str, scopes: list = None, n_results: int = 10):
        """Search using RAG"""
        from rag.query import RAGQueryEngine
        engine = RAGQueryEngine(self.requester_id, self.requester_type)
        return engine.query(query, scope=scopes, n_results=n_results)
    
    def query(self, visibility: str = None, owner_member_id: str = None,
               knowledge_type: str = None, category: str = None, limit: int = 100):
        """Direct DB query"""
        rows = query_knowledge(
            visibility=visibility,
            owner_member_id=owner_member_id,
            knowledge_type=knowledge_type,
            category=category,
            limit=limit
        )
        return self.access.filter_knowledge_list(rows)
    
    def delete(self, knowledge_id: str, reason: str = "user_confirmed"):
        soft_delete_knowledge(knowledge_id, reason)
    
    def export(self):
        return export_all_data()
    
    # === Member Operations ===
    
    def add_member(self, name: str, relationship: str, role: str = "member",
                   is_minor: bool = False, **kwargs) -> str:
        return create_member(name, relationship, role, is_minor, **kwargs)
    
    def get_member(self, member_id: str):
        return get_member(member_id)
    
    def get_members(self):
        return get_all_members()
    
    # === Confirmation Queue ===
    
    def get_pending(self, limit: int = 20):
        return get_pending_confirmations(limit)
    
    def confirm(self, confirmation_id: str, content: str, knowledge_type: str,
                category: str, visibility: str, owner_member_id: str = None):
        remove_pending_confirmation(confirmation_id)
        return create_knowledge(
            content=content,
            knowledge_type=knowledge_type,
            category=category,
            visibility=visibility,
            owner_member_id=owner_member_id,
            confidence=0.7,
            source="active_confirmation"
        )
    
    # === Learning ===
    
    def observe(self, text: str, context: str = None) -> list:
        """Passively observe text"""
        return self.learning.observe(text, context)
    
    def adjust_confidence(self, knowledge_id: str, triggered: bool = False):
        return self.learning.adjust_confidence(knowledge_id, triggered)
    
    # === Backup ===
    
    def backup_full(self, label: str = None) -> str:
        bm = BackupManager()
        return bm.backup_full(label)
    
    def backup_incremental(self) -> str:
        bm = BackupManager()
        return bm.backup_incremental()
    
    def list_backups(self) -> list:
        bm = BackupManager()
        return bm.list_backups()
    
    def restore(self, backup_path: str, restore_type: str = "full") -> bool:
        bm = BackupManager()
        return bm.restore(backup_path, restore_type)
    
    # === Initialization ===
    
    @staticmethod
    def initialize():
        from .database import init_db, get_all_members
        from .schema import MEMBER_DEFAULT
        init_db()
        existing = get_all_members()
        if not existing:
            for name, data in MEMBER_DEFAULT.items():
                create_member(
                    name=data["name"],
                    relationship=data["relationship"],
                    role=data["role"],
                    is_minor=data["is_minor"],
                    disclosure_level=data["disclosure_level"],
                    allow_agent_proxy=data["allow_agent_proxy"],
                    allow_spouse_view=data["allow_spouse_view"],
                    proxy_level=data["proxy_level"]
                )
            print("Default members created")


MemoryCenter.initialize()
