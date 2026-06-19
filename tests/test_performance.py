import os
import json
import csv
import pytest
from PIL import Image
from src.utils.performance_reporter import PerformanceReporter

def test_performance_reporter_calculations(tmp_path):
    # Setup mock performance history
    mock_history = [
        {
            "timestamp": 1000.0,
            "cpu_pct": 20.0,
            "ram_mb": 150.0,
            "fps": 60.0,
            "jank_count": 0,
            "frame_time_std_ms": 2.0,
            "gpu_pct": 15.0,
            "network_ping_ms": 20.0,
            "download_mbps": 50.0,
            "packet_loss_pct": 0.0
        },
        {
            "timestamp": 1001.0,
            "cpu_pct": 30.0,
            "ram_mb": 160.0,
            "fps": 55.0,
            "jank_count": 2,
            "frame_time_std_ms": 5.0,
            "gpu_pct": 25.0,
            "network_ping_ms": 24.0,
            "download_mbps": 48.0,
            "packet_loss_pct": 0.0
        },
        {
            "timestamp": 1002.0,
            "cpu_pct": 40.0,
            "ram_mb": 170.0,
            "fps": 30.0,
            "jank_count": 5,
            "frame_time_std_ms": 12.0,
            "gpu_pct": 35.0,
            "network_ping_ms": 30.0,
            "download_mbps": 40.0,
            "packet_loss_pct": 0.0
        }
    ]

    mock_data = {
        "platform": "android",
        "package_name": "com.netflix.NGP.Snakeio",
        "history": mock_history
    }

    # Generate reports in temporary folder
    output_dir = str(tmp_path)
    md_report_path = PerformanceReporter.generate_reports(mock_data, output_dir=output_dir)

    # 1. Verify files are created
    csv_path = os.path.join(output_dir, "performance_report.csv")
    json_path = os.path.join(output_dir, "performance_report.json")
    md_path = os.path.join(output_dir, "performance_report.md")

    assert os.path.exists(csv_path)
    assert os.path.exists(json_path)
    assert os.path.exists(md_path)
    assert md_report_path == md_path

    # 2. Verify JSON calculation logic
    with open(json_path, "r") as f:
        summary = json.load(f)

    # Duration = 1002 - 1000 = 2 seconds
    assert summary["metadata"]["session_duration_seconds"] == 2.0
    assert summary["metadata"]["total_samples"] == 3

    # CPU average = (20 + 30 + 40) / 3 = 30.0%
    assert summary["cpu"]["average_pct"] == 30.0
    assert summary["cpu"]["peak_pct"] == 40.0

    # RAM average = (150 + 160 + 170) / 3 = 160.0MB
    assert summary["ram"]["average_mb"] == 160.0
    assert summary["ram"]["peak_mb"] == 170.0
    assert summary["ram"]["final_mb"] == 170.0

    # FPS average = (60 + 55 + 30) / 3 = 48.33
    assert summary["fps"]["average"] == 48.33
    assert summary["fps"]["minimum"] == 30.0

    # Jank calculations
    assert summary["janks"]["total_stutters"] == 7
    # 7 janks in 2 seconds = 7 * 30 = 210 janks/minute
    assert summary["janks"]["janks_per_minute"] == 210.0

    # 3. Verify CSV formatting
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert "CPU_Util_Pct" in headers
        assert "RAM_Usage_MB" in headers
        
        row1 = next(reader)
        assert float(row1[1]) == 20.0  # cpu_pct
        assert float(row1[2]) == 150.0 # ram_mb

    # 4. Verify Markdown report contains keys
    with open(md_path, "r") as f:
        md_text = f.read()
        assert "Netflix Games Performance Compliance Report" in md_text
        assert "Sample Points:" in md_text
        assert "Average FPS" in md_text
        assert "Total Jank Stutters" in md_text
