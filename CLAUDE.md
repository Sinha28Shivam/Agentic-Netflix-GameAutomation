# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (use the project venv)
venv\Scripts\activate
pip install -r requirements.txt

# Run all tests
pytest

# Run a single test file
pytest tests/test_hierarchy.py

# Run a specific test function
pytest tests/test_cv.py::test_compute_pixel_diff_identical

# Run the agent loop (requires .env with API keys and an ADB device, or use MockDevice)
python -m src.agent.graph
```

## Environment Setup

Copy `.env` and populate the following keys:

```
GEMINI_API_KEY=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_DEPLOYMENT_NAME=...
AZURE_OPENAI_API_VERSION=2024-08-01-preview   # optional, has default
```

If none are set, `GameAgentBrain` runs in mock/dry-run mode (no real LLM calls).

## Architecture

This is a **Vision-Language-Action (VLA) agentic automation framework** for playing games inside the Netflix Android app. It follows a Sense → Think → Act loop built on LangGraph.

### Four-Layer Stack

```
Device/Emulator
    ↓ pixels + XML
Perception Layer  (src/perception/)
    ↓ structured state
Cognitive Layer   (src/agent/)
    ↓ high-level actions
Execution Layer   (src/device/)
```

### LangGraph State Machine (`src/agent/graph.py`)

The compiled graph has four nodes that cycle through `capture_state` as the hub:

- **`capture_state`** — dismisses OS popups via `SystemGuard`, takes a screenshot, dumps the XML accessibility tree, detects DRM-blocked screens, and routes to one of the three action nodes.
- **`menu_navigator`** — standard UI screens (login, game library, profile picker). Hybrid: tries named skill functions first, then falls back to raw ADB tap/swipe from the brain's JSON response.
- **`gameplay`** — game canvas screens (empty XML tree, pure OpenGL rendering). Passes the raw screenshot to the VLM for coordinate grounding.
- **`crash_recovery`** — force-stops and relaunches the package, then returns to `capture_state`.

Routing logic in `route_after_capture`: terminal statuses (`success`/`failed`/`timeout`) → END; if `actionable_elements` is non-empty → `menu_navigator`; otherwise → `gameplay`; crash signals in `last_result` → `crash_recovery`.

### Shared State (`src/agent/state.py` — `AgentState`)

TypedDict passed through every node. Key fields: `device`, `brain`, `guard`, `screenshot`, `hierarchy_xml`, `actionable_elements`, `action_history` (rolling list), `goal`, `package`, `step_count`/`max_steps`, `status`.

### Cognitive Layer (`src/agent/brain.py` — `GameAgentBrain`)

Priority order for LLM backends:
1. **Azure OpenAI** (GPT-4o) if `AZURE_OPENAI_*` env vars are set
2. **Google Gemini** (default `gemini-2.5-flash`) if `GEMINI_API_KEY` is set
3. **Mock/dry-run** — rule-based fallback for offline development

Always returns a structured JSON dict: `{analysis, action, coordinates, target_label, expected_outcome}`. Valid `action` values: `TAP | SWIPE | WAIT | KEY_BACK | SUCCESS | FAILED`.

DRM handling: if `screenshot.info["drm_blocked"]` is True, `decide_action` falls back to `_decide_from_elements_only` (text-only LLM prompt, no image).

### Perception Layer

- **`HierarchyParser`** (`src/perception/hierarchy_parser.py`) — parses Android UIAutomator XML. Supports exact and `contains:` prefix matching on `text`, `resource-id`, `class`, `content-desc`. All returned nodes include computed `center_x`/`center_y`.
- **`CVEngine`** (`src/perception/cv_engine.py`) — `compute_pixel_diff` detects phantom clicks (static screen = failed tap); `locate_template` does OpenCV template matching for known UI assets.

### Device Layer

- **`BaseDevice`** (`src/device/base.py`) — abstract interface: `take_screenshot`, `dump_hierarchy`, `tap`, `swipe`, `keyevent`, `launch_app`, `stop_app`.
- **`ADBDevice`** — real device via ADB subprocess. Auto-detects ADB path on Windows. Uses `exec-out screencap -p` pipe for fast binary screenshots; sets `img.info["drm_blocked"] = True` when the frame is ≥99% black.
- **`MockDevice`** — offline simulation with three states (`login_screen` → `game_lobby` → `gameplay`). Used for unit tests and dry runs.

### Guardrails (`src/utils/guardrails.py`)

- **`SystemGuard.dismiss_system_dialogs`** — scans the XML tree for OS-level crash/alert dialogs (restricted to `android`, `com.android.systemui`, `com.google.android.gms` packages) and auto-taps dismiss buttons before each capture cycle.
- **`ActionVerifier.verify_action`** — compares before/after screenshots with `CVEngine.compute_pixel_diff`. Threshold: 0.3% for Netflix UI, 6.0% for game packages (high idle animation). Skips diff when `drm_blocked`.

### Skills (`src/agent/skills/`)

Named high-level operations called by `menu_navigator_node` when the brain's `target_label` matches a keyword pattern. Each skill accepts a `BaseDevice` and handles its own XML lookups and waits. Adding a new skill: implement in the appropriate module, export from `__init__.py`, and add a keyword match in `nodes.py:menu_navigator_node`.

### Coordinate Normalization (`src/agent/nodes.py:normalize_coordinates`)

Corrects VLM outputs that confuse portrait/landscape axes, then clamps to screen bounds. Applied before every `device.tap` or `device.swipe` call.
