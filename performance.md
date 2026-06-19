# Netflix Games Performance Test Cases
 
These metrics help us ensure players get a smooth, lag-free gaming experience across all devices.
 
## Test Case Glossary
 
1. FPS (Frames Per Second)

2. Frame Time Standard Deviation

3. Jank / Stutter Count

4. CPU Utilization Percentage

5. GPU Utilization Percentage

6. Application RAM Usage
 
---
 
## Core Performance Metrics
 
Your platform should capture hardware performance data during standard 10-minute automated gameplay sessions.
 
### Test 1: FPS (Frames Per Second)
 
**What We're Measuring:**

How smoothly the game runs by counting total frames divided by total time (in seconds).
 
**Why It Matters:**

This tells us if the game feels fluid and responsive on different devices.
 
**What We're Solving For:**

* Making sure your agent can count frames accurately across different rendering systems

* Keeping measurement windows consistent so results are comparable
 
---
 
### Test 2: Frame Time Standard Deviation
 
**What We're Measuring:**

How much frame delivery time varies (using standard deviation).
 
**Why It Matters:**

This helps us catch micro-stutters and timing issues that make games feel jerky.
 
**What We're Solving For:**

* Capturing precise timing for each frame

* Making sure your agent can spot the difference between normal frame fluctuations and real glitches that hurt gameplay
 
---
 
### Test 3: Jank / Stutter Count
 
**What We're Measuring:**

How many times frame delivery takes longer than our threshold (in milliseconds).
 
**Why It Matters:**

This catches the obvious visual hiccups that players actually notice.
 
**What We're Solving For:**

* Setting the right threshold for different types of games (fast-action vs. slow-paced)

* Connecting frame time spikes with issues that players can actually see
 
---
 
### Test 4: CPU Utilization Percentage
 
**What We're Measuring:**

Total CPU time divided by (number of cores × duration) × 100.
 
**Why It Matters:**

This shows us if the game is pushing the processor too hard or hitting bottlenecks.
 
**What We're Solving For:**

* Handling games that use multiple CPU threads at once

* Comparing results fairly across different processor types
 
---
 
### Test 5: GPU Utilization Percentage
 
**What We're Measuring:**

Active GPU time divided by total session time × 100.
 
**Why It Matters:**

This tells us if the graphics card is healthy or overheating under stress.
 
**What We're Solving For:**

* Capturing GPU data across different brands (NVIDIA, AMD, Intel)

* Tracking power use and thermal throttling that can slow down performance
 
---
 
### Test 6: Application RAM Usage
 
**What We're Measuring:**

Proportional Set Size (PSS) in megabytes.
 
**Why It Matters:**

This helps us catch memory leaks before the game runs out of RAM and crashes.
 
**What We're Solving For:**

* Telling the difference between normal memory usage and actual leaks

* Watching how memory grows during long gaming sessions
 
---
 
## Optional Extensions (Network Performance)
 
The following optional metrics can be captured for games with significant network requirements:
 
* **Average Download Rate:** Measured in Mbps to benchmark core asset distribution efficiency.

* **Ping / Jitter:** Round-trip latency and variation tracking to score multiplayer responsiveness.

* **Packet Loss & Connection Stability:** Dropped packets and session uptime ratios to diagnose network drops.
