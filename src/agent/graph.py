from langgraph.graph import StateGraph, START, END
from src.agent.state import AgentState
from src.agent.nodes import capture_state_node, menu_navigator_node, gameplay_node, crash_recovery_node
from src.utils.logger import automation_logger

def route_after_capture(state: AgentState) -> str:
    """
    Router determining the next execution path based on the captured environment state.
    """
    status = state.get("status", "running")
    
    if status in ["success", "failed", "timeout"]:
        automation_logger.info(f"[Graph Router] Terminal status reached: {status.upper()}. Ending graph.")
        return END

    # Detect crash warnings or force recovery triggers
    last_res = state.get("last_result", "").lower()
    if "unregistered" in last_res or "crash" in last_res:
        # Check if we should recover
        # If the app crash popup was detected, dismiss it and trigger recovery node
        if "dialog" in last_res or "ignored" in last_res:
            automation_logger.info("[Graph Router] Actions failing or crash popup detected. Routing to [CrashRecovery].")
            return "crash_recovery"
            
    # Route based on XML elements presence (hybrid UI Automator / Visual canvas routing)
    if len(state.get("actionable_elements", [])) > 0:
        automation_logger.info("[Graph Router] UI elements detected. Routing to [MenuNavigator].")
        return "menu_navigator"
    else:
        automation_logger.info("[Graph Router] Graphics canvas detected. Routing to [Gameplay].")
        return "gameplay"

# Initialize state graph builder
builder = StateGraph(AgentState)

# Add Node Functions
builder.add_node("capture_state", capture_state_node)
builder.add_node("menu_navigator", menu_navigator_node)
builder.add_node("gameplay", gameplay_node)
builder.add_node("crash_recovery", crash_recovery_node)

# Set Entry Point
builder.add_edge(START, "capture_state")

# Define Routing Edges
builder.add_conditional_edges(
    "capture_state",
    route_after_capture,
    {
        "menu_navigator": "menu_navigator",
        "gameplay": "gameplay",
        "crash_recovery": "crash_recovery",
        END: END
    }
)

# Nodes return to capture state
builder.add_edge("menu_navigator", "capture_state")
builder.add_edge("gameplay", "capture_state")
builder.add_edge("crash_recovery", "capture_state")

# Compile the graph
compiled_graph = builder.compile()
automation_logger.info("[Graph] LangGraph workflow compiled successfully.")
