import argparse
import json
import time
import sys
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file at startup
load_dotenv()

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from src.device.mock_device import MockDevice
from src.device.appium_device import AppiumDevice
from src.device.adb_device import ADB_EXE
from src.agent.brain import GameAgentBrain
from src.agent.graph import compiled_graph
from src.utils.guardrails import SystemGuard
from src.utils.logger import automation_logger
from src.utils.performance_profiler import PerformanceProfiler
from src.utils.performance_reporter import PerformanceReporter


def load_test_suite(path: str = "test_suite.json") -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        automation_logger.warning(f"Could not load {path}: {e}")
        return []


def run_orchestration(test_config: dict, mode: str, max_steps: int):
    goal = test_config.get("goal", "Navigate the app")
    package_name = test_config.get("package", "com.netflix.mediaclient")
    game_package = test_config.get("game_package")

    # Check if target game is already installed to launch directly
    if game_package and mode != "mock":
        platform = test_config.get("platform", os.environ.get("APPIUM_PLATFORM_NAME", "Android")).lower()
        if "android" in platform:
            try:
                serial = os.environ.get("APPIUM_DEVICE_NAME")
                cmd = [ADB_EXE]
                if serial:
                    cmd.extend(["-s", serial])
                cmd.extend(["shell", "pm", "path", game_package])
                
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5.0)
                if "package:" in res.stdout:
                    automation_logger.info(f"[Target Detection] Game '{game_package}' is already installed. Directly launching the game.")
                    package_name = game_package
                else:
                    automation_logger.info(f"[Target Detection] Game '{game_package}' is NOT installed. Launching Netflix client to download.")
            except Exception as e:
                automation_logger.warning(f"Failed to check package installation via ADB: {e}")

    automation_logger.info("=" * 60)
    automation_logger.info("   LANGGRAPH NETFLIX GAME AUTOMATION FRAMEWORK")
    automation_logger.info("=" * 60)
    automation_logger.info(f"Test: [{test_config.get('id')}] {test_config.get('title', '')}")
    automation_logger.info(f"Goal: {goal}")
    automation_logger.info(f"Mode: {mode.upper()}")
    automation_logger.info(f"Target App Package: {package_name}")
    automation_logger.info("-" * 60)

    # 1. Initialize Device Controller
    perf_profiler = None

    if mode == "appium":
        appium_url = os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
        capabilities = {
            "platformName": os.environ.get("APPIUM_PLATFORM_NAME", "Android"),
            "automationName": os.environ.get("APPIUM_AUTOMATION_NAME", "UiAutomator2"),
            "deviceName": os.environ.get("APPIUM_DEVICE_NAME", "Android Device"),
            "appPackage": package_name,
            "noReset": True,
            "ensureWebviewsHavePages": True,
            "nativeWebScreenshot": True,
            "newCommandTimeout": 3600,
            "connectHardwareKeyboard": True
        }
        # Only set appActivity if explicitly provided via env var.
        # Do NOT hardcode Netflix's LaunchActivity — it is not exported on MIUI/newer Android
        # and causes a SecurityException when Appium tries `am start-activity -W -n ... -S`.
        # Without appActivity, Appium uses `monkey -p <package>` (equivalent to tapping the icon).
        app_activity = os.environ.get("APPIUM_APP_ACTIVITY")
        if app_activity and app_activity != "com.netflix.mediaclient.ui.launch.LaunchActivity":
            capabilities["appActivity"] = app_activity
        try:
            device = AppiumDevice(server_url=appium_url, capabilities=capabilities)
            perf_profiler = PerformanceProfiler(device.driver, package_name)
            perf_profiler.start()
        except Exception as e:
            automation_logger.error(f"Failed to connect Appium. Falling back to Mock device. Error: {e}")
            device = MockDevice()
            mode = "mock"
    else:
        device = MockDevice()

    # 2. Initialize Core Modules
    brain = GameAgentBrain()
    guard = SystemGuard(device)

    # 3. Launch the target app
    automation_logger.info(f"Launching target app: {package_name}...")
    device.launch_app(package_name)
    time.sleep(3.0)  # Wait for cold start

    # 4. Build Initial State
    initial_state = {
        "goal": goal,
        "package": package_name,
        "test_config": test_config,
        "device": device,
        "brain": brain,
        "guard": guard,
        "screenshot": None,
        "hierarchy_xml": "",
        "actionable_elements": [],
        "action_history": [],
        "last_action": None,
        "last_result": "Started successfully.",
        "step_count": 0,
        "max_steps": max_steps,
        "status": "running"
    }

    # 6. Invoke LangGraph Compiled State Machine
    automation_logger.info("Invoking compiled LangGraph workflow...")
    try:
        final_state = compiled_graph.invoke(initial_state)
        
        status = final_state.get("status", "failed")
        automation_logger.info(f"LangGraph execution complete. Terminal status: {status.upper()}")
        
        if status == "success":
            print(f"\n[Goal Reached] AI successfully completed the task: {goal}")
        elif status == "timeout":
            print(f"\n[Timeout] Automation reached step limit ({max_steps}) without finishing.")
        else:
            print(f"\n[Goal Failed] AI failed to achieve the goal: {goal}")

    except Exception as e:
        automation_logger.error(f"LangGraph execution failed with critical exception: {e}", exc_info=True)
    finally:
        # Stop background performance profiler and dump reports on exit
        if perf_profiler:
            # Construct structured reports directory: reports/<platform>/<package>/run_<timestamp>
            platform = perf_profiler.platform_name
            timestamp_str = time.strftime("%Y%m%d_%H%M%S")
            reports_dir = os.path.join("reports", platform, package_name, f"run_{timestamp_str}")
            
            perf_data = perf_profiler.stop(reports_dir)
            perf_profiler.join()
            report_path = PerformanceReporter.generate_reports(perf_data, output_dir=reports_dir)
            
            # Read generated JSON summary and send it to AI for analysis
            if report_path and brain:
                try:
                    import json
                    json_path = report_path.replace(".md", ".json")
                    with open(json_path, "r", encoding="utf-8") as f:
                        summary = json.load(f)
                    
                    automation_logger.info("Sending performance telemetry to AI for analysis...")
                    ai_analysis = brain.analyze_performance(summary)
                    
                    # Append AI Analysis to the Markdown report
                    with open(report_path, "a", encoding="utf-8") as f:
                        f.write(f"\n\n## AI Performance Analysis & Recommendations\n\n{ai_analysis}\n")
                        
                    automation_logger.info("[PerformanceReporter] Performance report appended with AI analysis.")
                    print(f"\n=== AI Performance Analysis ===\n{ai_analysis}\n")
                except Exception as e:
                    automation_logger.error(f"Failed to generate AI performance analysis: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangGraph Netflix Game Automation Framework")
    parser.add_argument("--mode", type=str, choices=["mock", "appium"], default="appium",
                        help="appium: Appium driver (primary, cross-device), mock: offline dry-run simulator")
    parser.add_argument("--max-steps", type=int, default=25,
                        help="Maximum step limit for the agent loop")
    parser.add_argument("--test-id", type=int, default=None,
                        help="Run a specific test by ID from test_suite.json (default: first test)")
    parser.add_argument("--suite", type=str, default="test_suite.json",
                        help="Path to the test suite JSON file")

    args = parser.parse_args()

    tests = load_test_suite(args.suite)
    if not tests:
        print(f"[Error] No tests found in '{args.suite}'. Exiting.")
        sys.exit(1)

    if args.test_id is not None:
        test_config = next((t for t in tests if t.get("id") == args.test_id), None)
        if test_config is None:
            print(f"[Error] Test ID {args.test_id} not found in '{args.suite}'. Available IDs: {[t['id'] for t in tests]}")
            sys.exit(1)
    else:
        test_config = tests[0]

    run_orchestration(
        test_config=test_config,
        mode=args.mode,
        max_steps=args.max_steps,
    )
