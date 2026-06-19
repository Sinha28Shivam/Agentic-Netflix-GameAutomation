import PIL.Image
from src.device.base import BaseDevice

class MockDevice(BaseDevice):
    """
    Mock Android Device simulation for offline testing and verification.
    """

    def __init__(self):
        self.current_state = "login_screen"
        self.last_inputs = []
        self.width = 1080
        self.height = 2400

    def take_screenshot(self) -> PIL.Image.Image:
        """
        Return a basic mock image with a colored background based on state.
        """
        color = "black"
        if self.current_state == "game_lobby":
            color = "white"
        elif self.current_state == "gameplay":
            color = "gray"
        
        # Create a simple image with state text
        img = PIL.Image.new("RGB", (self.width, self.height), color=color)
        
        # Login screen is black — mark it so ActionVerifier skips pixel diff
        # This prevents false "static screen" failures in mock mode
        if self.current_state == "login_screen":
            img.info["drm_blocked"] = True
            
        return img

    def dump_hierarchy(self) -> str:
        """
        Return a mock XML layout tree based on the current state.
        """
        if self.current_state == "login_screen":
            return """<?xml version="1.0" encoding="utf-8"?>
            <hierarchy rotation="0">
                <node index="0" class="android.widget.FrameLayout" resource-id="android:id/content">
                    <node index="0" class="android.widget.TextView" resource-id="com.netflix:id/title" text="Netflix Games" bounds="[100,200][980,400]" />
                    <node index="1" class="android.widget.Button" resource-id="com.netflix:id/btn_login" text="SIGN IN" bounds="[300,1000][780,1150]" />
                </node>
            </hierarchy>
            """
        elif self.current_state == "game_lobby":
            return """<?xml version="1.0" encoding="utf-8"?>
            <hierarchy rotation="0">
                <node index="0" class="android.widget.FrameLayout" resource-id="android:id/content">
                    <node index="0" class="android.widget.TextView" text="Game Library" bounds="[100,100][980,250]" />
                    <node index="1" class="android.widget.Button" resource-id="com.netflix:id/game_card_0" text="Start Game" bounds="[400,1200][680,1350]" />
                </node>
            </hierarchy>
            """
        elif self.current_state == "gameplay":
            # Gameplay canvas shows a blank hierarchy, simulating game engine canvas rendering
            return """<?xml version="1.0" encoding="utf-8"?>
            <hierarchy rotation="0">
                <node index="0" class="android.view.SurfaceView" resource-id="com.netflix:id/game_surface" bounds="[0,0][1080,2400]" />
            </hierarchy>
            """
        return "<hierarchy />"

    def tap(self, x: int, y: int) -> bool:
        print(f"[MockDevice] Tap registered at ({x}, {y}) while in state '{self.current_state}'")
        self.last_inputs.append(("tap", x, y))

        # Simulate state transitions based on where was clicked
        if self.current_state == "login_screen":
            # SIGN IN Button bounds: [300,1000][780,1150] (Center is 540, 1075)
            if 300 <= x <= 780 and 1000 <= y <= 1150:
                print("[MockDevice] Clicked SIGN IN button. Transitioning to 'game_lobby'")
                self.current_state = "game_lobby"
        elif self.current_state == "game_lobby":
            # Start Game button bounds: [400,1200][680,1350] (Center is 540, 1275)
            if 400 <= x <= 680 and 1200 <= y <= 1350:
                print("[MockDevice] Clicked Start Game button. Transitioning to 'gameplay'")
                self.current_state = "gameplay"
        
        return True

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        print(f"[MockDevice] Swipe from ({x1}, {y1}) to ({x2}, {y2}) over {duration_ms}ms")
        self.last_inputs.append(("swipe", x1, y1, x2, y2, duration_ms))
        return True

    def keyevent(self, key_code: int | str) -> bool:
        print(f"[MockDevice] Keyevent: {key_code}")
        self.last_inputs.append(("keyevent", key_code))
        if key_code == 4 or key_code == "KEYCODE_BACK":  # Back key
            if self.current_state == "gameplay":
                self.current_state = "game_lobby"
            elif self.current_state == "game_lobby":
                self.current_state = "login_screen"
        return True

    def launch_app(self, package_name: str) -> bool:
        print(f"[MockDevice] Launch app: {package_name}")
        self.current_state = "login_screen"
        return True

    def stop_app(self, package_name: str) -> bool:
        print(f"[MockDevice] Stop app: {package_name}")
        return True

    def input_text(self, text: str) -> bool:
        print(f"[MockDevice] input_text: '{text}'")
        self.last_inputs.append(("input_text", text))
        return True
