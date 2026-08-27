from langgraph.graph import StateGraph, END
from typing import TypedDict

class ChatState(TypedDict):
    query: str
    intent: str
    context: dict
    vendor_response: str
    final_response: str

def intent_router(state: ChatState):
    if "refund" in state["query"].lower():
        state["intent"] = "billing"
    else:
        state["intent"] = "general"
    return state

def vendor_ai_handler(state: ChatState):
    state["vendor_response"] = f"Vendor AI processed: {state['query']}"
    return state

def internal_agent_handler(state: ChatState):
    state["context"]["routed_from"] = "vendor"
    state["final_response"] = f"Internal agent resolved: {state['vendor_response']}"
    return state

def human_handoff_decision(state: ChatState):
    return "human" if state["intent"] == "billing" else "end"

workflow = StateGraph(ChatState)
workflow.add_node("intent_router", intent_router)
workflow.add_node("vendor_ai", vendor_ai_handler)
workflow.add_node("internal_agent", internal_agent_handler)
workflow.set_entry_point("intent_router")
workflow.add_edge("intent_router", "vendor_ai")
workflow.add_edge("vendor_ai", "internal_agent")
workflow.add_conditional_edges("internal_agent", human_handoff_decision, {"human": END, "end": END})
app = workflow.compile()
