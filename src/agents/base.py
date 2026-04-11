"""
Base Agent - 所有子 Agent 的基类
"""
import json
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI

MINIMAX_KEY = "sk-cp-ChtXE5BJLzAv9LVPJXtL0eKh3pqAK5_xlQOyf-mSt7MHCQaD8ykHVFC8UaYlEoZhi6PpSb1SL08lmBhWUaTzGSS_tzed9x20ksd_5kAGr55NPrau5BPX_0s"
MINIMAX_URL = "https://api.minimaxi.com/v1"
MINIMAX_MODEL = "MiniMax-M2.7-highspeed"


class BaseAgent(ABC):
    name: str = "BaseAgent"

    def __init__(self, model: str = MINIMAX_MODEL):
        self.model = model
        self.key = MINIMAX_KEY
        self.url = MINIMAX_URL

    @abstractmethod
    def system_prompt(self, context: dict = None) -> str:
        pass

    def run(self, user_message: str, context: dict = None) -> dict:
        from langchain_core.messages import HumanMessage, SystemMessage
        system = self.system_prompt(context)
        messages = [SystemMessage(content=system), HumanMessage(content=user_message)]

        try:
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
