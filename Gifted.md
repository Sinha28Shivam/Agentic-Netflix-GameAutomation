# Netflix Is A Joke Presents: Gifted Gameplay Test Cases
 
**Gifted** is an 18+ cloud-based party game where up to 9 players use smartphones as controllers to search for GIFs, submit captions, and vote on meme matchups displayed on a TV or browser. These tests validate an AI agent's ability to handle asynchronous dual-device interactions, real-time voting, and dynamic media searches.
 
## Test Case Glossary
 
1. Cross-Screen Room Sync via QR Code

2. Player Customization Interface

3. Keyword Search & Text Clear

4. Scrolling Live Media Grids

5. Meme Submission Multi-Action Sequence

6. Real-Time Vote Cast

7. Timer Expiration Handling

8. Adult Filter Content Block Detection

9. Dynamic Disconnect Recovery

10. Scoreboard Dashboard Verification
 
---
 
## Section 1: Connection & Lobby Navigation
 
### Test 1: Cross-Screen Room Sync via QR Code
 
**What We're Testing:**

Using the controller device's camera to read a TV room code and join the lobby.
 
**Why It Matters:**

This validates the agent can establish the critical connection between the mobile controller and the main display.
 
**What We're Solving For:**

* Aligning the mobile camera frame over the main screen's QR code

* Using OCR fallback to manually type the 4-digit code if QR scanning fails

* Confirming the controller transitions to the "In Lobby" screen
 
---
 
### Test 2: Player Customization Interface
 
**What We're Testing:**

Interacting with text entry fields and carousel avatar menus.
 
**Why It Matters:**

Players need to customize their profile before joining a game, testing basic input capabilities.
 
**What We're Solving For:**

* Tapping and typing into the "Enter Nickname" text field

* Swiping left and right on the avatar selection wheel

* Confirming the lobby host screen updates with the chosen name and avatar
 
---
 
## Section 2: GIPHY Search & Media Selection
 
### Test 3: Keyword Search & Text Clear
 
**What We're Testing:**

Executing keyword queries against the GIPHY database and clearing mistakes.
 
**Why It Matters:**

Search is the primary way players find GIFs, so accurate typing and error correction are essential.
 
**What We're Solving For:**

* Inputting search terms into the search field

* Spotting and tapping the small "X" delete icon to clear the field

* Confirming the search field restores the default placeholder text
 
---
 
### Test 4: Scrolling Live Media Grids
 
**What We're Testing:**

Loading and scrolling through infinite visual media columns without crashing.
 
**Why It Matters:**

GIF grids load dynamically from the cloud, requiring smooth scrolling and rendering.
 
**What We're Solving For:**

* Executing repetitive vertical drag gestures to load lower rows

* Confirming thumbnails have fully rendered before selection

* Successfully scrolling through at least 3 rows of fresh GIFs
 
---
 
## Section 3: Game Mechanics & Submissions
 
### Test 5: Meme Submission Multi-Action Sequence
 
**What We're Testing:**

Completing a tiered submission process (Pick GIF + Write Caption) before the countdown expires.
 
**Why It Matters:**

This is the core gameplay loop requiring coordinated actions under time pressure.
 
**What We're Solving For:**

* Tapping a chosen GIF block to lock it in

* Detecting the "Add a caption" prompt and typing a phrase

* Locating and hitting the "Submit" button before the timer runs out
 
---
 
### Test 6: Real-Time Vote Cast
 
**What We're Testing:**

Making a clean decision during a split-screen voting phase.
 
**Why It Matters:**

Voting requires comparing content on the main display and tapping the choice on the phone quickly.
 
**What We're Solving For:**

* Watching the main TV display to compare Meme A vs Meme B

* Tapping either the "Left Choice" or "Right Choice" button on the smartphone

* Confirming the vote registers with a visual/haptic cue
 
---
 
## Section 4: Edge Cases & Network Handling
 
### Test 7: Timer Expiration Handling
 
**What We're Testing:**

The agent's behavior when it fails to act before the timer reaches zero.
 
**Why It Matters:**

Timeout scenarios shouldn't crash the agent—it should gracefully transition to spectator mode.
 
**What We're Solving For:**

* Tracking the countdown timer on the TV screen visually

* Handling sudden UI state changes when the phase times out

* Transitioning to spectator mode without throwing errors
 
---
 
### Test 8: Adult Filter Content Block Detection
 
**What We're Testing:**

Recognizing blocked or broken GIPHY assets and selecting alternatives.
 
**Why It Matters:**

Adult content filters may replace GIFs with grey placeholder blocks that shouldn't be submitted.
 
**What We're Solving For:**

* Spotting generic grey placeholder thumbnails

* Avoiding the blocked asset and choosing an adjacent working GIF

* Successfully submitting a fully rendered asset
 
---
 
### Test 9: Dynamic Disconnect Recovery
 
**What We're Testing:**

Handling temporary loss of socket connectivity mid-round.
 
**Why It Matters:**

Network interruptions are common in party games and need graceful recovery.
 
**What We're Solving For:**

* Recognizing a "Connection Interrupted" overlay modal

* Clicking the "Reconnect" or "Refresh Session" button

* Successfully syncing back to the current active turn state
 
---
 
### Test 10: Scoreboard Dashboard Verification
 
**What We're Testing:**

Processing final reward screens and interacting with post-game menus.
 
**Why It Matters:**

End-of-game flows validate the agent can complete the full game lifecycle.
 
**What We're Solving For:**

* Reading the final scoreboard ranking chart on the TV display

* Clicking the "Play Again" button on the mobile screen

* Confirming the lobby resets to an empty room state
