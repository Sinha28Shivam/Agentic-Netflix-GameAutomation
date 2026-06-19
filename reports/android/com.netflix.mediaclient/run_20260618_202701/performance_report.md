# Netflix Games Performance Compliance Report

This report summarizes hardware resource utilization and visual pacing compliance captured during the automation session.

## Summary Status

> [!TIP]
> **Performance Healthy!** All hardware metrics fall within standard compliance ranges.

## Telemetry Metadata
* **Platform:** ANDROID
* **OS Version:** 13
* **Device Info:** Xiaomi M2101K6P
* **Target Package:** `com.netflix.mediaclient`
* **Session Duration:** 58.75 seconds
* **Sample Points:** 31

---

## Hardware Telemetry Performance

### Resource Utilization

| Metric | Session Average | Session Peak | Compliance Limit | Status |
| :--- | :---: | :---: | :---: | :---: |
| **CPU Utilization** | 5.4% | 5.4% | < 80.0% | PASS |
| **GPU Utilization** | 18.0% | 18.0% | < 90.0% | PASS |
| **RAM Footprint (PSS)** | 203.84 MB | 228.2 MB | < 500.0 MB | PASS |

### Rendering & Frame Pacing

| Metric | Target / Average Value | compliance Limit / Threshold | Status |
| :--- | :---: | :---: | :---: |
| **Average FPS** | 58.57 FPS | > 55.0 FPS | PASS |
| **Minimum FPS** | 57.65 FPS | > 30.0 FPS | PASS |
| **5th Percentile FPS** | 57.68 FPS | > 45.0 FPS | PASS |
| **Total Jank Stutters** | 8 | < 15 per minute | PASS |
| **Pacing Std Deviation** | 2.5 ms | < 5.0 ms | PASS |

### Network Telemetry (Optional Extensions)

| Metric | Average Value | Status |
| :--- | :---: | :---: |
| **Connection Ping** | 27.27 ms | HEALTHY |
| **Download Throughput** | 64.45 Mbps | ACTIVE |
| **Packet Loss** | 0.0% | CLEAR |

---

## File Registry
* **Raw telemetry log (CSV):** [performance_report.csv](file:///C:/Users/sinha/Desktop/All_POC/Python_Netflix/reports/android/com.netflix.mediaclient/run_20260618_202701/performance_report.csv)
* **Aggregated summary data (JSON):** [performance_report.json](file:///C:/Users/sinha/Desktop/All_POC/Python_Netflix/reports/android/com.netflix.mediaclient/run_20260618_202701/performance_report.json)
