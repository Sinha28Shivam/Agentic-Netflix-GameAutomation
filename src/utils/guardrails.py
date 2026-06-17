from PIL import Image
from src.device.base import BaseDevice
from src.perception.hierarchy_parser import HierarchyParser
from src.perception.cv_engine import CVEngine

class SystemGuard:
    """
    Monitors device state and handles intrusive system interruptions, crashes, and OS popups.
    """

    def __init__(self, device: BaseDevice):
        self.device = device
        # Common Android OS crash/warning button texts and resource IDs
        self.system_dialog_keywords = [
            "close app", "close", "ok", "wait", "keep waiting", "dismiss"
        ]

    def dismiss_system_dialogs(self) -> bool:
        """
        Scan XML dump for system dialogs / app crash popups and auto-dismiss them.
        Only targets elements belonging to Android system packages to prevent false triggers.
        Returns True if a dialog was detected and clicked, False otherwise.
        """
        xml_content = self.device.dump_hierarchy()
        if not xml_content:
            return False

        # Check elements against keywords
        actionable_elements = HierarchyParser.get_actionable_elements(xml_content)
        for el in actionable_elements:
            package = el.get("package", "").lower()
            # Restrict alerts to Android OS packages, system UI, and Google Play Services
            if package not in ["android", "com.android.systemui", "com.google.android.gms"]:
                continue
                
            text = el.get("text", "").lower().strip()
            desc = el.get("content-desc", "").lower().strip()
            res_id = el.get("resource-id", "").lower().strip()

            # If element matches any dismiss keyword and has center coordinates
            for keyword in self.system_dialog_keywords:
                if (keyword == text or keyword in desc or keyword in res_id) and "center_x" in el:
                    print(f"[SystemGuard] Auto-dismissing system alert: Clicked '{el.get('text')}' at ({el['center_x']}, {el['center_y']})")
                    self.device.tap(el["center_x"], el["center_y"])
                    return True

        return False


class ActionVerifier:
    """
    Verifies the success of execution steps to eliminate false positives and phantom clicks.
    """

    @staticmethod
    def verify_action(
        before_img: Image.Image,
        after_img: Image.Image,
        action_type: str,
        expected_outcome: str,
        post_xml: str,
        package_name: str = ""
    ) -> tuple[bool, str]:
        """
        Check if the action had a visual or state effect.
        """
        if action_type in ["TAP", "SWIPE"]:
            # Check for static screen (Phantom Clicks)
            change_pct = CVEngine.compute_pixel_diff(before_img, after_img)
            print(f"[ActionVerifier] Screen changed by {change_pct:.2f}% after {action_type}.")

            # Set threshold based on package (games have high idle animations like breathing/particles)
            threshold = 0.3
            is_game = package_name and "mediaclient" not in package_name.lower()
            if is_game:
                threshold = 6.0
                
            # If pixel change is extremely low, the tap was likely ignored by the OS/canvas
            if change_pct < threshold:
                return False, f"Screen remained static (change: {change_pct:.2f}% under threshold of {threshold}%). Action failed to register. Please try a different coordinate or verify if blocked."

        # If we have an expected text outcome and XML hierarchy, check for presence
        if expected_outcome and post_xml:
            clean_expected = expected_outcome.lower().strip()
            keywords = [w for w in clean_expected.split() if len(w) > 4]
            found_keywords = [w for w in keywords if w in post_xml.lower()]
            
            if keywords and len(found_keywords) == 0:
                print(f"[ActionVerifier] Warning: Expected terms '{keywords}' not found in new UI hierarchy.")

        return True, "Action registered successfully."
