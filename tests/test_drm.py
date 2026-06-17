import pytest
from PIL import Image
from src.device.adb_device import ADBDevice
from src.utils.guardrails import ActionVerifier

def test_is_black_frame():
    # Instantiate device with a dummy serial to avoid auto-detect subprocess calls
    device = ADBDevice(device_serial="dummy_serial_123")
    
    # 1. Fully black image
    img_black = Image.new("RGB", (100, 100), color="black")
    assert device._is_black_frame(img_black)
    
    # 2. Mostly black image (99% black)
    img_mostly_black = Image.new("RGB", (100, 100), color="black")
    img_mostly_black.putpixel((0, 0), (255, 255, 255)) # 1 white pixel out of 10000 = 0.01%
    assert device._is_black_frame(img_mostly_black)
    
    # 3. Non-black image (e.g. blue)
    img_blue = Image.new("RGB", (100, 100), color="blue")
    assert not device._is_black_frame(img_blue)

def test_action_verifier_drm_bypass():
    img1 = Image.new("RGB", (100, 100), color="black")
    img2 = Image.new("RGB", (100, 100), color="black")
    
    # Normally, static image verification fails (since there is 0% pixel change)
    verified, msg = ActionVerifier.verify_action(
        before_img=img1,
        after_img=img2,
        action_type="TAP",
        expected_outcome="",
        post_xml="",
        package_name="com.netflix.mediaclient"
    )
    assert verified is False
    assert "Screen remained static" in msg

    # If before_img has drm_blocked info flag set, the verify_action should return True
    img1.info["drm_blocked"] = True
    verified, msg = ActionVerifier.verify_action(
        before_img=img1,
        after_img=img2,
        action_type="TAP",
        expected_outcome="",
        post_xml="",
        package_name="com.netflix.mediaclient"
    )
    assert verified is True
    assert "DRM mode" in msg

    # If after_img has drm_blocked info flag set, it should also return True
    img1.info.clear()
    img2.info["drm_blocked"] = True
    verified, msg = ActionVerifier.verify_action(
        before_img=img1,
        after_img=img2,
        action_type="TAP",
        expected_outcome="",
        post_xml="",
        package_name="com.netflix.mediaclient"
    )
    assert verified is True
    assert "DRM mode" in msg
