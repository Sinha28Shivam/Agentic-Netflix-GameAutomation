import io
from PIL import Image
from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

from src.device.base import BaseDevice
from src.utils.logger import automation_logger

class AppiumDevice(BaseDevice):
    """
    Cross-device automation controller using the Appium Python Client.
    Supports Android (UiAutomator2) and iOS (XCUITest) drivers.
    """

    def __init__(self, server_url: str = "http://127.0.0.1:4723", capabilities: dict = None):
        self.server_url = server_url
        self.capabilities = capabilities or {}
        
        # Load capabilities into Appium Options
        options = AppiumOptions().load_capabilities(self.capabilities)
        
        automation_logger.info(f"[AppiumDevice] Connecting to Appium Server at {self.server_url}...")
        try:
            self.driver = webdriver.Remote(self.server_url, options=options)
            self.platform_name = self.capabilities.get("platformName", "android").lower()
            size = self.driver.get_window_size()
            self.width = size.get("width", 1080)
            self.height = size.get("height", 2400)
            automation_logger.info(f"[AppiumDevice] Successfully connected! Platform: {self.platform_name.upper()} Screen: {self.width}x{self.height}")
        except Exception as e:
            automation_logger.error(f"[AppiumDevice] Connection failed: {e}")
            raise e

    def take_screenshot(self) -> Image.Image:
        """
        Capture screenshot via Appium driver.
        """
        try:
            png_data = self.driver.get_screenshot_as_png()
            img = Image.open(io.BytesIO(png_data))
            
            # Check for black frame DRM detection (re-use same logic)
            if self._is_black_frame(img):
                automation_logger.warning("[AppiumDevice] Screenshot is black. Possible DRM active.")
                img.info["drm_blocked"] = True
            
            return img
        except Exception as e:
            automation_logger.error(f"[AppiumDevice] Failed to take screenshot: {e}")
            img = Image.new("RGB", (1080, 2400), color="black")
            img.info["drm_blocked"] = True
            return img

    def _is_black_frame(self, img: Image.Image, threshold: float = 0.99) -> bool:
        try:
            import numpy as np
            arr = np.array(img.convert("RGB"))
            black_pixels = np.sum(np.all(arr < 10, axis=2))
            total_pixels = arr.shape[0] * arr.shape[1]
            return (black_pixels / total_pixels) >= threshold
        except Exception:
            return False

    def dump_hierarchy(self) -> str:
        """
        Returns XML page source.
        """
        try:
            return self.driver.page_source
        except Exception as e:
            automation_logger.error(f"[AppiumDevice] Failed to dump page source: {e}")
            return ""

    def tap(self, x: int, y: int) -> bool:
        """
        W3C compliant tap using ActionChains pointer input.
        """
        try:
            automation_logger.info(f"[AppiumDevice] Executing tap at ({x}, {y})")
            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(x, y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
            return True
        except Exception as e:
            automation_logger.error(f"[AppiumDevice] Tap failed at ({x}, {y}): {e}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        """
        W3C compliant swipe using ActionChains pointer input.
        """
        try:
            automation_logger.info(f"[AppiumDevice] Executing swipe from ({x1}, {y1}) to ({x2}, {y2}) over {duration_ms}ms")
            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(x1, y1)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(duration_ms / 1000.0)
            actions.w3c_actions.pointer_action.move_to_location(x2, y2)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
            return True
        except Exception as e:
            automation_logger.error(f"[AppiumDevice] Swipe failed: {e}")
            return False

    def keyevent(self, key_code: int | str) -> bool:
        """
        Send physical keycode (Android) or handle back actions.
        """
        try:
            if self.platform_name == "android":
                automation_logger.info(f"[AppiumDevice] Sending key event: {key_code}")
                # Appium AndroidDriver exposes press_keycode
                if hasattr(self.driver, "press_keycode"):
                    self.driver.press_keycode(int(key_code))
                else:
                    self.driver.keyevent(int(key_code))
                return True
            else:
                # iOS fallback keyevent (e.g. back gesture or button)
                automation_logger.warning(f"[AppiumDevice] Key event '{key_code}' ignored on iOS. Using native back where possible.")
                return False
        except Exception as e:
            automation_logger.error(f"[AppiumDevice] Key event failed: {e}")
            return False

    def launch_app(self, package_name: str) -> bool:
        """
        Launch target app bundle/package.
        """
        try:
            automation_logger.info(f"[AppiumDevice] Launching app: {package_name}")
            self.driver.activate_app(package_name)
            return True
        except Exception as e:
            automation_logger.error(f"[AppiumDevice] Failed to launch app: {e}")
            return False

    def stop_app(self, package_name: str) -> bool:
        """
        Stop/terminate target app bundle/package.
        """
        try:
            automation_logger.info(f"[AppiumDevice] Terminating app: {package_name}")
            self.driver.terminate_app(package_name)
            return True
        except Exception as e:
            automation_logger.error(f"[AppiumDevice] Failed to stop app: {e}")
            return False

    def input_text(self, text: str) -> bool:
        """
        Type text into the currently focused input field.
        Uses mobile: type for Android (UiAutomator2) and mobile: typeText for iOS (XCUITest).
        """
        try:
            automation_logger.info(f"[AppiumDevice] Typing text: '{text}'")
            if self.platform_name == "ios":
                self.driver.execute_script("mobile: typeText", {"text": text})
            else:
                self.driver.execute_script("mobile: type", {"text": text})
            return True
        except Exception as e:
            automation_logger.error(f"[AppiumDevice] input_text failed: {e}")
            # Fallback: send_keys on the active element
            try:
                self.driver.switch_to.active_element.send_keys(text)
                return True
            except Exception:
                return False
