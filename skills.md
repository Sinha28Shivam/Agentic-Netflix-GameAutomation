# Agent Automation Skills Catalog (Android)

This document catalogs the high-level reusable routines (skills) available to the AI Orchestrator. The AI uses these skills to execute standard navigation, device state changes, and verification checks.

---

## 1. App Navigation Skills

### `open_games_tab()`
*   **Purpose**: Navigates to the Games section in the primary Netflix application.
*   **Execution**: Scans the bottom navigation bar in the UI hierarchy XML for a tab containing text "Games" or resource-id `com.netflix.mediaclient:id/games_tab` and taps it.

### `search_game_by_name(game_name: str)`
*   **Purpose**: Searches the Netflix catalog for a specific game title.
*   **Execution**:
    1. Locates the search search icon (`com.netflix.mediaclient:id/search_button`) and clicks it.
    2. Inputs `game_name` using `adb shell input text`.
    3. Triggers search submission.

### `scroll_catalog(direction: str = "down", scrolls: int = 1)`
*   **Purpose**: Scrolls list views to search or reveal content.
*   **Execution**: Runs a swipe gesture from `[center_x, center_y_start]` to `[center_x, center_y_end]` based on direction.

---

## 2. Netflix Account & Session Skills

### `select_netflix_profile(profile_name: str)`
*   **Purpose**: Authenticates past the initial profile selection overlay.
*   **Execution**: Scans the screen nodes for matching `text` or `content-desc` corresponding to `profile_name` and taps the icon center.

### `install_game_from_store(package_name: str)`
*   **Purpose**: Automates App Store / Play Store redirects and installs the target game.
*   **Execution**:
    1. Taps "Get Game" or "Install" in the Netflix app details page.
    2. Detects the Play Store application launch.
    3. Clicks "Install" button inside the Play Store.
    4. Loops `adb shell pm list packages` every 5 seconds until the package is listed as active.

### `launch_game_package(package_name: str)`
*   **Purpose**: Start the installed game.
*   **Execution**: Launches the app package directly using the ADB `monkey` tool.

---

## 3. Hardware & OS Control Skills

### `toggle_network(enabled: bool)`
*   **Purpose**: Enable or disable Wi-Fi/data connection (for Network Loss / Offline tests).
*   **Execution**: Runs `adb shell svc wifi enable` (or `disable`) and `adb shell svc data enable` (or `disable`).

### `rotate_screen(mode: str)`
*   **Purpose**: Rotate screen orientation.
*   **Execution**: 
    *   If `mode == "landscape"`, runs `adb shell content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1`.
    *   If `mode == "portrait"`, runs `adb shell content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:0`.

### `set_audio_mute(mute: bool)`
*   **Purpose**: Mute or unmute device sound.
*   **Execution**: Sends keyevents `164` (Mute/Unmute toggle) or adjusts volume steps via keyevent `25` (Volume Down) and `24` (Volume Up).

---

## 4. Telemetry & Verification Skills

### `measure_launch_time(package_name: str) -> float`
*   **Purpose**: Calculate cold start loading latency.
*   **Execution**: Records start epoch, issues `monkey` launch command, and polls screens via pixel-diffs until loading spinners clear. Returns total duration.

### `get_battery_status() -> dict`
*   **Purpose**: Read telemetry for battery consumption tests.
*   **Execution**: Parses output of `adb shell dumpsys battery` returning `level` (percentage), `voltage`, and `temperature`.

### `simulate_crash_recovery(package_name: str)`
*   **Purpose**: Test game resilience to sudden closures.
*   **Execution**:
    1. Force kills the app: `adb shell am force-stop package_name`.
    2. Relaunches the app package.
    3. Verifies that the game state resumes from save data.
