"""
LangGraph Builder - 构建状态图
"""
from langgraph.graph import StateGraph, END
from .state import HomeAgentState, initial_state
from .nodes import router_node, delegator_node, clarify_node, agent_node


def build_graph() -> StateGraph:
    """
    构建 HomeAgent 状态图

    流程：
        START → Router → Delegator → Agent → Supervisor → MemoryWriter → END
                              ↓
                         unknown → Clarify → END
    """
    graph = StateGraph(HomeAgentState)

    # 注册节点
    graph.add_node("router", router_node)
    graph.add_node("delegator", delegator_node)
    graph.add_node("clarify", clarify_node)
    graph.add_node("agent", agent_node)

    # 设置入口
    graph.set_entry_point("router")

    # Router 后的条件边
    def route_after_router(state: HomeAgentState) -> str:
        if state.get("intent") == "unknown":
            return "clarify"
        return "delegator"

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {"clarify": "clarify", "delegator": "delegator"},
    )

    # Delegator → Agent
    graph.add_edge("delegator", "agent")

    # Agent → Supervisor（暂跳过，直接 MemoryWriter）
    # Supervisor 后续接入
    graph.add_edge("agent", END)

    # Clarify 结束
    graph.add_edge("clarify", END)

    return graph.compile()


def run(user_message: str, context_history: list[str] = None) -> str:
    """运行图的便捷函数"""
    state = initial_state(user_message, context_history)
    compiled = build_graph()
    result = compiled.invoke(state)
    return result.get("final_response", "抱歉，出错了。")


if __name__ == "__main__":
    print("=== HomeAgent Graph Test ===")
    tests = ["明天开会吗？", "冰箱里还有什么菜？", "上次说的那本书"]

    for msg in tests:
        print(f"\n输入：{msg}")
        response = ru