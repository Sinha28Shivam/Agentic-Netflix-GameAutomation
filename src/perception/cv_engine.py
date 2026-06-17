import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional

class CVEngine:
    """
    Performs Computer Vision helper operations including template matching and screen difference detection.
    """

    @staticmethod
    def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
        """
        Convert a PIL Image to OpenCV BGR format.
        """
        # Convert RGB to BGR
        open_cv_image = np.array(pil_img)
        if len(open_cv_image.shape) == 3:
            return cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
        return open_cv_image

    @classmethod
    def compute_pixel_diff(cls, img1: Image.Image, img2: Image.Image) -> float:
        """
        Calculate the percentage of pixels that changed between two screenshots.
        Helps check if the screen is static (e.g. frozen or ignored tap) or transitioning.
        """
        if img1.size != img2.size:
            # Different sizes mean a change or rotation
            return 100.0

        cv_img1 = cls.pil_to_cv2(img1)
        cv_img2 = cls.pil_to_cv2(img2)

        # Convert to grayscale
        gray1 = cv2.cvtColor(cv_img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(cv_img2, cv2.COLOR_BGR2GRAY)

        # Compute absolute difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Apply threshold to focus on significant changes
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        # Calculate percentage of changed pixels
        non_zero_count = np.count_nonzero(thresh)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        
        change_pct = (non_zero_count / total_pixels) * 100.0
        return change_pct

    @classmethod
    def locate_template(
        cls, scene_img: Image.Image, template_path: str, threshold: float = 0.8
    ) -> Optional[Tuple[int, int]]:
        """
        Locate template image within the scene image.
        Returns the center coordinates (x, y) if match confidence is above threshold, otherwise None.
        """
        cv_scene = cls.pil_to_cv2(scene_img)
        # Read template image in color/gray
        cv_template = cv2.imread(template_path)
        if cv_template is None:
            print(f"[CVEngine] Warning: Template file not found at {template_path}")
            return None

        h, w = cv_template.shape[:2]
        
        # Perform matching
        res = cv2.matchTemplate(cv_scene, cv_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            # Calculate center of the matching box
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            print(f"[CVEngine] Template found at ({center_x}, {center_y}) with match confidence {max_val:.2f}")
            return center_x, center_y
        
        print(f"[CVEngine] Template matching failed. Best confidence: {max_val:.2f} (required: {threshold})")
        return None
