"""Family Memory Center — Access Controller"""
from enum import Enum
from typing import List, Optional, Dict, Any
from .database import get_knowledge, get_member


class RequesterType(Enum):
    USER = "user"
    AGENT = "agent"
    LEARNING = "learning"


class Visibility(Enum):
    FAMILY_SHARED = "family_shared"
    MEMBER_SHARED = "member_shared"
    MEMBER_PRIVATE = "member_private"
    STRICTLY_PRIVATE = "strictly_private"


class AccessController:
    """Access controller for Family Memory Center"""
    
    def __init__(self, requester_id: str, requester_type: RequesterType):
        self.requester_id = requester_id
        self.requester_type = requester_type
    
    def can_read(self, knowledge: Dict[str, Any]) -> bool:
        """Check if requester can read this knowledge"""
        visibility = knowledge.get("visibility", "family_shared")
        
        # Agent and learning mechanism can read everything (with filtering)
        if self.requester_type in (RequesterType.AGENT, RequesterType.LEARNING):
            return True
        
        # Family shared: everyone can read
        if visibility == Visibility.FAMILY_SHARED.value:
            return True
        
        # Member shared: only owner or agent
        if visibility == Visibility.MEMBER_SHARED.value:
            return knowledge.get("owner_member_id") == self.requester_id
        
        # Member private: only owner or agent (with proxy)
        if visibility in (Visibility.MEMBER_PRIVATE.value, Visibility.STRICTLY_PRIVATE.value):
            return knowledge.get("owner_member_id") == self.requester_id
        
        return False
    
    def can_write(self, knowledge: Dict[str, Any] = None) -> bool:
        """Check if requester can write"""
        # Only agents and learning mechanism can write
        return self.requester_type in (RequesterType.AGENT, RequesterType.LEARNING)
    
    def filter_knowledge_list(
        self,
        knowledge_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter knowledge list based on access control"""
        if self.requester_type in (RequesterType.AGENT, RequesterType.LEARNING):
            # Agents see everything, will be filtered by query scope
            return knowledge_list
        
        filtered = []
        for k in knowledge_list:
            if self.can_read(k):
                filtered.append(k)
        return filtered
    
    def get_visible_scopes(self) -> List[str]:
        """Get list of visible scopes for this requester"""
        if self.requester_type in (RequesterType.AGENT, RequesterType.LEARNING):
            return [
                Visibility.FAMILY_SHARED.value,
                Visibility.MEMBER_SHARED.value,
                Visibility.MEMBER_PRIVATE.value,
                Visibility.STRICTLY_PRIVATE.value
            ]
        
        # For users, only family shared and own member shared
        scopes = [Visibility.FAMILY_SHARED.value]
        
        # Could add logic to check if user is a member
        if self.requester_id.startswith("member_"):
            scopes.append(Visibility.MEMBER_SHARED.value)
            scopes.append(Visibility.MEMBER_PRIVATE.value)
        
        return scopes


class QueryScope:
    """Query scope for searching knowledge"""
    
    FAMILY_SHARED = "family_shared"
    MEMBER_SHARED = "member_shared"
    MEMBER_PRIVATE = "member_private"
    
    @classmethod
    def all(cls) -> List[str]:
        return [cls.FAMILY_SHARED, cls.MEMBER_SHARED, cls.MEMBER_PRIVATE]
    
    @classmethod
    def shared_only(cls) -> List[str]:
        return [cls.FAMILY_SHARED, cls.MEMBER_SHARED]
