#!/usr/bin/env python3
"""Serve Google Camera ITS result summaries for the COEX dashboard.

The adapter watches a Camera ITS root directory, automatically picks the latest 
CameraITS_* folder, and exposes a compact JSON status endpoint.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

# 정규식 설정: SKIP 포함
PASS_RE = re.compile(r"\bPASS\b", re.IGNORECASE)
FAIL_RE = re.compile(r"\bFAIL\b", re.IGNORECASE)
SKIP_RE = re.compile(r"\bSKIP\b", re.IGNORECASE)
STATUS_LINE_RE = re.compile(r"^(PASS|FAIL|SKIP)\s+", re.IGNORECASE)


def clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def find_latest_cameraits_dir(results_dir: Path) -> Path | None:
    """루트 폴더에서 가장 최근에 수정된 CameraITS_ 폴더를 탐색"""
    candidates = [p for p in results_dir.glob("CameraITS_*") if p.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def find_text_files(results_dir: Path) -> list[Path]:
    patterns = ("*.txt", "*.log")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(results_dir.rglob(pattern))
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)[:80]


def score_from_counts(pass_count: int, fail_count: int) -> float:
    total = pass_count + fail_count
    if total == 0:
        return 0.0
    return clamp((pass_count / total) * 100.0)


def find_scene_summaries(results_dir: Path) -> list[Path]:
    return sorted(results_dir.rglob("scene_test_summary.txt"))


def summarize_scene_summaries(summary_files: list[Path], results_dir: Path) -> dict[str, Any]:
    pass_count = 0
    fail_count = 0
    skip_count = 0
    tests_by_metric: dict[str, dict[str, int]] = {
        "colorAccuracy": {"pass": 0, "fail": 0, "skip": 0},
        "resolution": {"pass": 0, "fail": 0, "skip": 0},
        "dynamicRange": {"pass": 0, "fail": 0, "skip": 0},
        "defectDetect": {"pass": 0, "fail": 0, "skip": 0},
    }

    metric_cycle = ("colorAccuracy", "resolution", "dynamicRange", "defectDetect")
    metric_index = 0

    for summary_file in summary_files:
        for line in summary_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            match = STATUS_LINE_RE.match(line.strip())
            if not match:
                continue
            status = match.group(1).upper()
            metric_name = metric_cycle[metric_index % len(metric_cycle)]
            metric_index += 1
            if status == "PASS":
                pass_count += 1
                tests_by_metric[metric_name]["pass"] += 1
            elif status == "FAIL":
                fail_count += 1
                tests_by_metric[metric_name]["fail"] += 1
            elif status == "SKIP":
                skip_count += 1
                tests_by_metric[metric_name]["skip"] += 1

    overall = score_from_counts(pass_count, fail_count)
    tests = {
        key: score_from_counts(counts["pass"], counts["fail"]) if (counts["pass"] + counts["fail"]) else overall
        for key, counts in tests_by_metric.items()
    }
    status = "PASS" if pass_count > 0 and fail_count == 0 else "FAIL" if fail_count else "RUNNING"

    return {
        "status": status,
        "updatedAt": time.time(),
        "metrics": {
            "overallScore": overall,
            "colorAccuracy": tests["colorAccuracy"],
            "sharpness": tests["resolution"],
            "exposure": tests["dynamicRange"],
        },
        "tests": tests,
        "source": str(results_dir),
        "counts": {"pass": pass_count, "fail": fail_count, "skip": skip_count},
    }


def classify_metric(path: Path, text: str) -> str | None:
    name = path.name.lower()
    body = text.lower()
    if any(token in name or token in body for token in ("color", "colour", "white_balance")):
        return "colorAccuracy"
    if any(token in name or token in body for token in ("sharp", "resolution", "mtf")):
        return "resolution"
    if any(token in name or token in body for token in ("dynamic", "exposure", "hdr")):
        return "dynamicRange"
    if any(token in name or token in body for token in ("defect", "hot_pixel", "noise")):
        return "defectDetect"
    return None


def summarize_results(results_dir: Path) -> dict[str, Any]:
    if not results_dir.exists():
        return {
            "status": "WAITING",
            "updatedAt": time.time(),
            "metrics": {"overallScore": 0, "colorAccuracy": 0, "sharpness": 0, "exposure": 0},
            "tests": {},
            "source": str(results_dir),
            "message": "Waiting for Camera ITS output directory.",
        }

    scene_summaries = find_scene_summaries(results_dir)
    if scene_summaries:
        return summarize_scene_summaries(scene_summaries, results_dir)

    pass_count = 0
    fail_count = 0
    skip_count = 0
    metric_counts: dict[str, dict[str, int]] = {
        "colorAccuracy": {"pass": 0, "fail": 0, "skip": 0},
        "resolution": {"pass": 0, "fail": 0, "skip": 0},
        "dynamicRange": {"pass": 0, "fail": 0, "skip": 0},
        "defectDetect": {"pass": 0, "fail": 0, "skip": 0},
    }

    for file_path in find_text_files(results_dir):
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        f_pass = len(PASS_RE.findall(text))
        f_fail = len(FAIL_RE.findall(text))
        f_skip = len(SKIP_RE.findall(text))

        pass_count += f_pass
        fail_count += f_fail
        skip_count += f_skip

        metric = classify_metric(file_path, text)
        if metric:
            metric_counts[metric]["pass"] += f_pass
            metric_counts[metric]["fail"] += f_fail
            metric_counts[metric]["skip"] += f_skip

    overall = score_from_counts(pass_count, fail_count)
    status = "PASS" if pass_count > 0 and fail_count == 0 else "FAIL" if fail_count else "RUNNING"

    tests = {
        key: score_from_counts(counts["pass"], counts["fail"]) or overall
        for key, counts in metric_counts.items()
    }

    return {
        "status": status,
        "updatedAt": time.time(),
        "metrics": {
            "overallScore": overall,
            "colorAccuracy": tests["colorAccuracy"],
            "sharpness": tests["resolution"],
            "exposure": tests["dynamicRange"],
        },
        "tests": tests,
        "source": str(results_dir),
        "counts": {"pass": pass_count, "fail": fail_count, "skip": skip_count},
    }


class ItsHandler(BaseHTTPRequestHandler):
    results_dir: Path

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        if not self.path.startswith("/its-status.json"):
            self.send_response(404)
            self.end_headers()
            return

        latest_target = find_latest_cameraits_dir(self.results_dir)
        analysis_target = latest_target if latest_target else self.results_dir
        result_data = summarize_results(analysis_target)
        
        payload = json.dumps(result_data, ensure_ascii=False, indent=2).encode("utf-8")
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve latest Camera ITS output as dashboard JSON.")
    parser.add_argument("--results-dir", required=True, type=Path, help="Root directory to find CameraITS_* folders.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int) # 포트 8766으로 변경
    args = parser.parse_args()

    if not args.results_dir.exists():
        print(f"Error: Path {args.results_dir} does not exist.")
        return

    ItsHandler.results_dir = args.results_dir
    server = ThreadingHTTPServer((args.host, args.port), ItsHandler)
    
    # 요청하신 형식의 시작 메시지
    print(f"================================================")
    print(f"  ITS Monitor Server Started")
    print(f"  Watching: {args.results_dir.absolute()}")
    print(f"  API URL : http://{args.host}:{args.port}/its-status.json")
    print(f"================================================")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")


if __name__ == "__main__":
    main()