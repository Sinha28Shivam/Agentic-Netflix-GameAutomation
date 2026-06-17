import threading
import time
import subprocess
import os
import re
from src.utils.logger import telemetry_logger

class TelemetryDaemon(threading.Thread):
    """
    Background daemon thread that runs continuously to monitor battery drainage, 
    heat levels, refresh rate, and OS alert dialogs in parallel.
    """

    def __init__(self, adb_exe: str, device_serial: str, interval: float = 3.0):
        super().__init__(daemon=True)
        self.adb_exe = adb_exe
        self.device_serial = device_serial
        self.interval = interval
        self.running = False
        self.adb_prefix = [self.adb_exe]
        if self.device_serial:
            self.adb_prefix = [self.adb_exe, "-s", self.device_serial]
            
        telemetry_logger.info(f"[TelemetryDaemon] Initialized for device: {self.device_serial or 'default'}")

    def _run_cmd(self, cmd_args: list[str]) -> str:
        try:
            full_cmd = self.adb_prefix + cmd_args
            res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=5.0)
            return res.stdout
        except Exception:
            return ""

    def get_battery_and_temp(self) -> tuple[int, float]:
        """
        Parses adb shell dumpsys battery.
        Returns (battery_level_percent, temperature_celsius).
        """
        output = self._run_cmd(["shell", "dumpsys", "battery"])
        level = 100
        temp = 0.0
        
        # Parse level
        level_match = re.search(r"level:\s*(\d+)", output)
        if level_match:
            level = int(level_match.group(1))
            
        # Parse temp (battery temperature is returned in tenths of a degree Celsius)
        temp_match = re.search(r"temperature:\s*(\d+)", output)
        if temp_match:
            temp = float(temp_match.group(1)) / 10.0
            
        return level, temp

    def get_refresh_rate(self) -> float:
        """
        Retrieves active screen refresh rate.
        """
        output = self._run_cmd(["shell", "dumpsys", "display"])
        
        # Look for refresh rate entries
        # e.g., mDisplayInfos=..., refreshRate 120.0, or fps=60
        rate_match = re.search(r"refreshRate\s*([\d\.]+)", output)
        if rate_match:
            return float(rate_match.group(1))
            
        rate_match_alt = re.search(r"fps=([\d\.]+)", output)
        if rate_match_alt:
            return float(rate_match_alt.group(1))
            
        return 60.0  # default fallback

    def check_for_system_dialogs(self) -> bool:
        """
        Inspects window state to detect active system crash/alert dialogs.
        """
        output = self._run_cmd(["shell", "dumpsys", "window", "windows"])
        
        # Search for the currently focused window
        focus_match = re.search(r"mCurrentFocus=Window\{[^\}]*\}", output)
        if focus_match:
            focus_str = focus_match.group(0).lower()
            # If the focused window belongs to system alert/crash/ANR dialogs
            if ("alert" in focus_str or "crash" in focus_str or 
                "anr" in focus_str or "dialog" in focus_str or "has_stopped" in focus_str) and "systemui" not in focus_str:
                return True
                
        return False

    def run(self):
        self.running = True
        telemetry_logger.info("[TelemetryDaemon] Background telemetry daemon started.")
        
        while self.running:
            try:
                # 1. Collect metrics
                battery_level, temp = self.get_battery_and_temp()
                refresh_rate = self.get_refresh_rate()
                has_system_dialog = self.check_for_system_dialogs()
                
                # 2. Log metrics to logs/telemetry.log
                status_msg = (
                    f"DEVICE_STATS - Battery: {battery_level}% | "
                    f"Temp: {temp}°C | "
                    f"Refresh Rate: {refresh_rate}Hz | "
                    f"OS Crash Alert Visible: {has_system_dialog}"
                )
                
                # Alert triggers for critical states
                if temp > 45.0:
                    telemetry_logger.warning(f"CRITICAL HEAT ALERT - Device temperature is high: {temp}°C!")
                if battery_level < 15:
                    telemetry_logger.warning(f"LOW BATTERY ALERT - Battery level: {battery_level}%")
                if has_system_dialog:
                    telemetry_logger.error("SYSTEM WARNING - A crash or system dialog window is detected on screen.")
                    
                telemetry_logger.info(status_msg)
                
            except Exception as e:
                telemetry_logger.error(f"[TelemetryDaemon] Loop encountered exception: {e}")
                
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        telemetry_logger.info("[TelemetryDaemon] Background telemetry daemon stopped.")
