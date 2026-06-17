import argparse
import time
import sys
import os
import subprocess
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file at startup
load_dotenv()

from src.device.adb_device import ADBDevice, ADB_EXE
from src.device.mock_device import MockDevice
from src.perception.hierarchy_parser import HierarchyParser
from src.agent.brain import GameAgentBrain
from src.agent.graph import compiled_graph
from src.utils.guardrails import SystemGuard
from src.utils.logger import automation_logger
from src.utils.telemetry import TelemetryDaemon

def run_orchestration(goal: str, mode: str, max_steps: int, package_name: str):
    automation_logger.info("=" * 60)
    automation_logger.info("   LANGGRAPH NETFLIX GAME AUTOMATION FRAMEWORK")
    automation_logger.info("=" * 60)
    automation_logger.info(f"Goal: {goal}")
    automation_logger.info(f"Mode: {mode.upper()}")
    automation_logger.info(f"Target App Package: {package_name}")
    automation_logger.info("-" * 60)

    # 1. Initialize Device Controller
    if mode == "adb":
        device = ADBDevice()
        if not device.device_serial:
            automation_logger.error("No active physical Android devices found over ADB. Falling back to Mock.")
            device = MockDevice()
            mode = "mock"
    else:
        device = MockDevice()

    # 2. Initialize Telemetry Daemon
    telemetry = None
    if mode == "adb":
        # Launch telemetry in background for real device
        telemetry = TelemetryDaemon(ADB_EXE, device.device_serial)
        telemetry.start()
    else:
        # Start a local/mock telemetry logger for simulation runs
        telemetry = TelemetryDaemon("mock_adb", None)
        telemetry.start()

    # 3. Initialize Core Modules
    brain = GameAgentBrain()
    guard = SystemGuard(device)

    # 4. Launch the target app
    automation_logger.info(f"Launching target app: {package_name}...")
    device.launch_app(package_name)
    time.sleep(3.0)  # Wait for cold start

    # 5. Build Initial State
    initial_state = {
        "goal": goal,
        "package": package_name,
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
        # Stop background telemetry thread on exit
        if telemetry:
            telemetry.stop()
            telemetry.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangGraph Netflix Game Automation Framework")
    parser.add_argument("--goal", type=str, default="Sign in to Netflix Games and launch the game",
                        help="The target objective for the AI loop")
    parser.add_argument("--mode", type=str, choices=["adb", "mock"], default="adb",
                        help="adb: run on physical device, mock: dry-run simulator")
    parser.add_argument("--max-steps", type=int, default=10,
                        help="Maximum step limits for agent loop")
    parser.add_argument("--package", type=str, default="com.netflix.mediaclient",
                        help="The Android App Package to launch and automate")
    
    args = parser.parse_args()
    
    # Auto-detect if we have any ADB device connected. If not, fallback to mock to prevent instant failure.
    if args.mode == "adb":
        try:
            output = subprocess.check_output([ADB_EXE, "devices"], text=True)
            lines = output.strip().split("\n")[1:]
            devices = [line for line in lines if line.strip() and "device" in line]
            if not devices:
                print("[Warning] No connected ADB devices detected. Forcing mock simulator mode.")
                args.mode = "mock"
        except Exception as e:
            print(f"[Warning] ADB error encountered: {e}. Forcing mock simulator mode.")
            args.mode = "mock"

    run_orchestration(
        goal=args.goal,
        mode=args.mode,
        max_steps=args.max_steps,
        package_name=args.package
    )
