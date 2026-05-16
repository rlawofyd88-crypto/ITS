#!/usr/bin/env python3
"""Continuously mirror a DUT screen into a dashboard PNG file."""

from __future__ import annotations

import argparse
import os
import subprocess
import time
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mirror DUT screen to PNG.")
    parser.add_argument("--serial", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--interval", default=1.0, type=float)
    args = parser.parse_args()

    remote_path = "/sdcard/Download/codex_dut_live.png"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = args.output.with_suffix(args.output.suffix + ".tmp")

    while True:
        try:
            run(["adb", "-s", args.serial, "shell", "screencap", "-p", remote_path])
            run(["adb", "-s", args.serial, "pull", remote_path, str(temp_output)])
            os.replace(temp_output, args.output)
        except subprocess.CalledProcessError:
            pass
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
