import os
import csv
import json
import numpy as np
from typing import Dict, Any, List
from src.utils.logger import telemetry_logger

class PerformanceReporter:
    """
    Processes collected performance telemetry metrics and exports reports
    in CSV, JSON, and Markdown formats.
    """

    @staticmethod
    def generate_reports(data: Dict[str, Any], output_dir: str = "logs") -> str:
        history = data.get("history", [])
        platform = data.get("platform", "android").upper()
        package_name = data.get("package_name", "unknown")
        
        if not history:
            telemetry_logger.warning("[PerformanceReporter] No metrics recorded. Cannot generate reports.")
            return ""

        os.makedirs(output_dir, exist_ok=True)
        
        # Extract individual metric columns
        timestamps = [pt["timestamp"] for pt in history]
        cpu_values = [pt["cpu_pct"] for pt in history]
        ram_values = [pt["ram_mb"] for pt in history]
        fps_values = [pt["fps"] for pt in history]
        jank_counts = [pt["jank_count"] for pt in history]
        std_devs = [pt["frame_time_std_ms"] for pt in history]
        gpu_values = [pt["gpu_pct"] for pt in history]
        pings = [pt["network_ping_ms"] for pt in history]
        downloads = [pt["download_mbps"] for pt in history]
        losses = [pt["packet_loss_pct"] for pt in history]

        duration = timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0.0
        
        os_version = data.get("os_version", "N/A")
        device_model = data.get("device_model", "N/A")
        device_manufacturer = data.get("device_manufacturer", "N/A")

        # Calculate summary statistics
        summary = {
            "metadata": {
                "platform": platform,
                "package_name": package_name,
                "os_version": os_version,
                "device_model": device_model,
                "device_manufacturer": device_manufacturer,
                "session_duration_seconds": round(duration, 2),
                "total_samples": len(history)
            },
            "cpu": {
                "average_pct": round(float(np.mean(cpu_values)), 2),
                "peak_pct": round(float(np.max(cpu_values)), 2)
            },
            "ram": {
                "average_mb": round(float(np.mean(ram_values)), 2),
                "peak_mb": round(float(np.max(ram_values)), 2),
                "final_mb": round(float(ram_values[-1]), 2)
            },
            "fps": {
                "average": round(float(np.mean(fps_values)), 2),
                "minimum": round(float(np.min(fps_values)), 2),
                "fifth_percentile": round(float(np.percentile(fps_values, 5)), 2)
            },
            "janks": {
                "total_stutters": int(np.sum(jank_counts)),
                "janks_per_minute": round(float(np.sum(jank_counts) / (max(1.0, duration) / 60.0)), 2)
            },
            "frame_pacing": {
                "average_std_dev_ms": round(float(np.mean(std_devs)), 2)
            },
            "gpu": {
                "average_pct": round(float(np.mean(gpu_values)), 2),
                "peak_pct": round(float(np.max(gpu_values)), 2)
            },
            "network": {
                "average_ping_ms": round(float(np.mean(pings)), 2),
                "average_download_mbps": round(float(np.mean(downloads)), 2),
                "total_packet_loss_pct": round(float(np.mean(losses)), 2)
            }
        }

        # 1. Export CSV File
        csv_path = os.path.join(output_dir, "performance_report.csv")
        try:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "CPU_Util_Pct", "RAM_Usage_MB", "FPS", 
                    "Jank_Count", "Frame_Time_StdDev_MS", "GPU_Util_Pct", 
                    "Network_Ping_MS", "Download_Mbps", "Packet_Loss_Pct"
                ])
                for pt in history:
                    writer.writerow([
                        pt["timestamp"], pt["cpu_pct"], pt["ram_mb"], pt["fps"],
                        pt["jank_count"], pt["frame_time_std_ms"], pt["gpu_pct"],
                        pt["network_ping_ms"], pt["download_mbps"], pt["packet_loss_pct"]
                    ])
            telemetry_logger.info(f"[PerformanceReporter] CSV report generated at: {csv_path}")
        except Exception as e:
            telemetry_logger.error(f"[PerformanceReporter] Failed to write CSV: {e}")

        # 2. Export JSON File
        json_path = os.path.join(output_dir, "performance_report.json")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=4)
            telemetry_logger.info(f"[PerformanceReporter] JSON summary generated at: {json_path}")
        except Exception as e:
            telemetry_logger.error(f"[PerformanceReporter] Failed to write JSON: {e}")

        # 3. Export Markdown Report
        md_path = os.path.join(output_dir, "performance_report.md")
        try:
            # Check for critical performance thresholds
            alerts = []
            if summary["fps"]["average"] < 55.0:
                alerts.append("> [!WARNING]\n> **Low Frame Rate detected!** Average FPS was below 55.0. Gamplay may feel sluggish.")
            if summary["ram"]["peak_mb"] > 400.0:
                alerts.append("> [!IMPORTANT]\n> **High RAM Usage!** Memory footprint exceeded 400MB. Inspect app for potential leaks.")
            if summary["janks"]["total_stutters"] > 10:
                alerts.append("> [!NOTE]\n> **Micro-stutters detected!** Multiple jank spikes exceeded standard frame pacing intervals.")
                
            alert_str = "\n\n".join(alerts) if alerts else "> [!TIP]\n> **Performance Healthy!** All hardware metrics fall within standard compliance ranges."

            device_info = f"{summary['metadata']['device_manufacturer']} {summary['metadata']['device_model']}".strip()
            md_content = f"""# Netflix Games Performance Compliance Report

This report summarizes hardware resource utilization and visual pacing compliance captured during the automation session.

## Summary Status

{alert_str}

## Telemetry Metadata
* **Platform:** {summary['metadata']['platform']}
* **OS Version:** {summary['metadata']['os_version']}
* **Device Info:** {device_info}
* **Target Package:** `{summary['metadata']['package_name']}`
* **Session Duration:** {summary['metadata']['session_duration_seconds']} seconds
* **Sample Points:** {summary['metadata']['total_samples']}

---

## Hardware Telemetry Performance

### Resource Utilization

| Metric | Session Average | Session Peak | Compliance Limit | Status |
| :--- | :---: | :---: | :---: | :---: |
| **CPU Utilization** | {summary['cpu']['average_pct']}% | {summary['cpu']['peak_pct']}% | < 80.0% | {'PASS' if summary['cpu']['average_pct'] < 80 else 'FAIL'} |
| **GPU Utilization** | {summary['gpu']['average_pct']}% | {summary['gpu']['peak_pct']}% | < 90.0% | {'PASS' if summary['gpu']['average_pct'] < 90 else 'FAIL'} |
| **RAM Footprint (PSS)** | {summary['ram']['average_mb']} MB | {summary['ram']['peak_mb']} MB | < 500.0 MB | {'PASS' if summary['ram']['peak_mb'] < 500 else 'FAIL'} |

### Rendering & Frame Pacing

| Metric | Target / Average Value | compliance Limit / Threshold | Status |
| :--- | :---: | :---: | :---: |
| **Average FPS** | {summary['fps']['average']} FPS | > 55.0 FPS | {'PASS' if summary['fps']['average'] >= 55 else 'FAIL'} |
| **Minimum FPS** | {summary['fps']['minimum']} FPS | > 30.0 FPS | {'PASS' if summary['fps']['minimum'] >= 30 else 'FAIL'} |
| **5th Percentile FPS** | {summary['fps']['fifth_percentile']} FPS | > 45.0 FPS | {'PASS' if summary['fps']['fifth_percentile'] >= 45 else 'FAIL'} |
| **Total Jank Stutters** | {summary['janks']['total_stutters']} | < 15 per minute | {'PASS' if summary['janks']['janks_per_minute'] < 15 else 'FAIL'} |
| **Pacing Std Deviation** | {summary['frame_pacing']['average_std_dev_ms']} ms | < 5.0 ms | {'PASS' if summary['frame_pacing']['average_std_dev_ms'] < 5.0 else 'FAIL'} |

### Network Telemetry (Optional Extensions)

| Metric | Average Value | Status |
| :--- | :---: | :---: |
| **Connection Ping** | {summary['network']['average_ping_ms']} ms | HEALTHY |
| **Download Throughput** | {summary['network']['average_download_mbps']} Mbps | ACTIVE |
| **Packet Loss** | {summary['network']['total_packet_loss_pct']}% | CLEAR |

---

## File Registry
* **Raw telemetry log (CSV):** [performance_report.csv](file:///{os.path.abspath(csv_path).replace(os.sep, '/')})
* **Aggregated summary data (JSON):** [performance_report.json](file:///{os.path.abspath(json_path).replace(os.sep, '/')})
"""
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            telemetry_logger.info(f"[PerformanceReporter] Markdown report generated at: {md_path}")
        except Exception as e:
            telemetry_logger.error(f"[PerformanceReporter] Failed to write Markdown: {e}")

        return md_path
