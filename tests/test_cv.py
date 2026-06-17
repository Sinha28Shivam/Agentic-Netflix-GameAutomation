import pytest
from PIL import Image, ImageDraw
from src.perception.cv_engine import CVEngine

def test_compute_pixel_diff_identical():
    # Create two identical blue images
    img1 = Image.new("RGB", (100, 100), color="blue")
    img2 = Image.new("RGB", (100, 100), color="blue")
    
    diff = CVEngine.compute_pixel_diff(img1, img2)
    assert diff == 0.0

def test_compute_pixel_diff_different():
    # Create one blue and one red image
    img1 = Image.new("RGB", (100, 100), color="blue")
    img2 = Image.new("RGB", (100, 100), color="red")
    
    diff = CVEngine.compute_pixel_diff(img1, img2)
    # The diff should be very close to 100% since we changed the whole background
    assert diff > 90.0

def test_compute_pixel_diff_partial():
    # Create a base image and one with a red square drawn on it
    img1 = Image.new("RGB", (100, 100), color="white")
    img2 = Image.new("RGB", (100, 100), color="white")
    
    draw = ImageDraw.Draw(img2)
    # Draw a 20x20 square (400 pixels out of 10000 = 4% change)
    draw.rectangle([40, 40, 59, 59], fill="red")
    
    diff = CVEngine.compute_pixel_diff(img1, img2)
    # Allow some thresholding and edge smoothing tolerances
    assert 3.0 <= diff <= 5.0
