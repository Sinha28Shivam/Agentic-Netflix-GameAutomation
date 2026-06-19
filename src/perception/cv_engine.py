import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, Dict

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

    @classmethod
    def draw_spatial_grid(cls, img: Image.Image, rows: int = 10, cols: int = 10) -> Image.Image:
        """
        Draws a Set-of-Mark style alphanumeric grid (e.g., A1, B2) over the image.
        This provides spatial grounding for Vision Language Models.
        """
        # Create a transparent overlay
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        width, height = img.size
        cell_w = width / cols
        cell_h = height / rows

        # Draw grid lines
        line_color = (255, 0, 0, 128)  # Semi-transparent red
        for i in range(1, cols):
            x = int(i * cell_w)
            draw.line([(x, 0), (x, height)], fill=line_color, width=2)
            
        for i in range(1, rows):
            y = int(i * cell_h)
            draw.line([(0, y), (width, y)], fill=line_color, width=2)

        # Draw labels (A1, A2, B1...)
        # Try loading a basic font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", size=max(12, int(min(cell_w, cell_h) * 0.3)))
        except IOError:
            font = ImageFont.load_default()

        # Columns A-Z, Rows 1-N
        col_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        for r in range(rows):
            for c in range(cols):
                if c < len(col_chars):
                    label = f"{col_chars[c]}{r+1}"
                    # Calculate center of cell
                    cx = (c * cell_w) + (cell_w / 2)
                    cy = (r * cell_h) + (cell_h / 2)
                    
                    # Draw text with a subtle background box for readability
                    text_bbox = draw.textbbox((0, 0), label, font=font)
                    tw = text_bbox[2] - text_bbox[0]
                    th = text_bbox[3] - text_bbox[1]
                    
                    tx = cx - (tw / 2)
                    ty = cy - (th / 2)
                    
                    draw.rectangle([tx - 2, ty - 2, tx + tw + 2, ty + th + 2], fill=(0, 0, 0, 180))
                    draw.text((tx, ty), label, fill=(255, 255, 255, 255), font=font)

        # Alpha composite the overlay onto the original image
        img_rgba = img.convert('RGBA')
        out_img = Image.alpha_composite(img_rgba, overlay)
        return out_img.convert('RGB')

    @classmethod
    def grid_to_pixels(cls, cell: str, screen_size: Tuple[int, int], rows: int = 10, cols: int = 10) -> Tuple[int, int]:
        """
        Translates a grid string (e.g. 'C4') back to center pixel coordinates (x, y).
        """
        cell = cell.strip().upper()
        if not cell or len(cell) < 2:
            raise ValueError(f"Invalid cell format: {cell}")
            
        col_char = cell[0]
        row_str = cell[1:]
        
        col_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if col_char not in col_chars:
            raise ValueError(f"Invalid column character in cell: {cell}")
            
        col_idx = col_chars.index(col_char)
        try:
            row_idx = int(row_str) - 1
        except ValueError:
            raise ValueError(f"Invalid row number in cell: {cell}")
            
        if col_idx >= cols or row_idx >= rows or row_idx < 0:
            raise ValueError(f"Cell {cell} is out of bounds for a {cols}x{rows} grid.")
            
        width, height = screen_size
        cell_w = width / cols
        cell_h = height / rows
        
        center_x = int((col_idx * cell_w) + (cell_w / 2))
        center_y = int((row_idx * cell_h) + (cell_h / 2))
        
        return center_x, center_y
