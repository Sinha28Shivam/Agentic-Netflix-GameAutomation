# Into the Breach Gameplay Test Cases
 
**Into the Breach** is a turn-based tactical strategy game where players command mechs to defend cities from alien Vek attacks. These tests validate an AI agent's spatial reasoning, tactical logic, grid-based combat mechanics, and ability to read and respond to complex board states.
 
## Test Case Glossary
 
1. Netflix Account Handshake & Profile Selection

2. Settings UI Scroll and Toggle

3. Enemy Intent Identification via Long-Press

4. Undo Move Safety Valve

5. Reset Turn Emergency Protocol

6. Single-Target Melee Attack Execution

7. Environmental Kill via Push Mechanics

8. Threat Intercept via Block Mitigation

9. Dynamic Hazard Interruption Handling

10. Weapon Sub-System Power Upgrade
 
---
 
## Section 1: Main Menu & Configuration
 
### Test 1: Netflix Account Handshake & Profile Selection
 
**What We're Testing:**

Navigating the external Netflix OAuth/Profile layer to access the game.
 
**Why It Matters:**

This confirms the agent can handle the Netflix authentication flow before reaching the game.
 
**What We're Solving For:**

* Identifying the Netflix profile grid using OCR and object detection

* Tapping the correct target profile avatar

* Confirming the main title screen loads successfully
 
---
 
### Test 2: Settings UI Scroll and Toggle
 
**What We're Testing:**

Interacting with standard mobile scroll views and slider components.
 
**Why It Matters:**

Settings validation ensures the agent can handle basic UI controls like sliders and checkboxes.
 
**What We're Solving For:**

* Dragging the "Sound Volume" slider to 0%

* Scrolling down a menu to reveal hidden settings

* Tapping the "Grid Coordinates" checkbox to turn it ON
 
---
 
## Section 2: Combat Grid Mechanics
 
### Test 3: Enemy Intent Identification via Long-Press
 
**What We're Testing:**

Inspecting enemy state to parse upcoming attack vectors.
 
**Why It Matters:**

Understanding enemy threats is fundamental to making strategic decisions.
 
**What We're Solving For:**

* Using long-press gesture on a specific Vek alien tile

* Reading the orange threat matrix overlay

* Detecting which building the Vek is targeting
 
---
 
### Test 4: Undo Move Safety Valve
 
**What We're Testing:**

Executing a physical movement and successfully rolling it back before committing.
 
**Why It Matters:**

The undo feature allows experimentation without penalty—critical for agent learning.
 
**What We're Solving For:**

* Tapping a Mech and moving it to an adjacent tile

* Recognizing the "Undo Move" button appears

* Tapping "Undo Move" to revert the position
 
---
 
### Test 5: Reset Turn Emergency Protocol
 
**What We're Testing:**

Handling a once-per-battle full turn state reset.
 
**Why It Matters:**

This is a critical safety feature for recovering from strategic mistakes.
 
**What We're Solving For:**

* Executing multiple mech movements and attacks

* Accessing the in-game menu and selecting "Reset Turn"

* Confirming the game reloads to the beginning of the player's turn
 
---
 
## Section 3: Tactical Execution & Combat
 
### Test 6: Single-Target Melee Attack Execution
 
**What We're Testing:**

Selecting a weapon and executing a targeted combat action.
 
**Why It Matters:**

Basic attack execution is the foundation of all combat interactions.
 
**What We're Solving For:**

* Tapping the Combat Mech to select it

* Tapping the "Titan Fist" weapon card icon

* Tapping an adjacent Vek target to confirm the punch
 
---
 
### Test 7: Environmental Kill via Push Mechanics
 
**What We're Testing:**

Higher-level tactical reasoning using the environment to instantly kill enemies.
 
**Why It Matters:**

Environmental kills demonstrate strategic understanding beyond basic attacks.
 
**What We're Solving For:**

* Identifying that pushing a Vek into water causes instant death

* Moving a Mech into position to execute a push attack

* Confirming the Vek drowns and is removed from the field
 
---
 
### Test 8: Threat Intercept via Block Mitigation
 
**What We're Testing:**

Intentionally sacrificing mech health to shield a high-value asset.
 
**Why It Matters:**

This tests value-based decision making and defensive positioning.
 
**What We're Solving For:**

* Deciding to take damage on a Mech to protect a civilian building

* Moving a Mech directly into the line of fire

* Confirming the Mech blocks the attack trajectory successfully
 
---
 
## Section 4: Edge Cases & Advanced Mechanics
 
### Test 9: Dynamic Hazard Interruption Handling
 
**What We're Testing:**

Processing automated board changes and updating the mental state model.
 
**Why It Matters:**

The agent must wait for enemy turns to complete and recognize new hazards that appear.
 
**What We're Solving For:**

* Stopping actions during the AI Vek turn animations

* Watching for active tile changes (mountains collapsing, fire spreading)

* Registering the start of Player Turn 2 without timeout errors
 
---
 
### Test 10: Weapon Sub-System Power Upgrade
 
**What We're Testing:**

Navigating complex menu overlays to allocate upgrade resources.
 
**Why It Matters:**

Between-mission upgrades are critical for progression and require precise UI navigation.
 
**What We're Solving For:**

* Tapping the Mech Upgrade tab from the strategic map

* Selecting a specific weapon to upgrade

* Dragging a "Reactor Core" into an empty power slot and confirming the upgrade
