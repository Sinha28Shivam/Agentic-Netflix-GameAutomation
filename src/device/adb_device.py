import subprocess
import io
import re
import time
import os
import numpy as np
from PIL import Image
from src.device.base import BaseDevice
from src.utils.logger import automation_logger

# Auto-resolve common platform-tools paths on Windows to avoid manual PATH configuration
ADB_EXE = "adb"
if os.name == 'nt':
    common_adb_paths = [
        r"C:\Program Files (x86)\platform-tools",
        r"C:\Program Files\platform-tools",
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Android\Sdk\platform-tools")
    ]
    for p in common_adb_paths:
        full_path = os.path.join(p, "adb.exe")
        if os.path.isdir(p) and os.path.exists(full_path):
            ADB_EXE = full_path
            if p not in os.environ["PATH"]:
                os.environ["PATH"] = p + os.pathsep + os.environ["PATH"]
            print(f"[ADBDevice] Found and using ADB executable at: {ADB_EXE}")
            break

class ADBDevice(BaseDevice):
    """
    Physical Android Device automation using ADB subprocess commands.
    """

    def __init__(self, device_serial: str = None):
        self.device_serial = device_serial
        # If no serial provided, auto-detect the first connected device
        if not self.device_serial:
            self.device_serial = self._detect_device()
        
        self.adb_prefix = [ADB_EXE]
        if self.device_serial:
            self.adb_prefix = [ADB_EXE, "-s", self.device_serial]
            print(f"[ADBDevice] Initialized with serial: {self.device_serial}")
        else:
            print("[ADBDevice] Warning: No specific device detected. Defaulting to single adb device.")

    def _detect_device(self) -> str | None:
        try:
            output = subprocess.check_output([ADB_EXE, "devices"], text=True)
            lines = output.strip().split("\n")[1:]
            devices = [line.split("\t")[0] for line in lines if line.strip() and "device" in line]
            if devices:
                return devices[0]
        except Exception as e:
            print(f"[ADBDevice] Error listing adb devices: {e}")
        return None

    def _run_cmd(self, cmd_args: list[str], timeout: float = 10.0) -> subprocess.CompletedProcess:
        full_cmd = self.adb_prefix + cmd_args
        return subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)

    def _is_black_frame(self, img: Image.Image, threshold: float = 0.99) -> bool:
        """
        Returns True if 99%+ of the image pixels are black.
        Indicates either a DRM block or a screencap failure.
        """
        arr = np.array(img.convert("RGB"))
        black_pixels = np.sum(np.all(arr < 10, axis=2))
        total_pixels = arr.shape[0] * arr.shape[1]
        return (black_pixels / total_pixels) >= threshold

    def take_screenshot(self) -> Image.Image:
        """
        Capture screenshot via raw pipe (adb exec-out screencap -p) for maximum speed.
        Detects DRM-blocked screens (fully black) and sets info metadata.
        """
        full_cmd = self.adb_prefix + ["exec-out", "screencap", "-p"]
        try:
            # We must use capture_output=True but not text=True as screenshots are binary
            res = subprocess.run(full_cmd, capture_output=True, timeout=15.0)
            if res.returncode != 0:
                raise RuntimeError(f"ADB screencap failed: {res.stderr}")
            
            img = Image.open(io.BytesIO(res.stdout))
            
            if self._is_black_frame(img):
                automation_logger.warning(
                    "[ADBDevice] Screenshot is black. "
                    "Possible causes: (1) FLAG_SECURE/DRM active, "
                    "(2) screencap pipe failure. "
                    "Returning DRM_BLOCKED signal."
                )
                img.info["drm_blocked"] = True
            
            return img
        except Exception as e:
            automation_logger.error(f"[ADBDevice] Failed to take screenshot: {e}")
            # Fallback mock or empty image if it fails
            img = Image.new("RGB", (1080, 2400), color="black")
            img.info["drm_blocked"] = True
            return img

    def dump_hierarchy(self) -> str:
        """
        Dump Android XML UI hierarchy to SD card and read it back.
        This method is compatible with almost all Android versions.
        """
        # 1. Trigger the dump
        dump_res = self._run_cmd(["shell", "uiautomator", "dump", "/sdcard/window_dump.xml"])
        if dump_res.returncode != 0:
            print(f"[ADBDevice] Warning: uiautomator dump returned error: {dump_res.stderr}")
            # Try dumping to stdout directly as a fallback if supported
            direct_res = self._run_cmd(["shell", "uiautomator", "dump", "/dev/tty"])
            if direct_res.returncode == 0 and "<hierarchy" in direct_res.stdout:
                return direct_res.stdout
            return ""

        # 2. Cat the XML dump file
        cat_res = self._run_cmd(["shell", "cat", "/sdcard/window_dump.xml"])
        if cat_res.returncode != 0 or not cat_res.stdout.strip():
            automation_logger.error(f"[ADBDevice] Failed to read window_dump.xml: {cat_res.stderr.strip()}")
            return ""
        xml_content = cat_res.stdout

        # 3. Clean up in background
        self._run_cmd(["shell", "rm", "/sdcard/window_dump.xml"])

        return xml_content

    def tap(self, x: int, y: int) -> bool:
        """
        Inject tap coordinates via standard input tap.
        """
        res = self._run_cmd(["shell", "input", "tap", str(x), str(y)])
        return res.returncode == 0

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        """
        Inject swipe event.
        """
        res = self._run_cmd(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])
        return res.returncode == 0

    def keyevent(self, key_code: int | str) -> bool:
        """
        Inject Android key event.
        """
        res = self._run_cmd(["shell", "input", "keyevent", str(key_code)])
        return res.returncode == 0

    def launch_app(self, package_name: str) -> bool:
        """
        Launch app using the Android Monkey tool (which triggers default launcher intent).
        """
        res = self._run_cmd(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
        # Monkey returns 0 on successful launch trigger
        return res.returncode == 0

    def stop_app(self, package_name: str) -> bool:
        """
        Force stop app.
        """
        res = self._run_cmd(["shell", "am", "force-stop", package_name])
        return res.returncode == 0

    def input_text(self, text: str) -> bool:
        """
        Type text into the currently focused input field via ADB.
        Subprocess passes the text as a single argument so spaces are handled correctly.
        """
        res = self._run_cmd(["shell", "input", "text", text])
        return res.returncode == 0
