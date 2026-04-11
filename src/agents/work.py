"""
WorkAgent - 工作助手
"""
import json
from .base import BaseAgent


class WorkAgent(BaseAgent):
    """工作助手：处理工作任务、项目管理"""

    name = "WorkAgent"

    def system_prompt(self, context: dict = None) -> str:
        return """你是家庭工作助手。

你的职责：
1. 协助处理工作任务、项目管理
2. 整理会议记录、待办事项
3. 提供技术问题解答
4. 帮助制定计划

回复格式（JSON）：
{
  "summary": "回答内容",
  "confidence": 0.0-1.0,
  "action_items": ["待办1", "待办2"],  // 可选
  "learnings": []
}
"""
