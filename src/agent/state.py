from typing import TypedDict, List, Dict, Any, Optional
from PIL import Image
from src.device.base import BaseDevice
from src.agent.brain import GameAgentBrain
from src.utils.guardrails import SystemGuard

class AgentState(TypedDict):
    """
    Defines the shared state schema for the LangGraph automation graph.
    """
    goal: str
    package: str
    device: BaseDevice
    brain: GameAgentBrain
    guard: SystemGuard
    
    # State snapshots
    screenshot: Optional[Image.Image]
    hierarchy_xml: str
    actionable_elements: List[Dict[str, Any]]
    
    # Execution history and trackers
    action_history: List[Dict[str, Any]]
    last_action: Optional[Dict[str, Any]]
    last_result: str
    step_count: int
    max_steps: int
    
    # Terminal condition tracker
    status: str  # "running" | "success" | "failed" | "timeout"
