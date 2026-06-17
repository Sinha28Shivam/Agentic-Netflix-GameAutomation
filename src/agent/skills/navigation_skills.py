import time
from src.device.base import BaseDevice
from src.perception.hierarchy_parser import HierarchyParser
from src.utils.logger import automation_logger

def open_games_tab(device: BaseDevice) -> bool:
    """
    Finds and taps the Netflix 'Games' navigation tab.
    """
    automation_logger.info("Executing skill: open_games_tab")
    xml_content = device.dump_hierarchy()
    if not xml_content:
        automation_logger.error("Failed to dump hierarchy XML.")
        return False
        
    # Search for Games tab nodes
    # Typically com.netflix.mediaclient:id/games_tab or text='Games'
    node = HierarchyParser.find_node_by_id(xml_content, "com.netflix.mediaclient:id/games_tab")
    if not node:
        node = HierarchyParser.find_node_by_text(xml_content, "Games")
        
    if node and "center_x" in node:
        cx, cy = node["center_x"], node["center_y"]
        automation_logger.info(f"Games tab node found. Tapping at ({cx}, {cy})")
        return device.tap(cx, cy)
        
    # Standard fallback swipe/coordinates on common screens if XML node is missing
    automation_logger.warning("Games tab node not found in XML. Tapping default coordinates [540, 2200]")
    return device.tap(540, 2200)

def search_game_by_name(device: BaseDevice, game_name: str) -> bool:
    """
    Clicks Netflix search bar, enters game name, and submits search.
    """
    automation_logger.info(f"Executing skill: search_game_by_name for '{game_name}'")
    xml_content = device.dump_hierarchy()
    if not xml_content:
        return False

    # Find search icon button
    search_node = HierarchyParser.find_node_by_id(xml_content, "com.netflix.mediaclient:id/search_button")
    if not search_node:
        search_node = HierarchyParser.find_node_by_text(xml_content, "Search")

    if search_node and "center_x" in search_node:
        device.tap(search_node["center_x"], search_node["center_y"])
        time.sleep(1.5)
    else:
        # Fallback click search icon area
        device.tap(950, 150)
        time.sleep(1.5)

    # Input text using ADB shell input text (standard command supported by ADBDevice)
    # We must escape spaces or use direct typing command
    escaped_name = game_name.replace(" ", "%s")
    # Execute text typing via ADB shell command
    # Because typing is an OS utility, we can execute via device or shell directly.
    # To keep it encapsulated, we run adb command via subprocess inside ADBDevice or a shell command.
    # We can add an input_text method to ADBDevice or run it via keyevents.
    # Let's run raw adb shell command directly:
    if hasattr(device, "_run_cmd"):
        device._run_cmd(["shell", "input", "text", escaped_name])
        time.sleep(1.5)
        # Click enter
        device.keyevent(66) # 66 = KEYCODE_ENTER
        return True
    
    automation_logger.warning("Device connector does not support direct ADB typing command.")
    return False

def scroll_catalog(device: BaseDevice, direction: str = "down", scrolls: int = 1) -> bool:
    """
    Steers scroll swipe up or down.
    """
    automation_logger.info(f"Executing skill: scroll_catalog {direction} x{scrolls}")
    for _ in range(scrolls):
        if direction == "down":
            device.swipe(540, 1600, 540, 600, duration_ms=500)
        else:
            device.swipe(540, 600, 540, 1600, duration_ms=500)
        time.sleep(1.0)
    return True
