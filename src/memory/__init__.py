"""Family Memory Center — Main Module"""
from typing import List, Dict, Optional, Any
from .database import (
    init_db, get_db, create_knowledge, get_knowledge, query_knowledge,
    update_confidence, increment_trigger, soft_delete_knowledge,
    create_member, get_member, get_all_members,
    add_pending_confirmation, get_pending_confirmations, remove_pending_confirmation,
    export_all_data
)
from .access_control import AccessController, RequesterType, Visibility, QueryScope
from .schema import MEMBER_DEFAULT


class MemoryCenter:
    """Main interface for Family Memory Center"""
    
    def __init__(self, requester_id: str = "system", requester_type: str = "agent"):
        self.requester_id = requester_id
        self.requester_type = RequesterType(requester_type)
        self.access = AccessController(requester_id, self.requester_type)
    
    # === Knowledge Operations ===
    
    def add_knowledge(
        self,
        content: str,
        knowledge_type: str,
        category: str,
        visibility: str,
        owner_member_id: Optional[str] = None,
        value: Optional[str] = None,
        confidence: float = 0.5,
        source: str = "learning",
        auto_index: bool = True
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
        
        # Update vector index
        if auto_index:
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
            except Exception as e:
                print(f"Warning: Failed to index knowledge: {e}")
        
        return kid
    
    def get(self, knowledge_id: str) -> Optional[Dict]:
        """Get knowledge by ID"""
        knowledge = get_knowledge(knowledge_id)
        if knowledge and self.access.can_read(knowledge):
            return knowledge
        return None
    
    def search(
        self,
        query: str,
        scope: Optional[List[str]] = None,
        n_results: int = 10,
        knowledge_type: Optional[str] = None
    ) -> List[Dict]:
        """Search knowledge using RAG"""
        # Get scopes
        if scope is None:
            scopes = self.access.get_visible_scopes()
        else:
            scopes = scope
        
        # Build filter
        filter_metadata = {
            "visibility": {"$in": scopes}
        }
        if knowledge_type:
            filter_metadata["type"] = knowledge_type
        
        # Vector search
        try:
            from ..rag.vector_store import search_vectors
            results = search_vectors(
                query=query,
                n_results=n_results * 2,  # Get more, then filter
                filter_metadata=filter_metadata
            )
            
            # Filter by access
            filtered = []
            for r in results:
                kid = r["knowledge_id"]
                k = get_knowledge(kid)
                if k and self.access.can_read(k):
                    filtered.append({
                        **k,
                        "similarity": r["similarity"]
                    })
                    if len(filtered) >= n_results:
                        break
            
            return filtered
        except Exception as e:
            print(f"Vector search failed, falling back to DB: {e}")
            # Fallback to DB search
            knowledge_list = query_knowledge(
                visibility=scopes[0] if len(scopes) == 1 else None,
                knowledge_type=knowledge_type,
                limit=n_results
            )
            return self.access.filter_knowledge_list(knowledge_list)
    
    def query(
        self,
        visibility: Optional[str] = None,
        owner_member_id: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Direct DB query with filters"""
        knowledge_list = query_knowledge(
            visibility=visibility,
            owner_member_id=owner_member_id,
            knowledge_type=knowledge_type,
            category=category,
            limit=limit
        )
        return self.access.filter_knowledge_list(knowledge_list)
    
    def update_confidence(self, knowledge_id: str, new_confidence: float):
        """Update knowledge confidence"""
        update_confidence(knowledge_id, new_confidence)
    
    def trigger(self, knowledge_id: str):
        """Record knowledge trigger (for confidence boost)"""
        increment_trigger(knowledge_id)
    
    def delete(self, knowledge_id: str, reason: str = "user_confirmed"):
        """Delete knowledge"""
        soft_delete_knowledge(knowledge_id, reason)
    
    # === Member Operations ===
    
    def add_member(
        self,
        name: str,
        relationship: str,
        role: str = "member",
        is_minor: bool = False,
        **kwargs
    ) -> str:
        """Add family member"""
        return create_member(name, relationship, role, is_minor, **kwargs)
    
    def get_member(self, member_id: str) -> Optional[Dict]:
        """Get member"""
        return get_member(member_id)
    
    def get_members(self) -> List[Dict]:
        """Get all members"""
        return get_all_members()
    
    # === Confirmation Queue ===
    
    def add_pending(
        self,
        knowledge_type: str,
        knowledge_content: str,
        suggested_value: Optional[str] = None,
        trigger_context: Optional[str] = None
    ) -> str:
        """Add pending confirmation"""
        return add_pending_confirmation(
            knowledge_type, knowledge_content, suggested_value, trigger_context
        )
    
    def get_pending(self, limit: int = 20) -> List[Dict]:
        """Get pending confirmations"""
        return get_pending_confirmifications(limit)
    
    def confirm(self, confirmation_id: str, knowledge_id: str):
        """Confirm pending knowledge"""
        remove_pending_confirmation(confirmation_id)
    
    # === Backup ===
    
    def export(self) -> Dict[str, Any]:
        """Export all data"""
        return export_all_data()
    
    # === Initialization ===
    
    @staticmethod
    def initialize():
        """Initialize database"""
        init_db()
        
        # Add default members if not exist
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


# Initialize on import
MemoryCenter.initialize()
