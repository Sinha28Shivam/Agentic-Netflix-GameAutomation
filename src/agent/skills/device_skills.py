import time
import subprocess
from src.device.base import BaseDevice
from src.device.adb_device import ADB_EXE
from src.utils.logger import automation_logger

def toggle_network_connection(device: BaseDevice, enabled: bool) -> bool:
    """
    Turns Wi-Fi and Mobile Data ON or OFF via ADB commands.
    """
    state_str = "enable" if enabled else "disable"
    automation_logger.info(f"Executing skill: toggle_network_connection -> {state_str.upper()}")
    
    try:
        # Toggle WiFi
        subprocess.run([ADB_EXE, "shell", "svc", "wifi", state_str], check=True)
        # Toggle Data
        subprocess.run([ADB_EXE, "shell", "svc", "data", state_str], check=True)
        
        # Additional help command to ensure airplane mode status if needed
        time.sleep(2.0) # Wait for network state to update
        return True
    except Exception as e:
        automation_logger.error(f"Failed to toggle network connection: {e}")
        return False

def rotate_device_orientation(device: BaseDevice, mode: str) -> bool:
    """
    Rotates the device screen to landscape (1) or portrait (0).
    """
    automation_logger.info(f"Executing skill: rotate_device_orientation -> {mode.upper()}")
    try:
        # Disable auto-rotate first (user_rotation is locked)
        subprocess.run([ADB_EXE, "shell", "content", "insert", "--uri", "content://settings/system", "--bind", "name:s:accelerometer_rotation", "--bind", "value:i:0"], check=True)
        
        # Set rotation angle
        rotation_val = "1" if mode == "landscape" else "0"
        subprocess.run([ADB_EXE, "shell", "content", "insert", "--uri", "content://settings/system", "--bind", "name:s:user_rotation", "--bind", "value:i:" + rotation_val], check=True)
        
        time.sleep(1.5)
        return True
    except Exception as e:
        automation_logger.error(f"Failed to rotate device screen: {e}")
        return False

def adjust_device_volume(device: BaseDevice, level: str) -> bool:
    """
    Mutes, unmutes, or changes device volume.
    levels: 'mute', 'unmute', 'up', 'down'
    """
    automation_logger.info(f"Executing skill: adjust_device_volume -> {level.upper()}")
    try:
        if level == "mute":
            # KEYCODE_VOLUME_MUTE = 164
            device.keyevent(164)
        elif level == "up":
            # KEYCODE_VOLUME_UP = 24
            device.keyevent(24)
        elif level == "down":
            # KEYCODE_VOLUME_DOWN = 25
            device.keyevent(25)
        elif level == "unmute":
            # Send volume up once to unmute state
            device.keyevent(24)
        return True
    except Exception as e:
        automation_logger.error(f"Failed to adjust device volume: {e}")
        return False
