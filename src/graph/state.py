"""
HomeAgentState - LangGraph 状态定义
"""
from typing import TypedDict, Literal, Optional
from datetime import datetime


class HomeAgentState(TypedDict, total=False):
    # === 路由层 ===
    intent: Literal["work", "life", "learn", "finance", "memory", "unknown"]
    route_confidence: float  # 0-1

    # === 请求层 ===
    user_message: str
    context_history: list[str]  # 最近5条对话历史

    # === 计划层 ===
    plan: list[str]  # 复杂任务分解步骤
    current_step: int

    # === 执行层 ===
    current_agent: str
    agent_results: dict  # {agent_name: {"summary": str, "confidence": float, "learnings": list}}
    supervisor_feedback: str
    needs_revision: bool

    # === 输出层 ===
    final_response: str
    learnings_to_save: list[dict]

    # === 控制层 ===
    iteration_count: int
    max_iterations: int
    needs_approval: bool
    approval_context: str
    error_message: str
    fallback_triggered: bool


def initial_state(user_message: str, context_history: list[str] = None) -> HomeAgentState:
    """构建初始状态"""
    return HomeAgentState(
        intent="unknown",
        route_confidence=0.0,
        user_message=user_message,
        context_history=context_history or [],
        plan=[],
        current_step=0,
        current_agent="",
        agent_results={},
        supervisor_feedback="",
        needs_revision=False,
        final_response="",
        learnings_to_save=[],
        iteration_count=0,
        max_iterations=3,
        needs_approval=False,
        approval_context="",
        error_message="",
        fallback_triggered=False,
    )
