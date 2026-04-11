"""
LearnAgent - 学习助手，集成现有 RAG 检索
"""
import json
import sys
sys.path.insert(0, "src")
from .base import BaseAgent


class LearnAgent(BaseAgent):
    """学习助手：回答知识性问题，调用 RAG 检索"""

    name = "LearnAgent"

    def system_prompt(self, context: dict = None) -> str:
        return """你是家庭学习助手。

你的职责：
1. 回答知识性问题（历史、科学、语言等）
2. 解释概念、术语
3. 提供学习方法建议
4. 查找相关资料

回复格式（JSON）：
{
  "summary": "回答内容",
  "confidence": 0.0-1.0,
  "learnings": [
    {"type": "knowledge", "content": "xxx", "source": "user_input"}
  ]
}
"""

    def run(self, user_message: str, context: dict = None) -> dict:
        from langchain_core.messages import HumanMessage, SystemMessage
        system = self.system_prompt(context)

        history_context = ""
        if context and context.get("relevant_memories"):
            memories = context["relevant_memories"]
            history_context = "\n\n相关记忆：\n" + "\n".join([f"- {m}" for m in memories[:3]])

        full_message = f"{user_message}{history_context}"
        messages = [SystemMessage(content=system), HumanMessage(content=full_message)]

        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model=self.model, base_url=self.url, api_key=self.key, temperature=0.7)
            response = llm.invoke(messages)
            content = response.content.strip()
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = {"summary": content, "confidence": 0.7, "learnings": []}
            return result
        except Exception as e:
            return {"summary": f"错误：{str(e)}", "confidence": 0.0, "error": str(e)}
