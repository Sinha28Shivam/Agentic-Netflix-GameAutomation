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

    node = HierarchyParser.find_node_by_id(xml_content, "com.netflix.mediaclient:id/games_tab")
    if not node:
        node = HierarchyParser.find_node_by_text(xml_content, "Games")
    if not node:
        nodes = HierarchyParser.find_nodes(xml_content, {"content-desc": "contains:Games"})
        node = nodes[0] if nodes else None

    if node and "center_x" in node:
        cx, cy = node["center_x"], node["center_y"]
        automation_logger.info(f"Games tab node found. Tapping at ({cx}, {cy})")
        return device.tap(cx, cy)

    automation_logger.warning("Games tab node not found in XML. Cannot tap without coordinates.")
    return False


def search_game_by_name(device: BaseDevice, game_name: str) -> bool:
    """
    Clicks the Netflix search bar, enters the game name, and submits.
    Uses device.input_text() for cross-device compatibility (Appium + ADB).
    """
    automation_logger.info(f"Executing skill: search_game_by_name for '{game_name}'")
    xml_content = device.dump_hierarchy()
    if not xml_content:
        return False

    # Find the search entry point — try multiple selectors
    search_node = HierarchyParser.find_node_by_id(xml_content, "com.netflix.mediaclient:id/search_button")
    if not search_node:
        search_node = HierarchyParser.find_node_by_text(xml_content, "Search")
    if not search_node:
        nodes = HierarchyParser.find_nodes(xml_content, {"content-desc": "contains:earch"})
        search_node = nodes[0] if nodes else None

    if search_node and "center_x" in search_node:
        device.tap(search_node["center_x"], search_node["center_y"])
        time.sleep(1.5)
    else:
        automation_logger.warning("Search button not found in XML. Skipping search icon tap.")

    # Type the game name via the device-agnostic interface
    if device.input_text(game_name):
        time.sleep(1.5)
        device.keyevent(66)  # KEYCODE_ENTER
        return True

    automation_logger.warning(f"input_text failed for '{game_name}'.")
    return False


def scroll_catalog(device: BaseDevice, direction: str = "down", scrolls: int = 1) -> bool:
    """
    Scrolls the Netflix catalog up or down using screen-relative coordinates.
    """
    automation_logger.info(f"Executing skill: scroll_catalog {direction} x{scrolls}")
    width = getattr(device, "width", 1080)
    height = getattr(device, "height", 2400)

    mid_x = width // 2
    start_y = int(height * 0.65)
    end_y = int(height * 0.25)

    for _ in range(scrolls):
        if direction == "down":
            device.swipe(mid_x, start_y, mid_x, end_y, duration_ms=500)
        else:
            device.swipe(mid_x, end_y, mid_x, start_y, duration_ms=500)
        time.sleep(1.0)
    return True
