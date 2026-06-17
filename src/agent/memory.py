from typing import Dict, List, Any

class AgentMemory:
    """
    Maintains the state and past action history of the agent loop.
    Prevents cyclic behavior and provides state context to the cognitive brain.
    """

    def __init__(self, max_history_len: int = 5):
        self.max_history_len = max_history_len
        self.history: List[Dict[str, Any]] = []
        self.current_goal: str = ""

    def set_goal(self, goal: str):
        self.current_goal = goal

    def add_action(self, state_summary: str, action: Dict[str, Any], result: str):
        """
        Record an action, context, and result in memory.
        """
        self.history.append({
            "state": state_summary,
            "action": action,
            "result": result
        })
        if len(self.history) > self.max_history_len:
            self.history.pop(0)

    def get_history_summary(self) -> str:
        """
        Return a text summary of the recent action history.
        """
        if not self.history:
            return "No history recorded yet."

        summary = []
        for i, entry in enumerate(self.history):
            action = entry["action"]
            action_desc = f"{action.get('action')} on '{action.get('target_label')}' at {action.get('coordinates')}"
            summary.append(
                f"Step {i+1}: Context: {entry['state']}\n"
                f"        Action taken: {action_desc}\n"
                f"        Verification result: {entry['result']}"
            )
        return "\n".join(summary)

    def clear(self):
        self.history.clear()
        self.current_goal = ""
