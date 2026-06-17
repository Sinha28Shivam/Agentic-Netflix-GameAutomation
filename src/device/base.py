from abc import ABC, abstractmethod
from PIL import Image

class BaseDevice(ABC):
    """
    Abstract interface for device interaction and automation.
    Supports screenshots, XML UI Automator dumps, and basic input injections.
    """

    @abstractmethod
    def take_screenshot(self) -> Image.Image:
        """
        Capture the current screen of the device and return it as a PIL Image.
        """
        pass

    @abstractmethod
    def dump_hierarchy(self) -> str:
        """
        Dump the current Android window UI hierarchy as an XML string.
        """
        pass

    @abstractmethod
    def tap(self, x: int, y: int) -> bool:
        """
        Tap on the specified screen coordinates (x, y).
        """
        pass

    @abstractmethod
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        """
        Swipe from (x1, y1) to (x2, y2) over the specified duration.
        """
        pass

    @abstractmethod
    def keyevent(self, key_code: int | str) -> bool:
        """
        Inject a keypress event (e.g. Back button, Home button).
        """
        pass

    @abstractmethod
    def launch_app(self, package_name: str) -> bool:
        """
        Launch the application with the specified package name.
        """
        pass

    @abstractmethod
    def stop_app(self, package_name: str) -> bool:
        """
        Force-stop the application with the specified package name.
        """
        pass
