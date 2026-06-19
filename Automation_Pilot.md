# Netflix Games Agentic Test Automation Pilot

## Program Overview Document
 
**Program Duration:** 2–4 weeks  

**Document Version:** 1.0  

**Last Updated:** June 15, 2026
 
---
 
## Executive Summary
 
This pilot helps us explore how effectively your platform can autonomously test Netflix games across multiple dimensions—compliance, performance, and gameplay. Our ultimate goal is to find a long-term partner to help us scale AI-driven QA and deliver better gaming experiences to our players.
 
---
 
## 1. Scope & Execution Strategy
 
### 1.1 Games Under Test

The pilot evaluates three selected Netflix games representing a balanced spectrum of visual perspectives and interaction speeds.
 
### 1.2 Test Suite Composition

A total of 30 test cases will be sourced and categorized as follows:
 
| Test Category | Count | Test Plan | Primary Validation Focus |

| :--- | :---: | :--- | :--- |

| **Compliance** | 10 | `Compliance.md` | SDK specifications, platform standards, and branding guidelines. |

| **Compatibility & Performance** | 10 | `Comp.md` | Technical telemetry (FPS, CPU/GPU utilization, memory, battery, load times). |

| **Gameplay** | 10 | `GameXYZ.Plan.md` | Complex game mechanics, visual perspectives, and multiplayer functionality. |
 
### 1.3 Testing Matrix & Run Configurations

The pilot expands its execution scope across cross-platform environments using the following criteria:

* **Dimensions:** 3 Games × 30 Tests across (Cloud/Web) and Mobile (Android, iOS) backends.

* **Display Variables:** Two distinct mobile resolutions and two browser window sizes.

* **Modes:** Single-player and cross-platform multiplayer (Cloud/Web + Android + iOS).
 
#### Standard Run Configurations

* **Cloud/Web:** Game client paired with Google Chrome or Apple Safari.

* **Mobile:** Game client executed natively on Android or iOS hardware.

* **Multiplayer Matrix:** Game + ( Chrome | Safari ) + Android + iOS
 
### 1.4 Execution Optimization Strategy (How We Fine-Tune Results)
 
To improve agent accuracy and refine test prompts, we'll run tests through a 5-pass cycle (theoretically, realizing there would be several sub-iterations and tangential explorations along this general direction):
 
1. **Pass 1: Full Test Run** → Establish baseline results across the complete test matrix

2. **Pass 2: Full Test Run** → Generate comparison data and identify anomalies

3. **Pass 3: Targeted Retest** → Focus only on tests that showed differences or false positives

4. **Pass 4: Verification** → Confirm that test adjustments are working

5. **Pass 5: Final Full Run** → Validate stability across the entire test suite
 
### 1.5 Estimated Telemetry and Test Volumes

Each game title is estimated to baseline a test pass of **120 test results**, structured around the following parameters:

* **Single-Player Execution:** 1 Game × 30 Tests = 30 Results.

* **Multiplayer Execution:** 1 Game × 30 Tests × 2 Browsers × 2 Devices = 120 Results.

* **Performance Baseline Runs:** 10 minutes of active gameplay initiated from a standard account starting point.

  * *Single Player:* 1 Game × 2 Devices × 2 Runs = 40 Total Minutes.

  * *Multiplayer:* 1 Game × 3 Devices × 1 Run = 30 Total Minutes.
 
---
 
## 2. Test Requirements & Validation Guidelines
 
### 2.1 Compliance Validations

Compliance tests evaluate adherence to Netflix Games Requirements & Guidelines (GRNs), ensuring uniform branding and foundational technical stability.
 
#### Compliance Test Cases
 
1. **Latest SDK Version Verification** - Validates that games use the most current Netflix SDK version through internal infrastructure verification.

2. **Netflix Launch Screen Presence** - Ensures games launch directly into the branded splash screen with proper timing.

3. **Launch Screen Display Duration** - Measures and validates that the launch screen displays for exactly 2000ms without interruption.

4. **Netflix Button Placement** - Confirms UI asset positioning remains anchored to exact display corners across adaptive menus.

5. **Gameplay Pause on Netflix Menu** - Verifies that gameplay suspends immediately when the Netflix system overlay opens.

6. **Profile Language Respect** - Ensures user-profile language mapping loads accurately for each individual profile.

7. **Cloud Gaming Settings Restrictions** - Verifies restricted configuration choices remain hidden from local game menus.

8. **Game Menu Button Functionality** - Confirms explicit physical/virtual buttons execute both opening and closing operations for standard pause panels.

9. **QR Code Display Validation** - Validates that the initial QR code screen displays exactly one target code without duplicates.
 
For detailed test requirements and methodologies, refer to the [Compliance Test Cases](Compliance.md) document.
 
### 2.2 Compatibility & Performance Telemetry
 
Your platform should capture hardware performance data during standard 10-minute gameplay sessions.
 
#### Performance Test Cases
 
1. **FPS (Frames Per Second)** - Benchmarks general runtime fluidness across target specifications using frame count over time.

2. **Frame Time Standard Deviation** - Identifies micro-stutters and engine pacing discrepancies through delivery time variance analysis.

3. **Jank / Stutter Count** - Isolates explicit visual performance anomalies by counting frame time threshold violations.

4. **CPU Utilization Percentage** - Gauges core computational workload and hardware bottlenecks through normalized CPU time measurement.

5. **GPU Utilization Percentage** - Assesses rendering pipeline health and thermal stress via active GPU time tracking.

6. **Application RAM Usage** - Detects system memory leaks and operational threshold breaches using Proportional Set Size metrics.
 
#### Optional Network Performance Extensions
 
* **Average Download Rate:** Measured in Mbps to benchmark core asset distribution efficiency.

* **Ping / Jitter:** Round-trip latency and variation tracking to score multiplayer responsiveness.

* **Packet Loss & Connection Stability:** Dropped packets and session uptime ratios to diagnose network drops.
 
For detailed test requirements and methodologies, refer to the [Performance Test Cases](Performance.md) document.
 
---
 
## 3. How We'll Evaluate Your Platform
 
### 3.1 Scoring Framework
 
We'll grade your platform across 7 key areas using a 1-to-10 scale. Each category has a weight that reflects its importance to our goals.
 
**Overall Score** = (Reach × 0.15) + (Extensibility × 0.20) + (Scale × 0.15) + (Suitability × 0.15) + (Actionability × 0.15) + (Impact × 0.10) + (Cost × 0.10)
 
**What Your Score Means:**
 
* **8.5 - 10.0** → Strong fit! Let's move forward with enterprise deployment.

* **7.0 - 8.4** → Promising, but we'll need to address a few gaps before scaling.

* **5.0 - 6.9** → Interesting potential; let's extend the pilot to explore further.

* **< 5.0** → Not the right fit for our needs at this time.
 
### 3.2 Scoring Categories
 
#### Category 1: Reach (Weight: 15%)

*How broad are your testing capabilities?*
 
* **Compliance & Compatibility:** Can your platform handle our 10 automated compliance and performance checks flawlessly?

* **Gameplay Flexibility:** Does it work out-of-the-box with different game types (2D slow, 2D fast, 3D fast) without custom tweaking for each game?

* **Ease of Use:** Can our producers and manual testers run tests without needing developer help?
 
#### Category 2: Extensibility (Weight: 20%)

*How adaptable is your platform?*
 
* **Easy Customization & APIs:** Can we modify tests easily? Do you offer APIs for data integration and custom tooling?

* **Model Flexibility:** Can we switch between different AI models (GPT-4, Claude, Gemini, etc.) as needed?

* **Environment Support:** Does your platform work across our different environments (QA, Staging, Production) and global regions (Japan, Latin America, Europe)?
 
#### Category 3: Scale (Weight: 15%)

*Can your platform handle our volume?*
 
* **Parallel Execution:** Can it run 180 tests at the same time across different devices and browsers?

* **Speed:** Can it complete our full test matrix (1,620 test combinations) within reasonable time limits?

* **Cost Efficiency:** How well does it manage API usage, compute resources, and device farm allocation?
 
#### Category 4: Suitability (Weight: 15%)

*How well does it fit our environment?*
 
* **Infrastructure Compatibility:** Does it work with our device labs, internal clouds, and hardware setups?

* **Resilience:** Can it handle different game genres and camera types? Does it gracefully handle crashes or unstable alpha builds?
 
#### Category 5: Actionability (Weight: 15%)

*How useful are your test results?*
 
* **Clear Diagnostics:** Do test failures include logs, screenshots, and video recordings?

* **Easy Triage:** Can we quickly separate real bugs from AI mistakes? Can we re-run specific tests easily and create Jira tickets directly?
 
#### Category 6: Impact (Weight: 10%)

*What real value do we get?*
 
* **Bug Discovery:** How many real, critical issues does your platform catch?

* **Time Savings:** How much faster is it compared to manual testing?
 
#### Category 7: Cost (Weight: 10%)

*What's the total cost of ownership?*
 
* **All-In Pricing:** Total cost including AI model usage, licenses, setup, and ongoing maintenance.
 
---
 
## 4. Program Goals & Success Criteria
 
### 4.1 What Success Looks Like
 
We'll consider the pilot successful when we hit these benchmarks:
 
* **Autonomous Testing:** Your platform runs 20 basic tests without human help. *Target: ≥85% completion rate.*

* **Accuracy:** The AI correctly identifies pass/fail results. *Target: ≥90% agreement with manual QA.*

* **Bug Discovery:** Automated testing finds bugs as well as traditional methods. *Target: Find ≥80% of known issues plus at least 1 new bug.*

* **CI/CD Integration:** Testing fits smoothly into our build pipeline. *Target: Tests start within 5 minutes and finish within 15 minutes.*

* **Clean Data Output:** Results are easy to parse and include video evidence. *Target: 100% valid JSON/CSV with videos for ≥95% of failures.*

* **User-Friendly:** Anyone can run tests with minimal clicks. *Target: ≥90% success rate for one-click execution.*
 
### 4.2 Overall Pilot Success
 
We'll call the pilot a success if your platform:
 
1. Completes ≥80% of all scheduled test runs

2. Scores ≥7.0 on our evaluation framework

3. Finds at least 3 real bugs that manual QA missed
 
---
 
## 5. Timeline & Potential Roadblocks
 
### 5.1 Project Schedule
 
* **Week 1 (Setup):** Get your team access, set up infrastructure, and prepare test cases

* **Week 2 (Execution):** Run the full test matrix (1,620 total tests across 3 vendors, 3 games, 9 configs, 20 tests)

* **Week 3 (Validation):** Compare results with manual QA and identify real bugs

* **Week 4 (Assessment):** Compile final scores, gather feedback, and calculate total costs
 
### 5.2 Potential Roadblocks & How We'll Handle Them
 
| What Could Go Wrong | How Likely | Impact | How We'll Address It |

| :--- | :---: | :---: | :--- |

| **Platform Downtime** | Medium | High | • Run technical reviews before launch<br>• Set clear uptime requirements |

| **Too Many False Alarms** | High | Medium | • Add manual verification checkpoints<br>• Track precision and recall metrics |

| **Game Build Changes** | Low | Medium | • Freeze game updates during testing<br>• Document any emergency patches |

| **Not Enough Devices** | Medium | High | • Reserve dedicated testing devices<br>• Configure backup platforms |

| **AI Rate Limits** | Medium | Medium | • Negotiate higher API limits upfront<br>• Stagger test execution |

| **Data Format Mismatches** | Low | High | • Define data formats in Week 1<br>• Validate exports early |
 
---
 
## 6. Questions We're Exploring Together
 
* How quickly can we roll this out across Netflix Games if the pilot goes well?

* What's our budget for test execution (per-test and overall)?

* Can your platform run inside our secure, internal Netflix network? Can it use our lab? 

* Can we successfully extend your platform for our advanced testing operational and reporting needs?

* Will these scores factor into contract pricing discussions?
