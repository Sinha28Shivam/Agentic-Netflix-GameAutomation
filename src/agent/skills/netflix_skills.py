import time
from src.device.base import BaseDevice
from src.perception.hierarchy_parser import HierarchyParser
from src.perception.cv_engine import CVEngine
from src.utils.logger import automation_logger

def select_netflix_profile(device: BaseDevice, profile_name: str) -> bool:
    """
    Selects the profile named profile_name on the startup profile selection screen.
    """
    automation_logger.info(f"Executing skill: select_netflix_profile for '{profile_name}'")
    xml_content = device.dump_hierarchy()
    if not xml_content:
        return False

    nodes = HierarchyParser.find_nodes(xml_content, {"text": f"contains:{profile_name}"})
    if not nodes:
        nodes = HierarchyParser.find_nodes(xml_content, {"content-desc": f"contains:{profile_name}"})

    if nodes and "center_x" in nodes[0]:
        cx, cy = nodes[0]["center_x"], nodes[0]["center_y"]
        automation_logger.info(f"Profile '{profile_name}' found. Tapping at ({cx}, {cy})")
        return device.tap(cx, cy)

    # Swipe left to reveal more profiles and retry once
    automation_logger.warning(f"Profile '{profile_name}' not found. Swiping left to reveal more profiles.")
    width = getattr(device, "width", 1080)
    height = getattr(device, "height", 2400)
    mid_y = height // 2
    device.swipe(int(width * 0.75), mid_y, int(width * 0.25), mid_y, duration_ms=400)
    time.sleep(1.0)

    xml_content = device.dump_hierarchy()
    nodes = HierarchyParser.find_nodes(xml_content, {"text": f"contains:{profile_name}"})
    if not nodes:
        nodes = HierarchyParser.find_nodes(xml_content, {"content-desc": f"contains:{profile_name}"})

    if nodes and "center_x" in nodes[0]:
        cx, cy = nodes[0]["center_x"], nodes[0]["center_y"]
        automation_logger.info(f"Profile '{profile_name}' found after swipe. Tapping at ({cx}, {cy})")
        return device.tap(cx, cy)

    automation_logger.error(f"Profile '{profile_name}' not found after swipe. Cannot select profile.")
    return False


def install_game_from_store(device: BaseDevice, package_name: str) -> bool:
    """
    Taps 'Get Game' or 'Install' then waits for installation to complete.
    Uses Appium's is_app_installed() when available; falls back to UI polling.
    """
    automation_logger.info(f"Executing skill: install_game_from_store for '{package_name}'")
    xml_content = device.dump_hierarchy()
    if not xml_content:
        return False

    # Tap Get Game / Install in the Netflix game details page
    install_btn = HierarchyParser.find_node_by_text(xml_content, "Get Game")
    if not install_btn:
        install_btn = HierarchyParser.find_node_by_text(xml_content, "Install")

    if install_btn and "center_x" in install_btn:
        device.tap(install_btn["center_x"], install_btn["center_y"])
        time.sleep(3.0)

    # Find the Play Store Install button
    store_xml = device.dump_hierarchy()
    play_store_install = HierarchyParser.find_node_by_text(store_xml, "Install")
    if not play_store_install:
        automation_logger.warning("Play Store 'Install' button not found. Assuming app may already be installed.")
        return True

    device.tap(play_store_install["center_x"], play_store_install["center_y"])
    automation_logger.info("Clicked Install in Google Play Store. Polling for completion...")

    timeout = 180
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Appium path: use is_app_installed
        if hasattr(device, "driver") and hasattr(device.driver, "is_app_installed"):
            try:
                if device.driver.is_app_installed(package_name):
                    automation_logger.info(f"Package '{package_name}' installed successfully (Appium check).")
                    device.keyevent(4)  # Back to Netflix
                    return True
            except Exception:
                pass
        else:
            # Fallback: poll UI for "Open" button in Play Store
            check_xml = device.dump_hierarchy()
            open_btn = HierarchyParser.find_node_by_text(check_xml, "Open")
            if open_btn:
                automation_logger.info("Install complete: 'Open' button visible in Play Store.")
                device.keyevent(4)  # Back to Netflix
                return True

        time.sleep(5.0)

    automation_logger.error(f"Installation timed out after {timeout}s for package '{package_name}'.")
    return False


def place_tower(device: BaseDevice, tower_name: str, target_cell: str, screen_size: tuple) -> bool:
    """
    Places a tower on the visual grid (e.g. Bloons) using CVEngine grid-to-pixel mapping.
    """
    automation_logger.info(f"Executing skill: place_tower '{tower_name}' at grid cell {target_cell}")
    try:
        cx, cy = CVEngine.grid_to_pixels(target_cell, screen_size)
        return device.tap(cx, cy)
    except Exception as e:
        automation_logger.error(f"Failed to place tower at {target_cell}: {e}")
        return False
