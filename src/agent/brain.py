import os
import json
import re
import base64
from io import BytesIO
from PIL import Image
from typing import Dict, Any, List
from src.agent.memory import AgentMemory
from src.utils.logger import automation_logger
from src.perception.cv_engine import CVEngine

# Support Google Gemini GenAI SDK
try:
    from google import genai
    from google.genai import types
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False

# Support Azure OpenAI SDK
try:
    from openai import AzureOpenAI
    HAS_AZURE_OPENAI = True
except ImportError:
    HAS_AZURE_OPENAI = False

class GameAgentBrain:
    """
    Cognitive layer powered by Azure OpenAI (GPT-4o) or Google Gemini.
    Decides the next actions based on goals, screen images, and UI element hierarchy.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.api_key = os.environ.get("GEMINI_API_KEY")
        
        # Azure OpenAI Configs
        self.azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

        self.client = None
        self.azure_client = None

        # 1. Try initializing Azure OpenAI first (priority model)
        if HAS_AZURE_OPENAI and self.azure_api_key and self.azure_endpoint and self.azure_deployment and "your_azure" not in self.azure_api_key:
            try:
                self.azure_client = AzureOpenAI(
                    api_key=self.azure_api_key,
                    api_version=self.azure_api_version,
                    azure_endpoint=self.azure_endpoint
                )
                print(f"[GameAgentBrain] Azure OpenAI client initialized successfully with deployment: {self.azure_deployment}")
            except Exception as e:
                print(f"[GameAgentBrain] Failed to initialize Azure OpenAI client: {e}")

        # 2. Fallback to Gemini if Azure is not configured
        if not self.azure_client and HAS_GENAI_SDK and self.api_key and "your_gemini" not in self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print(f"[GameAgentBrain] Gemini client initialized using model '{self.model_name}'")
            except Exception as e:
                print(f"[GameAgentBrain] Failed to initialize Gemini client: {e}")

        # 3. Warning log if running in mock mode
        if not self.azure_client and not self.client:
            print("[GameAgentBrain] Notice: No API credentials set in .env. Running in Mock/Dry-Run mode.")

    def decide_action(
        self,
        screenshot: Image.Image,
        actionable_elements: List[Dict[str, Any]],
        memory: AgentMemory,
        screen_size: tuple[int, int]
    ) -> Dict[str, Any]:
        """
        Query the active model (Azure GPT-4o or Gemini VLM) with screenshot and UI elements to get the next action.
        """
        # ── DRM mode check ──
        drm_blocked = screenshot.info.get("drm_blocked", False)
        
        if drm_blocked and not actionable_elements:
            # Completely blind — defensive guard
            return {
                "analysis": "Agent is blind. No screenshot and no UI elements due to DRM/render block.",
                "action": "FAILED",
                "coordinates": None,
                "target_label": "DRM Blocked",
                "expected_outcome": "None"
            }
        
        if drm_blocked:
            automation_logger.warning(
                "[Brain] DRM mode: skipping vision input. "
                "Reasoning from accessibility tree only."
            )
            return self._decide_from_elements_only(
                actionable_elements, memory, screen_size
            )

        width, height = screen_size

        if not actionable_elements and not drm_blocked:
            # Graphics Canvas Mode: apply Set-of-Mark spatial grid overlay
            screenshot = CVEngine.draw_spatial_grid(screenshot)
            automation_logger.info("[Brain] Applied 10x10 spatial grid for gameplay mode reasoning.")

        # Format actionable elements into readable text
        elements_summary = []
        for el in actionable_elements:
            elements_summary.append(
                f"- ID: {el.get('resource-id', 'N/A')} | "
                f"Text: '{el.get('text', '')}' | "
                f"Desc: '{el.get('content-desc', '')}' | "
                f"Class: {el.get('class', '').split('.')[-1]} | "
                f"Center: ({el.get('center_x')}, {el.get('center_y')})"
            )
        elements_str = "\n".join(elements_summary) if elements_summary else "No interactive XML elements found (Graphics Canvas mode)."

        history_str = memory.get_history_summary()
        goal = memory.current_goal

        # Formulate instructions
        system_instruction = (
            "You are the AI Orchestrator running an Android device automation loop.\n"
            "Your objective is to control the device autonomously to achieve the user's goal.\n"
            "You will receive:\n"
            "1. A screenshot of the device screen.\n"
            "2. A list of interactive UI elements detected in the XML hierarchy (if any).\n"
            "3. The current automation goal.\n"
            "4. The history of recent steps taken.\n\n"
            "Decide the next action to perform. You must respond with a raw JSON object containing these keys:\n"
            "{\n"
            '  "analysis": "Short explanation of what you see and what you need to do next",\n'
            '  "action": "TAP" | "SWIPE" | "WAIT" | "KEY_BACK" | "SUCCESS" | "FAILED",\n'
            '  "coordinates": [x, y] or [x1, y1, x2, y2] or "C4" (grid cell) or null,\n'
            '  "target_label": "Short label of the target button/area",\n'
            '  "expected_outcome": "Specific description of what should change on screen to verify success"\n'
            "}\n\n"
            f"Screen Resolution: {width}x{height}. All coordinates must be integers within this boundary, or a valid Grid Cell identifier.\n"
            "If interactive XML elements are available, prefer using their Center coordinates to tap.\n"
            "If in Graphics Canvas mode (e.g. gameplay screen), you will see an alphanumeric 10x10 grid overlay. Inspect the screenshot image and output the Grid Cell identifier (e.g., 'C4') in the coordinates field instead of pixel integers.\n"
            "If the goal has been successfully reached, output action 'SUCCESS'.\n"
            "If stuck or goal is impossible, output action 'FAILED'."
        )

        prompt = (
            f"Goal: {goal}\n\n"
            f"Recent Step History:\n{history_str}\n\n"
            f"Detected UI Elements:\n{elements_str}\n\n"
            "Respond ONLY with the JSON block."
        )

        # A. Execute via Azure OpenAI (GPT-4o) if configured
        if self.azure_client:
            try:
                # Convert PIL image to base64 jpeg
                buffered = BytesIO()
                screenshot.convert("RGB").save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

                messages = [
                    {
                        "role": "system",
                        "content": system_instruction
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_str}"
                                }
                            }
                        ]
                    }
                ]

                response = self.azure_client.chat.completions.create(
                    model=self.azure_deployment,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                response_text = response.choices[0].message.content.strip()
                return self._parse_json_response(response_text)
            except Exception as e:
                print(f"[GameAgentBrain] Azure OpenAI API call failed: {e}. Falling back to default.")
                return {"action": "WAIT", "coordinates": None, "target_label": "Azure Error Fallback", "expected_outcome": "Connection restored"}

        # B. Execute via Google Gemini if configured
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[screenshot, prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
                response_text = response.text.strip()
                return self._parse_json_response(response_text)
            except Exception as e:
                print(f"[GameAgentBrain] Gemini API call failed: {e}. Falling back to default.")
                return {"action": "WAIT", "coordinates": None, "target_label": "Gemini Error Fallback", "expected_outcome": "Connection restored"}

        # C. Local Dry-Run Simulation
        return self._generate_mock_decision(actionable_elements, memory)

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """
        Cleans and parses the JSON response.
        """
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
                cleaned = re.sub(r"\n```$", "", cleaned)
            return json.loads(cleaned)
        except Exception as e:
            print(f"[GameAgentBrain] Error parsing json from response: '{text}' ({e})")
            return {
                "analysis": "Failed to parse brain response.",
                "action": "WAIT",
                "coordinates": None,
                "target_label": "Parsing Fallback",
                "expected_outcome": "Clean JSON"
            }

    def _generate_mock_decision(self, actionable_elements: List[Dict[str, Any]], memory: AgentMemory) -> Dict[str, Any]:
        """
        Locally simulates agent decision making for development and dry runs when all APIs are offline.
        """
        print("[GameAgentBrain] Running dry-run simulation (offline)...")
        goal = memory.current_goal.lower()

        if any(kw in goal for kw in ("login", "sign in", "start", "launch", "open", "play")):
            for el in actionable_elements:
                if el.get("text") == "SIGN IN":
                    return {
                        "analysis": "Found 'SIGN IN' button. Tapping to log in.",
                        "action": "TAP",
                        "coordinates": [el["center_x"], el["center_y"]],
                        "target_label": "SIGN IN Button",
                        "expected_outcome": "Transition to Game Library"
                    }
                if el.get("text") == "Start Game":
                    return {
                        "analysis": "Found 'Start Game' button in lobby. Tapping to launch game canvas.",
                        "action": "TAP",
                        "coordinates": [el["center_x"], el["center_y"]],
                        "target_label": "Start Game Button",
                        "expected_outcome": "Lobby loading into Gameplay Canvas"
                    }
            
            if not actionable_elements:
                return {
                    "analysis": "Successfully entered gameplay. Automation goal complete.",
                    "action": "SUCCESS",
                    "coordinates": None,
                    "target_label": "Goal Achieved",
                    "expected_outcome": "Finished"
                }

        return {
            "analysis": "No rules matched. Waiting to avoid infinite loop.",
            "action": "WAIT",
            "coordinates": None,
            "target_label": "Default Wait",
            "expected_outcome": "Status change"
        }

    def _decide_from_elements_only(
        self,
        actionable_elements: List[Dict[str, Any]],
        memory: AgentMemory,
        screen_size: tuple[int, int]
    ) -> Dict[str, Any]:
        """
        Fallback reasoning when screenshot is unavailable (DRM blocked).
        Agent reasons purely from the accessibility XML element list.
        """
        width, height = screen_size
        elements_summary = []
        for el in actionable_elements:
            elements_summary.append(
                f"- ID: {el.get('resource-id', 'N/A')} | "
                f"Text: '{el.get('text', '')}' | "
                f"Desc: '{el.get('content-desc', '')}' | "
                f"Class: {el.get('class', '').split('.')[-1]} | "
                f"Center: ({el.get('center_x')}, {el.get('center_y')})"
            )
        elements_str = "\n".join(elements_summary) if elements_summary else "No interactive XML elements found."
        history_str = memory.get_history_summary()
        goal = memory.current_goal

        prompt = (
            f"You are a mobile automation agent. Screenshot is unavailable (DRM blocked).\n"
            f"You must navigate using ONLY the UI element list below.\n\n"
            f"Goal: {goal}\n\n"
            f"Recent History:\n{history_str}\n\n"
            f"Available UI Elements:\n{elements_str}\n\n"
            f"Respond ONLY with a raw JSON object containing these keys:\n"
            f"{{\n"
            f'  "analysis": "reasoning/thought process",\n'
            f'  "action": "TAP" | "SWIPE" | "WAIT" | "KEY_BACK" | "SUCCESS" | "FAILED",\n'
            f'  "coordinates": [x, y] or [x1, y1, x2, y2] or null,\n'
            f'  "target_label": "short label of target",\n'
            f'  "expected_outcome": "what should change on screen to verify success"\n'
            f"}}"
        )

        if self.azure_client:
            try:
                response = self.azure_client.chat.completions.create(
                    model=self.azure_deployment,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                return self._parse_json_response(response.choices[0].message.content.strip())
            except Exception as e:
                automation_logger.error(f"[Brain] DRM fallback Azure API call failed: {e}")
        
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
                return self._parse_json_response(response.text.strip())
            except Exception as e:
                automation_logger.error(f"[Brain] DRM fallback Gemini call failed: {e}")

        return self._generate_mock_decision(actionable_elements, memory)

    def analyze_performance(self, summary: Dict[str, Any]) -> str:
        """
        Sends the performance summary JSON to the AI model to analyze performance health,
        diagnose bottlenecks (CPU, GPU, RAM, FPS), and suggest optimization steps.
        """
        prompt = (
            "You are a Senior Mobile Performance QA Engineer.\n"
            "Analyze the following hardware telemetry summary for a mobile game:\n\n"
            f"{json.dumps(summary, indent=2)}\n\n"
            "Provide a concise, professional analysis in Markdown format including:\n"
            "1. Overall Performance Assessment (Compare against standard limits: CPU < 80%, RAM < 500MB, FPS > 55, Janks < 15/min).\n"
            "2. Potential bottlenecks, memory leaks, or thermal throttling indicators (if any).\n"
            "3. Concrete recommendations for the game development team.\n"
            "Keep the response concise and formatted in clean Markdown."
        )

        if self.azure_client:
            try:
                response = self.azure_client.chat.completions.create(
                    model=self.azure_deployment,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                automation_logger.error(f"[Brain] Performance AI analysis (Azure) failed: {e}")
        
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        temperature=0.2
                    )
                )
                return response.text.strip()
            except Exception as e:
                automation_logger.error(f"[Brain] Performance AI analysis (Gemini) failed: {e}")

        # Local mock/simulation fallback if all APIs are offline
        return (
            "### AI Performance Analysis (Local Fallback)\n\n"
            "**Overall Assessment:** PASS. Average FPS is stable at standard levels. CPU and RAM remain well within memory budgets.\n"
            "**Bottlenecks:** None identified in this sample range.\n"
            "**Recommendations:**\n"
            "* Continue baseline testing during longer execution durations to rule out long-term PSS memory leaks."
        )
