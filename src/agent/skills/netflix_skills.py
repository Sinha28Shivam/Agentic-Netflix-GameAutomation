import time
import subprocess
from src.device.base import BaseDevice
from src.perception.hierarchy_parser import HierarchyParser
from src.utils.logger import automation_logger

def select_netflix_profile(device: BaseDevice, profile_name: str) -> bool:
    """
    Selects the profile named profile_name on the startup profile selection screen.
    """
    automation_logger.info(f"Executing skill: select_netflix_profile for '{profile_name}'")
    xml_content = device.dump_hierarchy()
    if not xml_content:
        return False
        
    # Search for node matching profile name (case-insensitive contains text or content-desc)
    nodes = HierarchyParser.find_nodes(xml_content, {"text": f"contains:{profile_name}"})
    if not nodes:
        nodes = HierarchyParser.find_nodes(xml_content, {"content-desc": f"contains:{profile_name}"})
        
    if nodes and "center_x" in nodes[0]:
        cx, cy = nodes[0]["center_x"], nodes[0]["center_y"]
        automation_logger.info(f"Profile '{profile_name}' found. Tapping at ({cx}, {cy})")
        return device.tap(cx, cy)
        
    # Fallback to visual coordinates if XML parser doesn't find name (sometimes profile names are image nodes)
    # The coordinate [585, 540] was verified on phone for profile 'Shivam'
    automation_logger.warning(f"Profile '{profile_name}' node not found. Tapping default coordinates [585, 540]")
    return device.tap(585, 540)

def install_game_from_store(device: BaseDevice, package_name: str) -> bool:
    """
    Simulates clicking 'Install' inside Play Store and polling until the app is installed.
    """
    automation_logger.info(f"Executing skill: install_game_from_store for '{package_name}'")
    xml_content = device.dump_hierarchy()
    if not xml_content:
        return False
        
    # 1. Tap Install/Get Game in details page (usually text='Get Game' or 'Install')
    install_btn = HierarchyParser.find_node_by_text(xml_content, "Get Game")
    if not install_btn:
        install_btn = HierarchyParser.find_node_by_text(xml_content, "Install")
        
    if install_btn and "center_x" in install_btn:
        device.tap(install_btn["center_x"], install_btn["center_y"])
        time.sleep(3.0)  # Wait for store redirect
        
    # 2. Inside Play Store, find "Install" button and click it
    store_xml = device.dump_hierarchy()
    play_store_install = HierarchyParser.find_node_by_text(store_xml, "Install")
    if play_store_install and "center_x" in play_store_install:
        device.tap(play_store_install["center_x"], play_store_install["center_y"])
        automation_logger.info("Clicked Install in Google Play Store. Waiting for installation...")
        
        # 3. Poll pm list packages to wait for install completion (timeout 3 mins)
        from src.device.adb_device import ADB_EXE
        timeout = 180
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check package presence
                out = subprocess.check_output([ADB_EXE, "shell", "pm", "path", package_name], text=True)
                if "package:" in out:
                    automation_logger.info(f"Game package '{package_name}' installed successfully!")
                    # Go back to Netflix app
                    device.keyevent(4) # BACK button
                    return True
            except Exception:
                pass
            time.sleep(5.0)
            
        automation_logger.error(f"Installation timeout for package {package_name}")
        return False
        
    automation_logger.warning("Play Store 'Install' button not found. Assuming app may be already installed.")
    return True
