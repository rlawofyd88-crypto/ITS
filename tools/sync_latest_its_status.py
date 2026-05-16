#!/usr/bin/env python3
"""Continuously export the newest CameraITS temp run into dashboard JSON."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from its_dashboard_adapter import summarize_results


def find_latest_cameraits_dir(temp_root: Path) -> Path | None:
    candidates = [p for p in temp_root.glob("CameraITS_*") if p.is_dir()]
    if not candidates:
      return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def write_status(output: Path, results_dir: Path | None) -> None:
    if results_dir is None:
        payload = {
            "status": "RUNNING",
            "updatedAt": time.time(),
            "metrics": {
                "overallScore": 0,
                "colorAccuracy": 0,
                "sharpness": 0,
                "exposure": 0,
            },
            "tests": {
                "colorAccuracy": 0,
                "resolution": 0,
                "dynamicRange": 0,
                "defectDetect": 0,
            },
            "source": "",
            "message": "Waiting for a CameraITS run to start.",
        }
    else:
        payload = summarize_results(results_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync newest CameraITS run to dashboard JSON.")
    parser.add_argument("--temp-root", default=os.environ.get("LOCALAPPDATA", "") + "\\Temp", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--interval", default=2.0, type=float)
    args = parser.parse_args()

    while True:
        latest = find_latest_cameraits_dir(args.temp_root)
        write_status(args.output, latest)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
