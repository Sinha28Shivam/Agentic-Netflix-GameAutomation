# Bloons TD 6 Gameplay Test Cases
 
**Bloons TD 6** is a fast-paced tower defense game where players deploy specialized monkey towers to pop waves of invading balloons. These tests validate an AI agent's ability to handle real-time spatial physics, drag-and-drop mechanics, and rapid UI state evaluation during dynamic gameplay.
 
## Test Case Glossary
 
1. Title Screen Navigation & Profile Handshake

2. Sidebar Carousel Navigation

3. Drag-and-Drop Placement Validation

4. Target Priority Adjustment

5. Upgrade Path Branching Logic

6. Battle Speed Toggle

7. Cooldown Ability Synchronization

8. Micro-Management Re-Sell Infrastructure

9. Defeat Modal Interaction

10. System Update Notification Handling
 
---
 
## Section 1: Navigation & UI Interaction
 
### Test 1: Title Screen Navigation & Profile Handshake
 
**What We're Testing:**

Navigating the dynamic title screen and entering the main game lobby successfully.
 
**Why It Matters:**

This confirms the agent can handle variable loading times and navigate past promotional pop-ups to reach the core gameplay.
 
**What We're Solving For:**

* Detecting when asset loading is complete

* Identifying and tapping the primary "Start" button while ignoring distracting promotional banners

* Verifying the home village screen loads with currency totals visible
 
---
 
### Test 2: Sidebar Carousel Navigation
 
**What We're Testing:**

Using precise swiping controls to locate hidden items in a compact scroll menu.
 
**Why It Matters:**

Many tower options are hidden below the viewport, requiring accurate scrolling to access.
 
**What We're Solving For:**

* Dragging the tower panel up and down to reveal units below the fold

* Confirming that hidden towers become visible and their price displays change from grayed-out to active
 
---
 
## Section 2: Tower Placement & Combat Mechanics
 
### Test 3: Drag-and-Drop Placement Validation
 
**What We're Testing:**

Distinguishing legal terrain from illegal collision boundaries when placing towers.
 
**Why It Matters:**

Towers must be placed on valid grass areas, not on paths, rocks, or other towers.
 
**What We're Solving For:**

* Executing smooth drag-and-drop tower placement

* Detecting visual color-state indicators (red for invalid, white/green for valid)

* Ensuring towers snap cleanly to legal coordinates without getting stuck
 
---
 
### Test 4: Target Priority Adjustment
 
**What We're Testing:**

Changing a tower's targeting logic through contextual sub-menus.
 
**Why It Matters:**

Different targeting strategies (First, Last, Close, Strong) are critical for optimal tower placement and strategy.
 
**What We're Solving For:**

* Opening a deployed tower's detail modal

* Cycling through targeting options using the targeting button

* Verifying the text correctly cycles through all targeting states
 
---
 
### Test 5: Upgrade Path Branching Logic
 
**What We're Testing:**

Understanding game logic restrictions when selecting upgrade configurations.
 
**Why It Matters:**

Towers can only upgrade deeply in two of three paths—the third path locks after certain thresholds.
 
**What We're Solving For:**

* Purchasing upgrades across multiple paths

* Recognizing when Path 3 becomes locked (padlock icon appears)

* Avoiding wasted actions trying to upgrade locked paths
 
---
 
### Test 6: Battle Speed Toggle
 
**What We're Testing:**

Interacting with UI speed multipliers during active combat.
 
**Why It Matters:**

Players need to speed up waves to progress faster through testing scenarios.
 
**What We're Solving For:**

* Tapping the play button to start a wave

* Activating 3x fast-forward speed mid-combat

* Confirming the button icon updates and game speed increases
 
---
 
### Test 7: Cooldown Ability Synchronization
 
**What We're Testing:**

Identifying dynamic targets and activating hero abilities at the right moment.
 
**Why It Matters:**

Timing hero abilities correctly is crucial for defeating large threats like M.O.A.B. blimps.
 
**What We're Solving For:**

* Detecting when a large blimp enters the map

* Activating a hero's special ability at the optimal moment

* Confirming the ability icon shows a cooldown overlay and the effect activates
 
---
 
### Test 8: Micro-Management Re-Sell Infrastructure
 
**What We're Testing:**

High-speed tower selling and rebuilding strategies.
 
**Why It Matters:**

Elite strategies require quickly selling and replacing towers to adapt to different wave types.
 
**What We're Solving For:**

* Executing rapid multi-tap sequences (select tower → sell → place new tower)

* Placing a replacement tower in the exact same footprint

* Confirming cash reserves update and the new tower is successfully placed
 
---
 
## Section 3: Exception Handling & Edge Cases
 
### Test 9: Defeat Modal Interaction
 
**What We're Testing:**

Recovery behavior when the game transitions to a fail state.
 
**Why It Matters:**

The agent must handle defeat screens gracefully and restart tests without crashing.
 
**What We're Solving For:**

* Recognizing the "Defeat" game-over screen

* Selecting the "Restart" option to reload the map

* Confirming the game reloads with full base health restored
 
---
 
### Test 10: System Update Notification Handling
 
**What We're Testing:**

Handling unexpected system-level notifications that block the screen.
 
**Why It Matters:**

Update notifications and system alerts shouldn't cause the agent to hang or fail.
 
**What We're Solving For:**

* Detecting non-gameplay notification overlays ("New Version Available")

* Finding and clicking the "Close" or "Later" button

* Resuming the test sequence without script failure
