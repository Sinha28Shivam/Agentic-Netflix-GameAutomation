import time
from src.device.base import BaseDevice
from src.utils.logger import automation_logger

def toggle_network_connection(device: BaseDevice, enabled: bool) -> bool:
    """
    Enables or disables WiFi and Mobile Data.
    Uses Appium network connection API (connection type 6 = WiFi+Data, 0 = none/airplane).
    """
    state_str = "ON" if enabled else "OFF"
    automation_logger.info(f"Executing skill: toggle_network_connection -> {state_str}")
    try:
        if hasattr(device, "driver"):
            connection_type = 6 if enabled else 0
            device.driver.set_network_connection(connection_type)
        else:
            automation_logger.warning("toggle_network_connection: device type does not support network toggle.")
            return False
        time.sleep(2.0)
        return True
    except Exception as e:
        automation_logger.error(f"Failed to toggle network connection: {e}")
        return False


def rotate_device_orientation(device: BaseDevice, mode: str) -> bool:
    """
    Rotates the device to 'landscape' or 'portrait' via Appium driver orientation property.
    """
    automation_logger.info(f"Executing skill: rotate_device_orientation -> {mode.upper()}")
    try:
        if hasattr(device, "driver"):
            device.driver.orientation = "LANDSCAPE" if mode == "landscape" else "PORTRAIT"
        else:
            automation_logger.warning("rotate_device_orientation: device type does not support orientation change.")
            return False
        time.sleep(1.5)
        return True
    except Exception as e:
        automation_logger.error(f"Failed to rotate device screen: {e}")
        return False


def adjust_device_volume(device: BaseDevice, level: str) -> bool:
    """
    Adjusts device volume via standard keycodes.
    levels: 'mute' (164), 'unmute' (24), 'up' (24), 'down' (25)
    """
    automation_logger.info(f"Executing skill: adjust_device_volume -> {level.upper()}")
    keycode_map = {"mute": 164, "unmute": 24, "up": 24, "down": 25}
    key_code = keycode_map.get(level)
    if key_code is None:
        automation_logger.warning(f"Unknown volume level: '{level}'. Use mute/unmute/up/down.")
        return False
    try:
        device.keyevent(key_code)
        return True
    except Exception as e:
        automation_logger.error(f"Failed to adjust device volume: {e}")
        return False
