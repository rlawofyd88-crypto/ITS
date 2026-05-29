#!/usr/bin/env python3
"""Collect live CameraITS Mobly logs into fixed rotating files.

This script does not modify CameraITS itself. It watches the latest
CameraITS_* run directory, tails per-test Mobly logs, and mirrors them into
fixed files such as /tmp/its_live/its_live.DEBUG and /tmp/its_live/its_live.INFO.
"""

import argparse
import logging.handlers
import os
import re
import time
from pathlib import Path


DEFAULT_RESULTS_DIR = Path("/tmp")
DEFAULT_OUTPUT_DIR = Path("/tmp/its_live")
DEFAULT_PREFIX = "its_live"
DEFAULT_POLL_INTERVAL = 0.5
DEFAULT_MAX_BYTES = 10 * 1024 * 1024
DEFAULT_BACKUP_COUNT = 3
DEFAULT_CAMERA_ID = "cam_id_0"
SCENE_ORDER = {
    "scene0", "scene1_1", "scene1_2", "scene1_3", "scene2_a", "scene2_b",
    "scene2_c", "scene2_d", "scene2_e", "scene2_f", "scene2_g", "scene3",
    "scene4", "scene6", "scene7", "scene8", "scene9", "scene_hdr",
    "scene_low_light", "scene6_tele", "scene7_tele", "scene_video",
    "sensor_fusion", "feature_combination", "scene_flash", "scene_ip",
    "scene_gen2_chart",
}
TIMESTAMPED_TEST_DIR_RE = re.compile(
    r"^\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2}-\d{3}_(?P<test>[A-Za-z0-9]+)$"
)


def camel_to_snake(value: str) -> str:
  value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
  value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
  return value.lower()


def find_latest_run(results_dir: Path) -> Path | None:
  if results_dir.is_dir() and results_dir.name.startswith("CameraITS_"):
    return results_dir

  candidates = []
  for path in results_dir.glob("CameraITS_*"):
    if not path.is_dir():
      continue
    try:
      candidates.append((path.stat().st_mtime, path))
    except OSError:
      continue
  return max(candidates, key=lambda item: item[0])[1] if candidates else None


def get_camera_id_from_path(path: Path, run_dir: Path) -> str:
  try:
    parts = path.relative_to(run_dir).parts
  except ValueError:
    parts = path.parts
  for part in parts:
    if part.startswith("cam_id_"):
      return part
  return DEFAULT_CAMERA_ID


def get_scene_name_from_path(path: Path, run_dir: Path) -> str:
  try:
    parts = path.relative_to(run_dir).parts
  except ValueError:
    parts = path.parts
  for part in parts:
    if part in SCENE_ORDER:
      return part
  return ""


def get_test_name_from_path(path: Path) -> str:
  for part in reversed(path.parts):
    match = TIMESTAMPED_TEST_DIR_RE.match(part)
    if match:
      raw = camel_to_snake(match.group("test"))
      if raw.endswith("_test"):
        raw = raw[:-5]
      return f"test_{raw}"

  parent_name = camel_to_snake(path.parent.name)
  if parent_name.endswith("_test"):
    parent_name = parent_name[:-5]
  return f"test_{parent_name}"


class LiveLogCollector:
  def __init__(self, results_dir: Path, output_dir: Path, prefix: str,
               poll_interval: float, max_bytes: int, backup_count: int):
    self.results_dir = results_dir
    self.output_dir = output_dir
    self.prefix = prefix
    self.poll_interval = poll_interval
    self.file_offsets: dict[str, int] = {}
    self.started_logs: set[str] = set()
    self.ended_logs: set[str] = set()
    self.active_run_key = ""

    self.output_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(message)s")

    self.debug_logger = logging.getLogger("its_live_debug")
    self.debug_logger.setLevel(logging.DEBUG)
    self.debug_logger.propagate = False
    self.debug_logger.handlers.clear()

    debug_handler = logging.handlers.RotatingFileHandler(
        self.output_dir / f"{self.prefix}.DEBUG",
        mode="a", maxBytes=max_bytes, backupCount=backup_count,
        encoding="utf-8")
    debug_handler.setFormatter(formatter)
    self.debug_logger.addHandler(debug_handler)

    self.info_logger = logging.getLogger("its_live_info")
    self.info_logger.setLevel(logging.INFO)
    self.info_logger.propagate = False
    self.info_logger.handlers.clear()

    info_handler = logging.handlers.RotatingFileHandler(
        self.output_dir / f"{self.prefix}.INFO",
        mode="a", maxBytes=max_bytes, backupCount=backup_count,
        encoding="utf-8")
    info_handler.setFormatter(formatter)
    self.info_logger.addHandler(info_handler)

  def reset_for_run(self, run_dir: Path) -> None:
    run_key = str(run_dir.resolve())
    if run_key == self.active_run_key:
      return
    self.active_run_key = run_key
    self.file_offsets = {}
    self.started_logs = set()
    self.ended_logs = set()

  def emit_start(self, camera_id: str, scene_name: str, test_name: str) -> None:
    marker = (
        f"LIVE_LOG_START scene={scene_name} camera={camera_id} "
        f"test={test_name} output={self.output_dir}"
    )
    self.debug_logger.debug(marker)
    self.info_logger.info(marker)

  def emit_end(self, camera_id: str, scene_name: str, test_name: str) -> None:
    marker = (
        f"LIVE_LOG_END scene={scene_name} camera={camera_id} "
        f"test={test_name}"
    )
    self.debug_logger.debug(marker)
    self.info_logger.info(marker)

  def append_line(self, log_name: str, line: str) -> None:
    if log_name.endswith(".DEBUG"):
      self.debug_logger.debug(line)
    elif log_name.endswith(".INFO"):
      self.info_logger.info(line)

  def process_log_file(self, log_path: Path, run_dir: Path) -> None:
    try:
      stat_result = log_path.stat()
    except OSError:
      return

    path_key = str(log_path)
    offset = self.file_offsets.get(path_key, 0)
    if offset > stat_result.st_size:
      offset = 0

    camera_id = get_camera_id_from_path(log_path, run_dir)
    scene_name = get_scene_name_from_path(log_path, run_dir)
    test_name = get_test_name_from_path(log_path)
    if not scene_name:
      return

    if path_key not in self.started_logs:
      self.emit_start(camera_id, scene_name, test_name)
      self.started_logs.add(path_key)

    if offset != stat_result.st_size:
      try:
        with log_path.open("r", encoding="utf-8", errors="ignore") as file:
          file.seek(offset)
          new_text = file.read()
          self.file_offsets[path_key] = file.tell()
      except OSError:
        return

      for line in new_text.replace("\r", "").split("\n"):
        stripped = line.strip()
        if stripped:
          self.append_line(log_path.name, stripped)

    summary_path = log_path.parent / "test_summary.yaml"
    if summary_path.exists() and path_key not in self.ended_logs:
      self.emit_end(camera_id, scene_name, test_name)
      self.ended_logs.add(path_key)

  def run_forever(self) -> None:
    print("================================================")
    print("   CameraITS Live Log Collector Started")
    print(f"   Watching: {self.results_dir}")
    print(f"   Output  : {self.output_dir}")
    print(f"   Prefix  : {self.prefix}")
    print("================================================")
    while True:
      run_dir = find_latest_run(self.results_dir)
      if run_dir:
        self.reset_for_run(run_dir)
        debug_logs = sorted(run_dir.rglob("test_log.DEBUG"))
        debug_parents = {log.parent for log in debug_logs}
        info_logs = [
            log for log in sorted(run_dir.rglob("test_log.INFO"))
            if log.parent not in debug_parents
        ]
        for log_path in debug_logs + info_logs:
          if log_path.is_file():
            self.process_log_file(log_path, run_dir)
      time.sleep(self.poll_interval)


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
  parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
  parser.add_argument("--prefix", default=DEFAULT_PREFIX)
  parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL)
  parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
  parser.add_argument("--backup-count", type=int, default=DEFAULT_BACKUP_COUNT)
  return parser.parse_args()


def main():
  args = parse_args()
  collector = LiveLogCollector(
      results_dir=args.results_dir.expanduser(),
      output_dir=args.output_dir.expanduser(),
      prefix=args.prefix,
      poll_interval=args.poll_interval,
      max_bytes=args.max_bytes,
      backup_count=args.backup_count,
  )
  try:
    collector.run_forever()
  except KeyboardInterrupt:
    print("\nShutting down...")


if __name__ == "__main__":
  main()
