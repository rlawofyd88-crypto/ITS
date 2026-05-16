#!/usr/bin/env python3
"""Export a one-shot ITS dashboard JSON file from a Camera ITS result folder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from its_dashboard_adapter import summarize_results


def main() -> None:
    parser = argparse.ArgumentParser(description="Export ITS status JSON.")
    parser.add_argument("--results-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    payload = summarize_results(args.results_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
