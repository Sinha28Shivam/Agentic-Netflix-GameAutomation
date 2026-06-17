import time
from typing import Dict, Any
from src.agent.state import AgentState
from src.perception.hierarchy_parser import HierarchyParser
from src.utils.logger import automation_logger
from src.utils.guardrails import ActionVerifier

# Import all registered skills modularly
from src.agent.skills import (
    open_games_tab,
    search_game_by_name,
    scroll_catalog,
    select_netflix_profile,
    install_game_from_store,
    toggle_network_connection,
    rotate_device_orientation,
    adjust_device_volume
)

def normalize_coordinates(coords: list[int], screen_size: tuple[int, int]) -> list[int]:
    """
    Validates and corrects VLM coordinate output if it mixes up portrait/landscape dimensions.
    """
    if not coords or len(coords) < 2:
        return coords
        
    w, h = screen_size
    x, y = coords[0], coords[1]
    
    # Check if Y is out of bounds for height, but fits within width (potential orientation scaling bug)
    if y >= h:
        if w > h and y < w:
            pct = y / w
            y = int(pct * h)
            automation_logger.warning(f"[Coords Correction] Corrected Y coordinate from {coords[1]} to {y} (re-scaled from landscape width)")
            
    # Check if X is out of bounds for width
    if x >= w:
        if h > w and x < h:
            pct = x / h
            x = int(pct * w)
            automation_logger.warning(f"[Coords Correction] Corrected X coordinate from {coords[0]} to {x}")

    # General clamping to ensure it is strictly within screen boundaries
    x = max(0, min(x, w - 1))
    y = max(0, min(y, h - 1))
    
    if len(coords) == 4:
        x2, y2 = coords[2], coords[3]
        if y2 >= h and w > h and y2 < w:
            y2 = int((y2 / w) * h)
        if x2 >= w and h > w and x2 < h:
            x2 = int((x2 / h) * w)
        x2 = max(0, min(x2, w - 1))
        y2 = max(0, min(y2, h - 1))
        return [x, y, x2, y2]
        
    return [x, y]

def capture_state_node(state: AgentState) -> Dict[str, Any]:
    """
    Senses the current device environment: dismisses popups, takes screenshots, 
    and extracts XML elements. Handles DRM-blocked screens gracefully.
    """
    device = state["device"]
    guard = state["guard"]
    
    # 1. Increment step count
    step_count = state.get("step_count", 0) + 1
    automation_logger.info(f"\n--- LangGraph Node [CaptureState] | Step {step_count} of {state['max_steps']} ---")
    
    # 2. Dismiss system crashes/dialogs
    dismissed = guard.dismiss_system_dialogs()
    if dismissed:
        automation_logger.info("System alert dismissed by Guard. Cooling down 1.5s...")
        time.sleep(1.5)

    # 3. Capture Screen
    screenshot = device.take_screenshot()

    # Determine status (timeout check)
    status = "running"
    if step_count > state["max_steps"]:
        automation_logger.warning("Max steps reached. Forcing loop timeout.")
        status = "timeout"

    # 4. DRM Gate Check
    if screenshot.info.get("drm_blocked"):
        automation_logger.error(
            "[CaptureState] DRM or screencap block detected. "
            "Vision layer unavailable. Switching to accessibility-tree-only mode."
        )
        # Still attempt hierarchy dump — this works even when screenshot is blocked
        xml_content = device.dump_hierarchy()
        actionable_elements = HierarchyParser.get_actionable_elements(xml_content)
        
        if not actionable_elements:
            # Both screenshot AND accessibility tree are dead — agent is completely blind
            automation_logger.error(
                "[CaptureState] Accessibility tree also empty. "
                "Agent has no perception input. Terminating run."
            )
            return {
                "screenshot": screenshot,
                "hierarchy_xml": "",
                "actionable_elements": [],
                "step_count": step_count,
                "status": "failed",
                "last_result": "BLOCKED: No screenshot and no accessibility tree. DRM or render issue."
            }
        
        # Accessibility tree exists — agent can still operate without vision
        automation_logger.warning(
            f"[CaptureState] Running in accessibility-tree-only mode. "
            f"Elements found: {len(actionable_elements)}. Visual defect detection is disabled."
        )
        return {
            "screenshot": screenshot,        # still passed — brain will get black image
            "hierarchy_xml": xml_content,
            "actionable_elements": actionable_elements,
            "step_count": step_count,
            "status": status,
            "last_result": "DRM_MODE: Vision blocked. Using accessibility tree only."
        }

    # Normal path — screenshot is valid
    xml_content = device.dump_hierarchy()
    actionable_elements = HierarchyParser.get_actionable_elements(xml_content)
    
    automation_logger.info(f"Screen captured ({screenshot.size}). XML elements found: {len(actionable_elements)}")
    
    return {
        "screenshot": screenshot,
        "hierarchy_xml": xml_content,
        "actionable_elements": actionable_elements,
        "step_count": step_count,
        "status": status
    }

def menu_navigator_node(state: AgentState) -> Dict[str, Any]:
    """
    Cognitive node for navigating standard menus (profile select, home page, details page).
    Executes input actions or runs high-level skills.
    """
    if state["status"] != "running":
        return {}

    device = state["device"]
    brain = state["brain"]
    screenshot = state["screenshot"]
    actionable_elements = state["actionable_elements"]
    action_history = state.get("action_history", [])
    
    # Create temporary memory object to get prompt formatted history
    # Keeps modular adapter compatible with state layout
    from src.agent.memory import AgentMemory
    temp_mem = AgentMemory()
    temp_mem.set_goal(state["goal"])
    temp_mem.history = action_history

    # Brain decides next action
    decision = brain.decide_action(screenshot, actionable_elements, temp_mem, screenshot.size)
    
    analysis = decision.get("analysis", "No analysis provided.")
    action_type = decision.get("action", "WAIT").upper()
    coordinates = decision.get("coordinates")
    target_label = decision.get("target_label", "Unknown target")
    expected_outcome = decision.get("expected_outcome", "")

    automation_logger.info(f"[MenuNavigator Node] Brain Thought: {analysis}")
    automation_logger.info(f"[MenuNavigator Node] Decision: {action_type} on '{target_label}' | Coords: {coordinates}")

    # Terminal check
    if action_type == "SUCCESS":
        return {"status": "success", "last_action": decision}
    elif action_type == "FAILED":
        return {"status": "failed", "last_action": decision}

    # Execute Action
    success = False
    
    # Check if a specific high-level skill should be triggered
    # (Matches label or action keyword strings)
    normalized_target = target_label.lower()
    normalized_action = action_type.lower()
    
    if "games tab" in normalized_target or "open_games_tab" in normalized_action:
        success = open_games_tab(device)
    elif "profile" in normalized_target and "select" in normalized_action:
        # Extract profile name from target label or goal
        profile_name = "Shivam"
        if "shivan" in normalized_target:
            profile_name = "Shivani"
        success = select_netflix_profile(device, profile_name)
    elif "search" in normalized_action or "search" in normalized_target:
        # Extract name to search
        game_name = "Snake"
        if "snake" in state["goal"].lower():
            game_name = "Snake.io"
        success = search_game_by_name(device, game_name)
    elif "scroll" in normalized_action or "swipe catalog" in normalized_target:
        direction = "down" if "down" in normalized_target else "up"
        success = scroll_catalog(device, direction)
    elif "install" in normalized_action or "install" in normalized_target:
        game_pkg = "com.netflix.NGP.Snakeio" if "snake" in state["goal"].lower() or "snake" in normalized_target else state["package"]
        success = install_game_from_store(device, game_pkg)
    elif "launch" in normalized_action or "launch" in normalized_target or "play game" in normalized_target:
        game_pkg = "com.netflix.NGP.Snakeio" if "snake" in state["goal"].lower() or "snake" in normalized_target else state["package"]
        automation_logger.info(f"Launching application package: {game_pkg}")
        success = device.launch_app(game_pkg)
    else:
        # Standard low-level execution fallback
        if action_type == "TAP" and coordinates:
            coords = normalize_coordinates(coordinates, screenshot.size)
            
            # Check if this is a repeated tap on the same coordinates
            is_repeat = False
            if action_history:
                last_hist = action_history[-1]
                last_act = last_hist.get("action", {})
                if last_act.get("action") == "TAP" and last_act.get("coordinates") == coordinates:
                    if "static" in last_hist.get("result", "").lower():
                        is_repeat = True
            
            if is_repeat:
                import random
                offset_x = coords[0] + random.choice([-25, 25])
                offset_y = coords[1] + random.choice([-25, 25])
                # Ensure offset stays in bounds
                w, h = screenshot.size
                offset_x = max(0, min(offset_x, w - 1))
                offset_y = max(0, min(offset_y, h - 1))
                
                automation_logger.warning(f"[Action Recovery] Previous tap failed. Retrying with offset double-tap at ({offset_x}, {offset_y})")
                device.tap(offset_x, offset_y)
                time.sleep(0.15)
                success = device.tap(offset_x, offset_y)
            else:
                automation_logger.info(f"Executing raw ADB TAP at {coords[0]}, {coords[1]}")
                success = device.tap(coords[0], coords[1])
        elif action_type == "SWIPE" and coordinates and len(coordinates) == 4:
            coords = normalize_coordinates(coordinates, screenshot.size)
            success = device.swipe(coords[0], coords[1], coords[2], coords[3])
        elif action_type == "KEY_BACK":
            success = device.keyevent(4)
        elif action_type == "WAIT":
            time.sleep(3.0)
            success = True

    # Verification checks
    time.sleep(2.0)  # wait for animations
    post_screenshot = device.take_screenshot()
    post_xml = device.dump_hierarchy()
    
    # Resolve active package name
    active_pkg = "com.netflix.NGP.Snakeio" if "snake" in state["goal"].lower() or "snake" in target_label.lower() else state["package"]
    
    verified, msg = ActionVerifier.verify_action(
        before_img=screenshot,
        after_img=post_screenshot,
        action_type=action_type,
        expected_outcome=expected_outcome,
        post_xml=post_xml,
        package_name=active_pkg
    )
    
    automation_logger.info(f"[MenuNavigator Verification] {msg}")

    # Update state history
    step_summary = f"Action: {action_type} on '{target_label}'"
    new_history = action_history + [{
        "state": step_summary,
        "action": decision,
        "result": msg
    }]

    return {
        "action_history": new_history,
        "last_action": decision,
        "last_result": msg
    }

def gameplay_node(state: AgentState) -> Dict[str, Any]:
    """
    Cognitive node for gameplay canvas screens (empty XML tree, raw custom canvas rendering).
    Performs visual VLM coordinate grounding and steerings.
    """
    if state["status"] != "running":
        return {}

    device = state["device"]
    brain = state["brain"]
    screenshot = state["screenshot"]
    action_history = state.get("action_history", [])
    
    from src.agent.memory import AgentMemory
    temp_mem = AgentMemory()
    temp_mem.set_goal(state["goal"])
    temp_mem.history = action_history

    # VLM Brain decides visual actions (no elements XML, purely image inputs)
    decision = brain.decide_action(screenshot, [], temp_mem, screenshot.size)
    
    analysis = decision.get("analysis", "No gameplay analysis provided.")
    action_type = decision.get("action", "WAIT").upper()
    coordinates = decision.get("coordinates")
    target_label = decision.get("target_label", "Gameplay Target")
    expected_outcome = decision.get("expected_outcome", "")

    automation_logger.info(f"[Gameplay Node] VLM Analysis: {analysis}")
    automation_logger.info(f"[Gameplay Node] Action: {action_type} | Coords: {coordinates}")

    if action_type == "SUCCESS":
        return {"status": "success", "last_action": decision}
    elif action_type == "FAILED":
        return {"status": "failed", "last_action": decision}

    # Execute Tap or Swipes
    success = False
    if action_type == "TAP" and coordinates:
        coords = normalize_coordinates(coordinates, screenshot.size)
        
        # Check if this is a repeated tap on the same coordinates
        is_repeat = False
        if action_history:
            last_hist = action_history[-1]
            last_act = last_hist.get("action", {})
            if last_act.get("action") == "TAP" and last_act.get("coordinates") == coordinates:
                if "static" in last_hist.get("result", "").lower():
                    is_repeat = True
                    
        if is_repeat:
            import random
            offset_x = coords[0] + random.choice([-25, 25])
            offset_y = coords[1] + random.choice([-25, 25])
            w, h = screenshot.size
            offset_x = max(0, min(offset_x, w - 1))
            offset_y = max(0, min(offset_y, h - 1))
            
            automation_logger.warning(f"[Action Recovery] Previous gameplay tap failed. Retrying with offset double-tap at ({offset_x}, {offset_y})")
            device.tap(offset_x, offset_y)
            time.sleep(0.15)
            success = device.tap(offset_x, offset_y)
        else:
            automation_logger.info(f"Executing gameplay TAP at {coords[0]}, {coords[1]}")
            success = device.tap(coords[0], coords[1])
    elif action_type == "SWIPE" and coordinates and len(coordinates) == 4:
        coords = normalize_coordinates(coordinates, screenshot.size)
        success = device.swipe(coords[0], coords[1], coords[2], coords[3])
    elif action_type == "WAIT":
        time.sleep(3.0)
        success = True

    # Gameplay verification
    time.sleep(1.5)
    post_screenshot = device.take_screenshot()
    
    # Resolve active package name
    active_pkg = "com.netflix.NGP.Snakeio" if "snake" in state["goal"].lower() or "snake" in target_label.lower() else state["package"]
    
    verified, msg = ActionVerifier.verify_action(
        before_img=screenshot,
        after_img=post_screenshot,
        action_type=action_type,
        expected_outcome=expected_outcome,
        post_xml="",
        package_name=active_pkg
    )
    automation_logger.info(f"[Gameplay Verification] {msg}")

    new_history = action_history + [{
        "state": f"Gameplay: {action_type} on '{target_label}'",
        "action": decision,
        "result": msg
    }]

    return {
        "action_history": new_history,
        "last_action": decision,
        "last_result": msg
    }

def crash_recovery_node(state: AgentState) -> Dict[str, Any]:
    """
    Relaunches the target application package if a crash occurred or if requested.
    """
    automation_logger.warning(f"[CrashRecovery Node] App crashed or error detected. Relaunching '{state['package']}'...")
    device = state["device"]
    
    # Force kill app
    device.stop_app(state["package"])
    time.sleep(2.0)
    
    # Relaunch app
    device.launch_app(state["package"])
    time.sleep(4.0)  # cold start wait
    
    automation_logger.info("[CrashRecovery Node] Package relaunched. Returning to state collection...")
    
    # We clear the error status and return to running
    return {
        "status": "running",
        "last_result": "App successfully force-stopped and relaunched."
    }
