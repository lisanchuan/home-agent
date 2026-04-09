"""Family Memory Center — Learning Module"""
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from .database import (
    add_pending_confirmation, get_pending_confirmations, remove_pending_confirmation,
    create_knowledge, update_confidence, get_knowledge, query_knowledge,
    increment_trigger
)
from .access_control import AccessController


class LearningEngine:
    """Passive + Active learning engine"""
    
    # Trigger patterns for passive observation
    TRIGGER_PATTERNS = {
        "explicit_statement": [
            r"我喜欢(.+)",
            r"我想要(.+)",
            r"我不喜欢(.+)",
            r"我不吃(.+)",
            r"我讨厌(.+)",
            r"我们(家)?(.+)习惯(.+)",
            r"我们(家)?总是(.+)",
        ],
        "behavioral": [
            r"又(.+)了",
            r"第\d+次(.+)",
            r"每次都(.+)",
        ],
        "preference": [
            r"觉得(.+)怎么样",
            r"喜不喜欢(.+)",
        ]
    }
    
    def __init__(self, requester_id: str = "learning", requester_type: str = "agent"):
        self.requester_id = requester_id
        self.requester_type = requester_type
        self.access = AccessController(requester_id, requester_type)
    
    def observe(self, text: str, context: Optional[str] = None) -> List[Dict]:
        """Passively observe text and extract potential knowledge"""
        findings = []
        
        # Check explicit statements
        for pattern in self.TRIGGER_PATTERNS["explicit_statement"]:
            matches = re.finditer(pattern, text)
            for m in matches:
                content = m.group(0)
                knowledge_type = self._infer_type(content)
                findings.append({
                    "content": content,
                    "type": knowledge_type,
                    "confidence": 0.6,
                    "source": "passive_observation",
                    "trigger_context": context
                })
        
        # Check behavioral patterns
        for pattern in self.TRIGGER_PATTERNS["behavioral"]:
            matches = re.finditer(pattern, text)
            for m in matches:
                content = m.group(0)
                findings.append({
                    "content": content,
                    "type": "habit",
                    "confidence": 0.5,
                    "source": "behavioral_pattern",
                    "trigger_context": context
                })
        
        return findings
    
    def _infer_type(self, content: str) -> str:
        """Infer knowledge type from content"""
        if any(w in content for w in ["喜欢", "想要", "讨厌", "不喜欢"]):
            return "preference"
        if any(w in content for w in ["习惯", "总是", "每次", "经常"]):
            return "habit"
        if any(w in content for w in ["不能", "不准", "禁止", "不许"]):
            return "taboo"
        return "fact"
    
    def propose(self, observation: Dict, owner_member_id: Optional[str] = None) -> str:
        """Propose knowledge to user for confirmation"""
        return add_pending_confirmation(
            knowledge_type=observation["type"],
            knowledge_content=observation["content"],
            suggested_value=None,
            trigger_context=observation.get("trigger_context")
        )
    
    def confirm(self, confirmation_id: str, knowledge_id: str, category: str, visibility: str):
        """Confirm pending knowledge and create actual knowledge entry"""
        # Remove from pending
        remove_pending_confirmation(confirmation_id)
        
        # Create knowledge
        kid = create_knowledge(
            content=knowledge_id,  # knowledge_id is actually content here
            knowledge_type=confirmation_id.split("_")[1] if "_" in confirmation_id else "fact",
            category=category,
            visibility=visibility,
            owner_member_id=owner_member_id,
            confidence=0.7,
            source="active_confirmation"
        )
        return kid
    
    def adjust_confidence(self, knowledge_id: str, triggered: bool = False):
        """Adjust confidence based on triggers or decay"""
        k = get_knowledge(knowledge_id)
        if not k:
            return
        
        current = k["confidence"]
        
        if triggered:
            # Boost confidence on repeated observation
            new_conf = min(1.0, current + 0.05)
            increment_trigger(knowledge_id)
        else:
            # Time-based decay
            days_old = (datetime.now() - datetime.fromisoformat(k["updated_at"])).days
            decay = days_old * 0.001  # 0.1% per day
            new_conf = max(0.3, current - decay)
        
        update_confidence(knowledge_id, new_conf)
        return new_conf
    
    def suggest_review(self) -> List[Dict]:
        """Suggest knowledge items to review"""
        # Find items with low triggers but high confidence
        # Or items not triggered in a while
        all_knowledge = query_knowledge(limit=100)
        
        suggestions = []
        for k in all_knowledge:
            if k["status"] != "active":
                continue
            updated = datetime.fromisoformat(k["updated_at"])
            days_since_update = (datetime.now() - updated).days
            
            # Suggest review if not updated in 30 days and confidence > 0.7
            if days_since_update > 30 and k["confidence"] > 0.7:
                suggestions.append({
                    **k,
                    "reason": f"30天未更新，置信度{k['confidence']:.0%}"
                })
        
        return suggestions[:10]


class ConflictResolver:
    """Resolve knowledge conflicts"""
    
    @staticmethod
    def detect_conflicts(new_content: str, scope: List[str]) -> List[Dict]:
        """Check for potential conflicts with existing knowledge"""
        new_lower = new_content.lower()
        
        # Simple keyword-based conflict detection
        conflict_indicators = ["不", "没", "不是", "不要", "不准", "禁止"]
        new_negated = any(ind in new_lower for ind in conflict_indicators)
        
        if not new_negated:
            return []
        
        # Find existing knowledge with opposite statements
        conflicts = []
        for indicator in conflict_indicators:
            if indicator in new_lower:
                keyword = new_lower.split(indicator)[-1].strip()
                existing = query_knowledge(visibility=scope[0] if scope else None, limit=50)
                for e in existing:
                    if keyword in e["content"].lower() and indicator not in e["content"].lower():
                        conflicts.append({
                            "existing": e,
                            "new": new_content,
                            "type": "potential_contradiction"
                        })
        
        return conflicts
    
    @staticmethod
    def merge_knowledge(older_id: str, newer_id: str, resolution: str = "newer") -> str:
        """Merge conflicting knowledge"""
        older = get_knowledge(older_id)
        newer = get_knowledge(newer_id)
        
        if resolution == "newer":
            # Keep newer, archive older
            from .database import soft_delete_knowledge
            soft_delete_knowledge(older_id, f"merged_with_{newer_id}")
            return newer_id
        else:
            # Keep older, archive newer
            from .database import soft_delete_knowledge
            soft_delete_knowledge(newer_id, f"merged_with_{older_id}")
            return older_id
