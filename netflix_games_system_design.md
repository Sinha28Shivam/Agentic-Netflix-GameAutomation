# System Design: Agentic Game Automation for Netflix Mobile

This document outlines the end-to-end system architecture, tools, workflows, and error-handling strategies for automating games on the Netflix Mobile application using an AI-driven, agentic approach implemented in Python.

---

## 1. Executive Summary

Automating mobile games inside a wrapper application like Netflix presents unique challenges: dynamic visual interfaces, non-standard UI hierarchies, strict DRM (Digital Rights Management) constraints, and unpredictable game states. 

To solve this, we design an **Agentic (Sense-Think-Act) Automation Framework**. Instead of relying on brittle, coordinate-based scripting or standard accessibility trees (which games rarely expose), this framework uses a **Vision-Language-Action (VLA)** loop. A Python-based orchestration engine drives a Multimodal AI Agent (VLM) that reads screen pixels, determines game state, reasons about goals, and executes touchscreen inputs.

---

## 2. System Architecture

The architecture is divided into four main layers:
1. **Target Layer (Device/Emulator)**: The physical or emulated Android/iOS device running Netflix and the target game.
2. **Perception Layer (Sense)**: Translates raw pixels and video streams into structured state data.
3. **Cognitive Layer (Think)**: The AI Agent (powered by a Vision-Language Model) that decides what action to take next.
4. **Execution Layer (Act)**: Translates high-level decisions into low-level OS inputs (taps, swipes).

```
                             +--------------------------+
                             | Target Layer             |
                             | (Mobile Device/Emulator) |
                             +------------+-------------+
                                          |
                                          | Screen Pixels
                                          v
                             +--------------------------+
                             | Perception Layer (Sense) |
                             | (OCR, Template Match, CV)|
                             +------------+-------------+
                                          |
                                          | Structured Visual State
                                          v
                             +--------------------------+
                             | Cognitive Layer (Think)  |
                             | (LangGraph Agent & VLM)  |
                             +------------+-------------+
                                          |
                                          | High-Level Action
                                          v
                             +--------------------------+
                             | Execution Layer (Act)    |
                             | (ADB / Appium Bridge)    |
                             +------------+-------------+
                                          |
                                          | Inject Touch Events
                                          +---------------------+
```

---

## 3. Core Automation Flow (The Agent Loop)

The agent operates in a continuous loop:

1. **Capture**: Capture the current screen of the mobile device.
2. **Perception**: Extract obvious metadata (e.g., text present, template matches for common buttons) to reduce VLM token usage and guide LLM reasoning.
3. **Formulate Context**: Combine the screenshot, extracted text, current game goal, and past 5 actions into a prompt.
4. **Inference**: Query the Multimodal LLM (e.g., Gemini 2.5 Flash/Pro) to return a structured JSON response containing:
   - Current situation analysis.
   - Intended action (e.g., `CLICK`, `SWIPE`, `DRAG`, `WAIT`).
   - Targets (either relative/absolute coordinates, or visual labels).
   - Expected outcome (for verification).
5. **Execution**: Execute the action via ADB (Android) or Appium (iOS/Android).
6. **Verify**: Wait, take a new screenshot, and compare it with the expected outcome to check for success, failure, or unexpected states.

---

## 4. Suggested Technology Stack (Python-centric)

* **Orchestration & Logic**: **Python 3.10+** - Industry standard for AI, agentic framework integration, and testing libraries.
* **Agent Framework**: **LangGraph** or **AutoGen** - Allows stateful, cyclic agent flows. LangGraph is excellent for handling complex state transitions and error recovery graphs.
* **AI Model (VLM)**: **Gemini 2.5 Flash / Pro** or **GPT-4o** - Multimodal capability with high spatial accuracy for coordinate placement. Gemini's native multimodal API is highly cost-effective and supports high-resolution image inputs.
* **Device Controller**: **pure-python-adb** (Android) / **Appium** (Cross-platform) - `pure-python-adb` provides raw socket speed for ADB operations (screenshots, taps, swipes) without the overhead of Appium. Use Appium if iOS support is mandatory.
* **Computer Vision (CV)**: **OpenCV (`opencv-python`)** & **Pillow** - Image resizing, color thresholding, template matching (e.g., checking if a standard icon is visible), and frame difference (motion detection).
* **Object Detection**: **Ultralytics YOLOv8 / YOLOv10** - For complex games, train a lightweight model to locate specific entities (e.g., enemies, gold coins, obstacles) in real-time.
* **OCR**: **EasyOCR** or **Tesseract (`pytesseract`)** - Extracts text from the screen (e.g., scores, menu text, pop-up dialogs).
* **Testing & Verification**: **pytest** - Structure test suites, handle mock environments, and run parallel automation tracks.

---

## 5. Critical Engineering Challenge: DRM (Digital Rights Management)

The Netflix application enforces Widevine DRM policies. When taking standard screenshots via ADB (`screencap`) or Appium on a non-rooted, standard retail device, the resulting image is often completely black.

### Architectural Workarounds for DRM:
1. **Android Emulator with DRM Disabled**: Use Android Virtual Devices (AVDs) running Google APIs system images without Widevine hardware backing.
2. **Rooted Devices**: Use a physical Android device rooted with Magisk and modules like *Disable-Flag_Secure* to bypass screenshot restrictions.
3. **Hardware-in-the-Loop (HIL)**: Connect the mobile device to an HDMI capture card via a USB-C dock. Capture the screen via a webcam stream in Python (`cv2.VideoCapture`). Inject touch events via ADB over Wi-Fi/USB. This is the most bulletproof enterprise solution as it bypasses OS-level software blocking.

---

## 6. Addressing False Positives and False Negatives

In AI-driven automation, standard assertions (e.g., `assert button.exists()`) fail because game UI is rendered dynamically in a canvas rather than standard OS UI views. We define and mitigate False Positives (FP) and False Negatives (FN) as follows:

### 6.1. False Positives (FP)
*Definition: The agent believes an action succeeded or game is in State A, but it actually failed or is in State B.*

* **Phantom Click**: Network lag or frame drop. The agent sent a click command, did not check state change, and assumed it progressed.
  * *Mitigation*: **Double-Check State (Visual Diffing)**: Compare screenshots before and after the action. If the pixel change is below a threshold (or visual hash matches 99%), flag that the click did not register and retry.
* **Misidentified Button**: The VLM outputs coordinates for "Play" but hits a decorative background element instead.
  * *Mitigation*: **Perception Grounding**: Use OpenCV template matching or YOLO bounding boxes to verify coordinates before clicking. Translate VLM target description (e.g., "Start Button") into specific coordinates verified by local CV instead of blindly trusting VLM coordinates.
* **Dismissed Dialog Assumption**: A random system popup (e.g., Low Battery, Google Play update) appears. The agent thinks it closed it, but the game is still blocked.
  * *Mitigation*: **System Guardrails**: A background thread checks for standard OS system dialogs using OCR/Appium UI hierarchy and auto-dismisses them outside the main agent loop.

### 6.2. False Negatives (FN)
*Definition: The agent believes a failure has occurred (e.g., game crashed, button missing, frozen), but the game is working fine.*

* **Slow Loading Screen**: A game level takes 15 seconds to load. The agent times out at 5 seconds and reports a game crash.
  * *Mitigation*: **Activity Detection**: Use optical flow or pixel-wise diffs over a 3-second window. If there are small changes (e.g., loading spinner rotating), wait. Increase timeouts for transitions known to involve network calls.
* **Occluded/Animated Buttons**: A button is pulsed, animated, or temporarily covered by an in-game tutorial finger. OCR or template matching fails to detect it.
  * *Mitigation*: **Multimodal Fallback**: If standard CV fails, pass the raw image to the VLM with a prompt like: *"The automated detector failed to find the 'Claim' button. Can you locate it in this image?"*
* **Network Spinner False Alarm**: A brief connection spinner appears. The agent marks the run as failed.
  * *Mitigation*: **Graceful Recovery Polling**: Implement a cooling-off period. When an anomaly is detected, trigger a recovery state: wait 5 seconds, capture a new frame, and re-assess before throwing a test failure.

---

## 7. Action Verification Matrix

To guarantee robustness, every action executed must be validated:

```python
class ActionVerifier:
    def verify_action(self, before_img, after_img, action_type, expected_result):
        if action_type == "TAP":
            # 1. Did the screen change at all? (Avoid phantom clicks)
            if self._is_screen_static(before_img, after_img):
                return False, "Screen did not change. Tap might have been ignored."
            
        # 2. State-specific checks
        if expected_result.get("target_screen"):
            # Use OCR/CV to check if the target screen elements exist
            exists = self._detect_screen_signature(after_img, expected_result["target_screen"])
            if not exists:
                return False, f"Failed to transition to {expected_result['target_screen']}"
                
        return True, "Success"
```

---

## 8. Summary of Implementation Plan for PoC

If you approve this architecture, we will build a Proof of Concept (PoC) codebase with the following structure:
1. **`device_connector.py`**: Handles raw ADB connection, screen captures, and input injection.
2. **`perception_engine.py`**: Runs OCR (EasyOCR/Tesseract) and OpenCV template matching to extract raw UI coordinates.
3. **`agent_brain.py`**: Integrates with the LLM/VLM API, manages conversation memory, prompts, and returns clean actions.
4. **`guardrails.py`**: Checks for system dialogs, network errors, app crashes, and visual diffs to eliminate false positives/negatives.
5. **`main.py`**: Runs the orchestration agent loop.
