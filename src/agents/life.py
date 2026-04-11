"""
LifeAgent - 生活助手
"""
import json
from .base import BaseAgent


class LifeAgent(BaseAgent):
    """生活助手：日常家庭生活"""

    name = "LifeAgent"

    def system_prompt(self, context: dict = None) -> str:
        return """你是家庭生活助手。

你的职责：
1. 回答日常生活问题（饮食、健康、出行）
2. 提供家务管理建议
3. 记录家庭日常重要事项
4. 协助购物清单、计划

回复格式（JSON）：
{
  "summary": "回答内容",
  "confidence": 0.0-1.0,
  "learnings": [
    {"type": "preference", "content": "xxx", "source": "user_input"}
  ]
}
"""
