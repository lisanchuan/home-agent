"""
Graph 节点定义
"""
import json
import sys
from typing import Tuple

sys.path.insert(0, "src")

from .state import HomeAgentState


# ============================================================
# 路由节点
# ============================================================

INTENT_PROMPT = """你是一个家庭智能助手的消息分类器。

根据用户消息，判断属于哪个领域：

- work: 工作任务、项目、会议、邮件、技术问题
- life: 日常生活、家庭事务、健康、出行、购物、闲聊
- learn: 知识问答、学习、研究、读书
- finance: 预算、消费、理财、账单
- memory: 查找记忆、回忆过去、问"上次/之前/什么时候"
- unknown: 无法分类或以上都不是

返回 JSON 格式：
{
  "intent": "xxx",
  "confidence": 0.0-1.0
}

只返回 JSON，不要其他内容。
"""


def classify_intent(message: str, history: list[str] = None) -> dict:
    """调用 LLM 进行意图分类"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        from agents.base import MINIMAX_KEY, MINIMAX_URL, MINIMAX_MODEL
        llm = ChatOpenAI(
            model=MINIMAX_MODEL,
            base_url=MINIMAX_URL,
            api_key=MINIMAX_KEY,
            temperature=0.0,
        )

        history_text = ""
        if history:
            history_text = "\n".join([f"- {h}" for h in history[-5:]])

        messages = [
            SystemMessage(content=INTENT_PROMPT),
            HumanMessage(content=f"对话历史：\n{history_text}\n\n当前消息：{message}"),
        ]

        response = llm.invoke(messages)
        result = json.loads(response.content.strip())

        return {
            "intent": result.get("intent", "unknown"),
            "route_confidence": result.get("confidence", 0.0),
        }
    except Exception:
        # Fallback to keyword-based classification
        return _keyword_intent(message)


def _keyword_intent(message: str) -> dict:
    """关键词兜底分类"""
    work_keywords = ["工作", "项目", "会议", "邮件", "任务", "代码", "git", "pr", "开会", "上班", "同事", "老板", "客户"]
    life_keywords = ["吃饭", "出门", "买", "去哪", "家人", "孩子", "健康", "运动", "冰箱", "做菜", "家务", "购物", "超市"]
    learn_keywords = ["学习", "知识", "怎么", "为什么", "什么", "读书", "课程", "教程", "研究"]
    finance_keywords = ["钱", "花", "买", "价格", "预算", "账单", "理财", "工资", "花费", "消费"]
    memory_keywords = ["上次", "之前", "什么时候", "还记得", "回忆", "以前", "曾经"]

    msg = message.lower()

    for kw in work_keywords:
        if kw in msg:
            return {"intent": "work", "route_confidence": 0.5}
    for kw in life_keywords:
        if kw in msg:
            return {"intent": "life", "route_confidence": 0.5}
    for kw in learn_keywords:
        if kw in msg:
            return {"intent": "learn", "route_confidence": 0.5}
    for kw in finance_keywords:
        if kw in msg:
            return {"intent": "finance", "route_confidence": 0.5}
    for kw in memory_keywords:
        if kw in msg:
            return {"intent": "memory", "route_confidence": 0.5}

    return {"intent": "unknown", "route_confidence": 0.0}


def router_node(state: HomeAgentState) -> HomeAgentState:
    """入口节点：意图分类"""
    result = classify_intent(
        message=state["user_message"],
        history=state.get("context_history"),
    )
    return {
        "intent": result["intent"],
        "route_confidence": result["route_confidence"],
    }


# ============================================================
# 派发节点
# ============================================================

def delegator_node(state: HomeAgentState) -> HomeAgentState:
    """根据 intent 设置 current_agent"""
    intent = state.get("intent", "unknown")

    agent_map = {
        "work": "WorkAgent",
        "life": "LifeAgent",
        "learn": "LearnAgent",
        "finance": "FinanceAgent",
        "memory": "MemoryAgent",
    }

    current_agent = agent_map.get(intent, "Router")

    return {"current_agent": current_agent}


# ============================================================
# 子 Agent 节点
# ============================================================

def _load_agent(agent_name: str):
    """动态加载 Agent"""
    agent_map = {
        "WorkAgent": ("src.agents.work", "WorkAgent"),
        "LifeAgent": ("src.agents.life", "LifeAgent"),
        "LearnAgent": ("src.agents.learn", "LearnAgent"),
        "MemoryAgent": ("src.agents.memory", "MemoryAgent"),
    }

    if agent_name not in agent_map:
        return None

    module_path, class_name = agent_map[agent_name]
    try:
        from importlib import import_module
        module = import_module(module_path)
        return getattr(module, class_name)()
    except Exception:
        return None


def agent_node(state: HomeAgentState) -> HomeAgentState:
    """
    执行对应子 Agent
    """
    agent_name = state.get("current_agent", "")

    if agent_name == "Router":
        # unknown，回退到 clarify
        return clarify_node(state)

    agent = _load_agent(agent_name)

    if agent is None:
        return {
            "final_response": f"[错误] 无法加载 Agent：{agent_name}",
            "learnings_to_save": [],
        }

    try:
        result = agent.run(
            user_message=state["user_message"],
            context={"relevant_memories": []},
        )

        summary = result.get("summary", "")
        confidence = result.get("confidence", 0.5)
        learnings = result.get("learnings", [])

        return {
            "final_response": summary,
            "learnings_to_save": learnings,
            "agent_results": {
                agent_name: {
                    "summary": summary,
                    "confidence": confidence,
                    "learnings": learnings,
                }
            },
            "supervisor_feedback": "",
            "needs_revision": False,
        }

    except Exception as e:
        return {
            "final_response": f"[错误] {agent_name} 执行失败：{str(e)}",
            "error_message": str(e),
            "learnings_to_save": [],
        }


# ============================================================
# 澄清节点
# ============================================================

CLARIFY_PROMPT = """你是家庭智能助手。用户发送的消息无法分类。

请礼貌地请用户澄清他的需求。
保持简洁，1-2句话即可。
"""


def clarify_node(state: HomeAgentState) -> HomeAgentState:
    """当 intent=unknown 时，询问用户"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        from agents.base import MINIMAX_KEY, MINIMAX_URL, MINIMAX_MODEL

        llm = ChatOpenAI(
            model=MINIMAX_MODEL,
            base_url=MINIMAX_URL,
            api_key=MINIMAX_KEY,
            temperature=0.7,
        )

        response = llm.invoke([
            SystemMessage(content=CLARIFY_PROMPT),
            HumanMessage(content=state["user_message"]),
        ])

        return {
            "final_response": response.content.strip(),
            "needs_approval": False,
        }
    except Exception:
        return {
            "final_response": "抱歉，我没有理解你的意思。能再说一次吗？😊",
            "needs_approval": False,
        }
