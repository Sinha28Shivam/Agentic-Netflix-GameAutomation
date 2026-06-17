import json
import argparse
import sys
import os
from main import run_orchestration
from src.utils.logger import automation_logger

TEST_SUITE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_suite.json"))

def load_test_suite():
    try:
        with open(TEST_SUITE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Failed to load test_suite.json: {e}")
        sys.exit(1)

def display_test_cases(test_cases):
    print("=" * 70)
    print("                 NETFLIX GAMES TEST CASE SUITE")
    print("=" * 70)
    print(f"{'ID':<4} | {'Test Case Title':<30} | {'Package Type':<25}")
    print("-" * 70)
    for tc in test_cases:
        pkg_type = "Netflix App" if tc["package"] == "com.netflix.mediaclient" else "Netflix Game"
        print(f"{tc['id']:<4} | {tc['title']:<30} | {pkg_type:<25}")
    print("-" * 70)

def main():
    parser = argparse.ArgumentParser(description="Netflix Game QA Test Suite Runner")
    parser.add_argument("--test-id", type=int, default=None,
                        help="The ID of the specific test case you want to execute")
    parser.add_argument("--mode", type=str, choices=["adb", "mock"], default="adb",
                        help="Execution mode (adb or mock)")
    parser.add_argument("--max-steps", type=int, default=15,
                        help="Step limit for the test run")
    
    args = parser.parse_args()
    
    test_cases = load_test_suite()
    
    # 1. Execute direct test-id if passed in command line
    if args.test_id is not None:
        target_tc = next((tc for tc in test_cases if tc["id"] == args.test_id), None)
        if not target_tc:
            print(f"[Error] Test Case ID {args.test_id} not found in registry.")
            sys.exit(1)
        
        print(f"[Runner] Launching Test ID {target_tc['id']}: {target_tc['title']}")
        run_orchestration(
            goal=target_tc["goal"],
            mode=args.mode,
            max_steps=args.max_steps,
            package_name=target_tc["package"]
        )
        sys.exit(0)
        
    # 2. Interactive CLI Mode
    display_test_cases(test_cases)
    
    try:
        user_input = input("\nEnter the Test Case ID you want to run (or type 'exit'): ").strip()
        if user_input.lower() == "exit":
            print("Exiting test suite runner.")
            sys.exit(0)
            
        test_id = int(user_input)
        target_tc = next((tc for tc in test_cases if tc["id"] == test_id), None)
        if not target_tc:
            print(f"[Error] Test Case ID {test_id} not found.")
            sys.exit(1)
            
        print(f"\n[Runner] Executing Test Case: {target_tc['title']}")
        run_orchestration(
            goal=target_tc["goal"],
            mode=args.mode,
            max_steps=args.max_steps,
            package_name=target_tc["package"]
        )
        
    except ValueError:
        print("Invalid input. Please enter a valid numerical Test ID.")
    except KeyboardInterrupt:
        print("\nTest execution interrupted.")

if __name__ == "__main__":
    main()
