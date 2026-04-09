"""Family Memory Center — Query Engine"""
import re
from typing import List, Dict, Optional


class QueryUnderstanding:
    """Parse and understand natural language queries"""
    
    PATTERNS = {
        "who": r"^(谁|是哪位|是谁)",
        "what": r"^(什么|是什么|有哪些|有什么)",
        "when": r"^(什么时候|几点|周几|哪天|什么时间)",
        "where": r"^(在哪里|哪儿|什么地点)",
        "why": r"^(为什么|原因)",
        "how": r"^(怎么|如何|怎样)",
        "preference": r"(喜欢|偏好|讨厌|不喜欢|想要|想|要)",
        "habit": r"(习惯|经常|总是|通常|一般|每天|每周|每月)",
        "fact": r"(是|就是|不会变|确定)",
    }
    
    @classmethod
    def parse(cls, query: str) -> Dict:
        query = query.strip()
        intent = "general"
        for name, pattern in cls.PATTERNS.items():
            if re.search(pattern, query):
                intent = name
                break
        
        stop_words = {"的", "是", "在", "有", "和", "了", "我", "你", "他", "她", "它", "我们", "你们", "他们", "什么", "谁", "怎么", "如何", "怎样", "哪里", "哪儿"}
        words = re.findall(r'[\w]+', query)
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        
        return {
            "original": query,
            "intent": intent,
            "keywords": keywords,
            "is_question": "?" in query or any(q in query for q in ["谁", "什么", "怎么", "为什么", "如何", "哪里"])
        }
    
    @classmethod
    def suggest_filters(cls, parsed: Dict) -> Dict:
        filters = {}
        if parsed["intent"] == "preference":
            filters["type"] = "preference"
        elif parsed["intent"] == "habit":
            filters["type"] = "habit"
        elif parsed["intent"] == "fact":
            filters["type"] = "fact"
        return filters


class HybridRetriever:
    """Hybrid retrieval: vector + keyword"""
    
    def __init__(self, top_k: int = 20):
        self.top_k = top_k
    
    def retrieve(self, query: str, scopes: List[str], filters: Optional[Dict] = None) -> List[Dict]:
        results = []
        vector_results = self._vector_search(query, scopes, filters)
        results.extend(vector_results)
        keyword_results = self._keyword_search(query, scopes, filters)
        seen = set()
        merged = []
        for r in results + keyword_results:
            if r["id"] not in seen:
                seen.add(r["id"])
                merged.append(r)
        reranked = self._rerank(merged, query)
        return reranked[:self.top_k]
    
    def _vector_search(self, query: str, scopes: List[str], filters: Optional[Dict]) -> List[Dict]:
        try:
            from .vector_store import search_vectors
            from ..memory.database import get_knowledge
            filter_meta = {"visibility": {"$in": scopes}}
            if filters:
                for k, v in filters.items():
                    filter_meta[k] = v
            vec_results = search_vectors(query=query, n_results=self.top_k * 2, filter_metadata=filter_meta)
            results = []
            for vr in vec_results:
                kid = vr["knowledge_id"]
                k = get_knowledge(kid)
                if k:
                    results.append({**k, "similarity": vr["similarity"], "search_type": "vector"})
            return results
        except (ImportError, Exception) as e:
            print(f"Vector search unavailable: {e}")
            return []
    
    def _keyword_search(self, query: str, scopes: List[str], filters: Optional[Dict]) -> List[Dict]:
        keywords = QueryUnderstanding.parse(query)["keywords"]
        if not keywords:
            return []
        try:
            from ..memory.database import query_knowledge
            rows = query_knowledge(
                visibility=scopes[0] if len(scopes) == 1 else None,
                knowledge_type=filters.get("type") if filters else None,
                limit=self.top_k
            )
            results = []
            for r in rows:
                content_lower = r["content"].lower()
                if any(kw.lower() in content_lower for kw in keywords):
                    results.append({**r, "keyword_match": True, "search_type": "keyword"})
            return results
        except Exception as e:
            print(f"Keyword search failed: {e}")
            return []
    
    def _rerank(self, results: List[Dict], query: str) -> List[Dict]:
        if not results:
            return []
        parsed = QueryUnderstanding.parse(query)
        query_keywords = set(parsed["keywords"])
        scored = []
        for r in results:
            score = 0.0
            if "similarity" in r:
                score += r["similarity"] * 0.4
            if parsed["intent"] == r.get("type"):
                score += 0.2
            content_lower = r["content"].lower()
            for kw in query_keywords:
                if kw.lower() in content_lower:
                    score += 0.1
            score += r.get("confidence", 0.5) * 0.1
            if r.get("keyword_match"):
                score += 0.2
            scored.append((score, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored]


class RAGQueryEngine:
    """Main RAG query engine"""
    
    def __init__(self, requester_id: str = "system", requester_type: str = "agent"):
        self.requester_id = requester_id
        self.requester_type = requester_type
        self.access = None
        self.retriever = HybridRetriever()
    
    @property
    def access_ctrl(self):
        if self.access is None:
            from ..memory.access_control import AccessController
            self.access = AccessController(self.requester_id, self.requester_type)
        return self.access
    
    def query(self, user_query: str, scope: Optional[List[str]] = None, n_results: int = 10, include_context: bool = True) -> Dict:
        parsed = QueryUnderstanding.parse(user_query)
        if scope is None:
            scopes = self.access_ctrl.get_visible_scopes()
        else:
            scopes = scope
        filters = QueryUnderstanding.suggest_filters(parsed)
        results = self.retriever.retrieve(query=user_query, scopes=scopes, filters=filters)
        filtered = self.access_ctrl.filter_knowledge_list(results)
        final_results = filtered[:n_results]
        response = {
            "query": user_query,
            "parsed_intent": parsed["intent"],
            "results_count": len(final_results),
            "results": final_results
        }
        if include_context:
            response["context"] = self._build_context(final_results)
        return response
    
    def _build_context(self, results: List[Dict]) -> str:
        if not results:
            return "没有找到相关记忆。"
        lines = ["相关记忆："]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. [{r['type']}] {r['content']}")
            if r.get("value"):
                lines.append(f"   值: {r['value']}")
            lines.append(f"   置信度: {r.get('confidence', 0.5):.0%} | 更新时间: {r.get('updated_at', '未知')}")
        return "\n".join(lines)
    
    def ask(self, question: str) -> str:
        result = self.query(question)
        if not result["results"]:
            return "我没有找到相关的记忆信息。"
        lines = [f"找到 {result['results_count']} 条相关信息：\n"]
        for r in result["results"]:
            lines.append(f"▸ {r['content']}")
            if r.get("value"):
                lines.append(f"  （{r['value']}）")
            lines.append("")
        return "\n".join(lines)
