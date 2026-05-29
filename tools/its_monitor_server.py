# its_monitor_server.py 수정본

#!/usr/bin/env python3
import argparse
import configparser
import json
import time
import re
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Any, List, Dict
from urllib.parse import parse_qs, urlparse

DEFAULT_CONFIG_PATH = Path(__file__).with_name("its_monitor_server.cfg")
DEFAULT_SERVER_CONFIG = {
    "results_dir": "/tmp",
    "its_tools": "",
    "port": "8765",
    "replay_interval": "0.5",
}

MASTER_STRUCTURE = [
    {"scene": "scene0", "tests": ["test_jitter", "test_metadata", "test_request_capture_match", "test_sensor_events", "test_solid_color_test_pattern", "test_test_patterns", "test_tonemap_curve", "test_unified_timestamps", "test_vibration_restriction"]},
    {"scene": "scene1_1", "tests": ["test_ae_precapture_trigger", "test_auto_vs_manual", "test_black_white", "test_burst_capture", "test_burst_sameness_manual", "test_crop_region_raw", "test_crop_regions", "test_exposure_x_iso", "test_latching", "test_linearity", "test_locked_burst"]},
    {"scene": "scene1_2", "tests": ["test_param_color_correction", "test_param_flash_mode", "test_param_noise_reduction", "test_param_shading_mode", "test_param_tonemap_mode", "test_post_raw_sensitivity_boost", "test_raw_exposure", "test_reprocess_noise_reduction", "test_tonemap_sequence", "test_yuv_plus_dng"]},
    {"scene": "scene1_3", "tests": ["test_capture_result", "test_dng_noise_model", "test_ev_compensation", "test_exposure_time_priority", "test_jpeg", "test_raw_burst_sensitivity", "test_raw_sensitivity", "test_sensitivity_priority", "test_yuv_jpeg_all", "test_yuv_plus_jpeg", "test_yuv_plus_raw"]},
    {"scene": "scene2_a", "tests": ["test_display_p3", "test_effects", "test_exposure_keys_consistent", "test_format_combos", "test_num_faces", "test_reprocess_uv_swap"]},
    {"scene": "scene2_b", "tests": ["test_preview_num_faces", "test_yuv_jpeg_capture_sameness"]},
    {"scene": "scene2_c", "tests": ["test_camera_launch_perf_class", "test_default_camera_hdr", "test_jpeg_capture_perf_class", "test_num_faces"]},
    {"scene": "scene2_d", "tests": ["test_autoframing", "test_num_faces", "test_preview_num_faces"]},
    {"scene": "scene2_e", "tests": ["test_continuous_picture", "test_num_faces"]},
    {"scene": "scene2_f", "tests": ["test_preview_num_faces"]},
    {"scene": "scene2_g", "tests": ["test_preview_num_faces"]},
    {"scene": "scene3", "tests": ["test_edge_enhancement", "test_flip_mirror", "test_imu_drift", "test_landscape_to_portrait", "test_lens_movement_reporting", "test_reprocess_edge_enhancement"]},
    {"scene": "scene4", "tests": ["test_30_60fps_preview_fov_match", "test_aspect_ratio_and_crop", "test_multi_camera_alignment", "test_preview_aspect_ratio_and_crop", "test_preview_stabilization_fov", "test_video_aspect_ratio_and_crop"]},
    {"scene": "scene6", "tests": ["test_in_sensor_zoom", "test_low_latency_zoom", "test_preview_video_zoom_match", "test_preview_zoom", "test_session_characteristics_zoom", "test_zoom"]},
    {"scene": "scene7", "tests": ["test_multi_camera_switch"]},
    {"scene": "scene8", "tests": ["test_ae_awb_regions", "test_color_correction_mode_cct"]},
    {"scene": "scene9", "tests": ["test_jpeg_high_entropy", "test_jpeg_quality"]},
    {"scene": "scene_hdr", "tests": ["test_hdr_extension"]},
    {"scene": "scene_low_light", "tests": ["test_low_light_boost_extension", "test_night_extension"]},
    {"scene": "scene6_tele", "tests": ["test_preview_zoom_tele", "test_zoom_tele"]},
    {"scene": "scene7_tele", "tests": ["test_multi_camera_switch_tele"]},
    {"scene": "scene_video", "tests": ["test_preview_frame_drop"]}
]

SCENE_ORDER = [item["scene"] for item in MASTER_STRUCTURE]
SCENE_INDEX = {scene: index for index, scene in enumerate(SCENE_ORDER)}
TEST_INDEX = {
    (item["scene"], test_name): index
    for item in MASTER_STRUCTURE
    for index, test_name in enumerate(item["tests"])
}

STATUS_LINE_RE = re.compile(r"^(PASS|FAIL|SKIP)\s+", re.IGNORECASE)
TEST_NAME_RE = re.compile(r"^\s*Test Name:\s*(test_[A-Za-z0-9_]+)\s*$", re.IGNORECASE | re.MULTILINE)
TEST_RESULT_RE = re.compile(r"^\s*Result:\s*(PASS|FAIL|SKIP|ERROR)\s*$", re.IGNORECASE | re.MULTILINE)
TEST_RECORD_RE = re.compile(r"^\s*Type:\s*Record\s*$", re.IGNORECASE | re.MULTILINE)
TEST_END_TIME_RE = re.compile(r"^\s*End Time:\s*(\d+)\s*$", re.IGNORECASE | re.MULTILINE)
TEST_LOG_RESULT_RE = re.compile(r"\[Test\]\s+(test_[A-Za-z0-9_]+)\s+(PASS|FAIL|SKIP|ERROR)\b", re.IGNORECASE)
CURRENT_TEST_LOG_RE = re.compile(r"\[Test\]\s+(test_[A-Za-z0-9_]+)\b", re.IGNORECASE)
EXECUTING_TEST_CLASS_RE = re.compile(
    r'Executing test class "(?P<class>[A-Za-z0-9]+)"',
    re.IGNORECASE,
)
DEBUG_LOG_LINE_RE = re.compile(
    r"^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+\s+(DEBUG|INFO)\b"
)

DEBUG_SUMMARY_PREFIXES = (
    "Total time elapsed",
    "Artifacts are saved in",
    "Test summary saved in",
    "Test results:",
)
TEST_NAME_ALIASES = {
    ("scene1_1", "test_ae_precapture"): "test_ae_precapture_trigger",
    ("scene1_3", "test_sensor_sensitivity_priority"): "test_sensitivity_priority",
}
IMAGE_EXTENSIONS = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".webp"}
DEFAULT_CAMERA_ID = "cam_id_0"
LIVE_STDOUT_SUFFIX = "_stdout.txt"
RUN_ALL_TESTS_LIVE_LOG = "run_all_tests_live.log"
LIVE_MOBLY_LOG_CANDIDATES = ("test_log.DEBUG", "test_log.INFO")
FIXED_LIVE_LOG_PREFIX = "its_live"
FIXED_LIVE_LOG_DIRNAME = "its_live"
FIXED_LIVE_LOG_CANDIDATES = (
    f"{FIXED_LIVE_LOG_PREFIX}.DEBUG",
    f"{FIXED_LIVE_LOG_PREFIX}.INFO",
)
LIVE_LOG_PREFIX_RE = re.compile(
    r"^\[(?P<scene>[^\]/]+)/(?P<test>[^\]]+)\]\s*(?P<text>.*)$"
)
TIMESTAMPED_TEST_DIR_RE = re.compile(
    r"^\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2}-\d{3}_(?P<test>[A-Za-z0-9]+)$"
)
LIVE_LOG_START_RE = re.compile(
    r".*LIVE_LOG_START scene=(?P<scene>\S*) camera=(?P<camera>\S*) test=(?P<test>\S*)"
)
LIVE_LOG_END_RE = re.compile(
    r".*LIVE_LOG_END scene=(?P<scene>\S*) camera=(?P<camera>\S*) test=(?P<test>\S*)"
)

class ITSMonitor:
    def __init__(self, root_dir: Path, replay_interval: float = 0.5):
        self.root_dir = root_dir
        self.replay_interval = max(0.0, replay_interval)
        self.status_map = {"PASS": 1, "SKIP": 2, "FAIL": 3}
        self.active_run_key = ""
        self.visible_results: Dict[str, Dict[str, Dict[str, int]]] = {}
        self.pending_results: List[Dict[str, Any]] = []
        self.published_events: List[Dict[str, Any]] = []
        self.current_event: Dict[str, Any] | None = None
        self.current_events_by_camera: Dict[str, Dict[str, Any]] = {}
        self.last_replay_emit_at: float | None = None
        self.replay_sequence = 0
        self.log_scene_name = ""
        self.replay_lock = Lock()
        self.log_entries: List[Dict[str, Any]] = []
        self.log_sequence = 0
        self.live_file_offsets: Dict[str, int] = {}
        self.last_emitted_log_camera_id = ""
        self.fixed_log_context: Dict[str, str] = {}
        self.active_execution: Dict[str, Any] | None = None
        self.active_executions_by_camera: Dict[str, Dict[str, Any]] = {}

    def status_value(self, status: str) -> int:
        normalized = status.upper()
        if normalized == "ERROR":
            normalized = "FAIL"
        return self.status_map.get(normalized, 0)

    def status_text(self, status_value: int) -> str:
        if status_value == 4:
            return "RUNNING"
        for status, value in self.status_map.items():
            if value == status_value:
                return status
        return "WAIT"

    def path_mtime(self, path: Path) -> float:
        try:
            return path.stat().st_mtime
        except OSError:
            return 0.0

    def normalize_test_name(self, scene_name: str, test_name: str) -> str:
        return TEST_NAME_ALIASES.get((scene_name, test_name), test_name)

    def camera_sort_key(self, camera_id: str):
        suffix = camera_id.replace("cam_id_", "", 1)
        return (0, int(suffix)) if suffix.isdigit() else (1, suffix)

    def result_sort_key(self, event: Dict[str, Any]):
        return (
            self.camera_sort_key(event.get("cameraId", DEFAULT_CAMERA_ID)),
            SCENE_INDEX.get(event["scene"], 999),
            TEST_INDEX.get((event["scene"], event["test"]), 999),
            event["completedAt"],
            event["test"],
        )

    def reset_replay(self, its_dir: Path) -> None:
        try:
            run_key = str(its_dir.resolve())
        except OSError:
            run_key = str(its_dir)

        if run_key == self.active_run_key:
            return

        self.active_run_key = run_key
        self.visible_results = {}
        self.pending_results = []
        self.published_events = []
        self.current_event = None
        self.current_events_by_camera = {}
        self.last_replay_emit_at = None
        self.replay_sequence = 0
        self.log_scene_name = ""
        self.last_log_camera_id = ""
        self.log_entries = []
        self.log_sequence = 0
        self.live_file_offsets = {}
        self.last_emitted_log_camera_id = ""
        self.fixed_log_context = {}
        self.active_execution = None
        self.active_executions_by_camera = {}

    def copy_visible_results(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        return {
            camera_id: {
                scene_name: dict(scene_results)
                for scene_name, scene_results in camera_results.items()
            }
            for camera_id, camera_results in self.visible_results.items()
        }

    def add_result_event(
        self,
        events: Dict[tuple[str, str, str], Dict[str, Any]],
        camera_id: str | None,
        scene_name: str | None,
        test_name: str,
        status: int,
        completed_at: float,
        source_group: int,
        artifact_dir: Path | None = None,
        log_file: Path | None = None,
    ) -> None:
        if not scene_name or not status:
            return

        normalized_camera_id = camera_id or DEFAULT_CAMERA_ID
        normalized_test_name = self.normalize_test_name(scene_name, test_name)
        event_key = (normalized_camera_id, scene_name, normalized_test_name)
        if (scene_name, normalized_test_name) not in TEST_INDEX:
            return

        event = {
            "cameraId": normalized_camera_id,
            "cameraLabel": normalized_camera_id,
            "scene": scene_name,
            "test": normalized_test_name,
            "status": status,
            "completedAt": completed_at,
            "sourceGroup": source_group,
            "artifactDir": str(artifact_dir) if artifact_dir else "",
            "logFile": str(log_file) if log_file else "",
        }
        previous = events.get(event_key)
        if previous is None:
            events[event_key] = event
            return

        if not previous.get("artifactDir") and event.get("artifactDir"):
            previous["artifactDir"] = event["artifactDir"]
        if not previous.get("logFile") and event.get("logFile"):
            previous["logFile"] = event["logFile"]

        if not event.get("artifactDir") and previous.get("artifactDir"):
            event["artifactDir"] = previous["artifactDir"]
        if not event.get("logFile") and previous.get("logFile"):
            event["logFile"] = previous["logFile"]

        if event["sourceGroup"] < previous["sourceGroup"]:
            events[event_key] = event
            return

        if event["sourceGroup"] == previous["sourceGroup"] and event["completedAt"] < previous["completedAt"]:
            events[event_key] = event

    def get_latest_dir(self) -> Path | None:
        if self.root_dir.is_dir() and self.root_dir.name.startswith("CameraITS_"):
            return self.root_dir

        candidates = []
        for path in self.root_dir.glob("CameraITS_*"):
            if not path.is_dir():
                continue
            try:
                candidates.append((path.stat().st_mtime, path))
            except OSError:
                continue
        return max(candidates, key=lambda item: item[0])[1] if candidates else None

    def get_camera_id_from_path(self, path: Path, its_dir: Path) -> str:
        try:
            path_parts = path.relative_to(its_dir).parts
        except ValueError:
            path_parts = path.parts

        for part in path_parts:
            if part.startswith("cam_id_"):
                return part
        return DEFAULT_CAMERA_ID

    def get_camera_ids(self, its_dir: Path | None = None) -> List[str]:
        camera_ids = set()
        if its_dir and its_dir.is_dir():
            for path in its_dir.glob("cam_id_*"):
                if path.is_dir():
                    camera_ids.add(path.name)

        with self.replay_lock:
            camera_ids.update(self.visible_results.keys())
            camera_ids.update(event.get("cameraId", DEFAULT_CAMERA_ID) for event in self.pending_results)
            camera_ids.update(event.get("cameraId", DEFAULT_CAMERA_ID) for event in self.published_events)
            if self.current_event:
                camera_ids.add(self.current_event.get("cameraId", DEFAULT_CAMERA_ID))

        return sorted(camera_ids, key=self.camera_sort_key)

    def camel_to_snake(self, value: str) -> str:
        value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
        value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
        return value.lower()

    def append_log_entry(
        self,
        camera_id: str,
        scene_name: str,
        test_name: str,
        text: str,
        entry_type: str = "LOG",
    ) -> None:
        if not text:
            return

        normalized_camera_id = camera_id or DEFAULT_CAMERA_ID
        normalized_test_name = test_name.replace(".py", "")

        if (
            self.last_emitted_log_camera_id
            and self.last_emitted_log_camera_id != normalized_camera_id
        ):
            self.log_sequence += 1
            self.log_entries.append({
                "type": "CAMERA_CHANGE",
                "id": f"camera:{self.log_sequence}:{normalized_camera_id}",
                "sequence": self.log_sequence,
                "cameraId": normalized_camera_id,
                "scene": scene_name,
                "test": normalized_test_name,
                "text": f"--- CAMERA_CHANGED_{normalized_camera_id} ---",
            })

        self.last_emitted_log_camera_id = normalized_camera_id
        self.log_sequence += 1
        self.log_entries.append({
            "type": entry_type,
            "id": f"log:{self.log_sequence}:{normalized_camera_id}:{scene_name}:{normalized_test_name}",
            "sequence": self.log_sequence,
            "cameraId": normalized_camera_id,
            "scene": scene_name,
            "test": normalized_test_name,
            "text": text,
        })

    def set_active_execution(
        self,
        camera_id: str,
        scene_name: str,
        test_name: str,
        artifact_dir: Path | None = None,
    ) -> None:
        if not scene_name or not test_name:
            return

        normalized_camera_id = camera_id or DEFAULT_CAMERA_ID
        normalized_test_name = self.normalize_test_name(
            scene_name, test_name.replace(".py", "")
        )
        execution = {
            "cameraId": normalized_camera_id,
            "cameraLabel": normalized_camera_id,
            "scene": scene_name,
            "test": normalized_test_name,
            "sourceDir": str(artifact_dir) if artifact_dir else "",
            "updatedAt": time.time(),
        }
        self.active_execution = execution
        self.active_executions_by_camera[normalized_camera_id] = execution

    def get_active_execution(self, camera_id: str | None = None) -> Dict[str, Any] | None:
        with self.replay_lock:
            if camera_id:
                execution = self.active_executions_by_camera.get(camera_id)
                return dict(execution) if execution else None
            return dict(self.active_execution) if self.active_execution else None

    def parse_live_log_path(self, log_path: Path, its_dir: Path) -> tuple[str, str, str]:
        camera_id = self.get_camera_id_from_path(log_path, its_dir)
        try:
            relative_parts = log_path.relative_to(its_dir).parts
        except ValueError:
            relative_parts = log_path.parts

        scene_name = ""
        for part in relative_parts:
            if part in SCENE_ORDER:
                scene_name = part
                break

        test_name = log_path.stem
        if test_name.endswith(LIVE_STDOUT_SUFFIX.replace(".txt", "")):
            test_name = test_name[: -len(LIVE_STDOUT_SUFFIX.replace(".txt", ""))]
        if test_name.endswith("_stdout"):
            test_name = test_name[:-7]

        return camera_id, scene_name, test_name

    def parse_mobly_live_log_path(self, log_path: Path, its_dir: Path) -> tuple[str, str, str]:
        camera_id = self.get_camera_id_from_path(log_path, its_dir)
        scene_name = self.get_scene_name_from_path(log_path, its_dir) or ""
        try:
            relative_parts = log_path.relative_to(its_dir).parts
        except ValueError:
            relative_parts = log_path.parts

        def normalize_candidate(raw_name: str) -> str:
            snake_name = self.camel_to_snake(raw_name)
            if snake_name.endswith("_test"):
                snake_name = snake_name[:-5]
            normalized = f"test_{snake_name}"
            return self.normalize_test_name(scene_name, normalized)

        test_name = ""
        for part in reversed(relative_parts):
            matched = TIMESTAMPED_TEST_DIR_RE.match(part)
            if matched:
                test_name = normalize_candidate(matched.group("test"))
                break

        if test_name and (scene_name, test_name) in TEST_INDEX:
            return camera_id, scene_name, test_name

        fallback_candidates = [log_path.parent.name]
        if len(relative_parts) >= 2:
            fallback_candidates.append(relative_parts[-2])
        try:
            fallback_candidates.extend(
                child.name
                for child in log_path.parent.iterdir()
                if child.is_dir() and child.name.endswith("Test")
            )
        except OSError:
            pass

        for candidate in fallback_candidates:
            if not candidate:
                continue
            normalized = normalize_candidate(candidate)
            if not scene_name or (scene_name, normalized) in TEST_INDEX:
                test_name = normalized
                break

        return camera_id, scene_name, test_name

    def collect_incremental_mobly_log(self, log_path: Path, its_dir: Path) -> None:
        try:
            stat_result = log_path.stat()
        except OSError:
            return

        path_key = str(log_path)
        previous_offset = self.live_file_offsets.get(path_key, 0)
        if previous_offset > stat_result.st_size:
            previous_offset = 0

        if previous_offset == stat_result.st_size:
            return

        camera_id, scene_name, test_name = self.parse_mobly_live_log_path(log_path, its_dir)
        if not scene_name or not test_name:
            return
        self.set_active_execution(camera_id, scene_name, test_name, log_path.parent)

        try:
            with log_path.open("r", encoding="utf-8", errors="ignore") as file:
                file.seek(previous_offset)
                new_text = file.read()
                self.live_file_offsets[path_key] = file.tell()
        except OSError:
            return

        for line in new_text.replace("\r", "").split("\n"):
            stripped = line.strip()
            if not stripped:
                continue

            current_test_name = test_name
            current_test_match = CURRENT_TEST_LOG_RE.search(stripped)
            if current_test_match:
                current_test_name = self.normalize_test_name(
                    scene_name,
                    current_test_match.group(1),
                )
                self.set_active_execution(camera_id, scene_name, current_test_name, log_path.parent)
                test_name = current_test_name
            else:
                class_match = EXECUTING_TEST_CLASS_RE.search(stripped)
                if class_match:
                    current_test_name = self.normalize_test_name(
                        scene_name,
                        f"test_{self.camel_to_snake(class_match.group('class')).removesuffix('_test')}",
                    )
                    self.set_active_execution(camera_id, scene_name, current_test_name, log_path.parent)
                    test_name = current_test_name

            self.append_log_entry(camera_id, scene_name, current_test_name, stripped, "LIVE_LOG")

    def collect_live_mobly_logs(self, its_dir: Path) -> bool:
        selected_logs = []
        for debug_log in its_dir.rglob("test_log.DEBUG"):
            if debug_log.is_file():
                selected_logs.append(debug_log)

        if not selected_logs:
            for info_log in its_dir.rglob("test_log.INFO"):
                if info_log.is_file():
                    selected_logs.append(info_log)

        selected_logs.sort(key=self.path_mtime)
        for log_path in selected_logs:
            self.collect_incremental_mobly_log(log_path, its_dir)

        return bool(selected_logs)

    def collect_fixed_live_logs(self, its_dir: Path) -> bool:
        selected_logs = []
        search_roots = [its_dir]
        parent_dir = its_dir.parent if its_dir.parent != its_dir else None
        if parent_dir:
            search_roots.append(parent_dir)
            search_roots.append(parent_dir / FIXED_LIVE_LOG_DIRNAME)

        for root in search_roots:
            for file_name in FIXED_LIVE_LOG_CANDIDATES:
                log_path = root / file_name
                if log_path.is_file() and log_path not in selected_logs:
                    selected_logs.append(log_path)

        selected_logs.sort(key=self.path_mtime)
        for log_path in selected_logs:
          self.collect_incremental_fixed_live_log(log_path)

        return bool(selected_logs)

    def collect_incremental_fixed_live_log(self, log_path: Path) -> None:
        try:
            stat_result = log_path.stat()
        except OSError:
            return

        path_key = str(log_path)
        previous_offset = self.live_file_offsets.get(path_key, 0)
        if previous_offset > stat_result.st_size:
            previous_offset = 0

        if previous_offset == stat_result.st_size:
            return

        try:
            with log_path.open("r", encoding="utf-8", errors="ignore") as file:
                file.seek(previous_offset)
                new_text = file.read()
                self.live_file_offsets[path_key] = file.tell()
        except OSError:
            return

        for line in new_text.replace("\r", "").split("\n"):
            stripped = line.strip()
            if not stripped:
                continue

            start_match = LIVE_LOG_START_RE.match(stripped)
            if start_match:
                self.fixed_log_context = {
                    "cameraId": start_match.group("camera") or DEFAULT_CAMERA_ID,
                    "scene": start_match.group("scene") or "",
                    "test": start_match.group("test") or "",
                }
                self.set_active_execution(
                    self.fixed_log_context["cameraId"],
                    self.fixed_log_context["scene"],
                    self.fixed_log_context["test"],
                    log_path.parent,
                )
                self.append_log_entry(
                    self.fixed_log_context["cameraId"],
                    self.fixed_log_context["scene"],
                    self.fixed_log_context["test"],
                    stripped,
                    "LIVE_LOG",
                )
                continue

            end_match = LIVE_LOG_END_RE.match(stripped)
            if end_match:
                camera_id = end_match.group("camera") or self.fixed_log_context.get(
                    "cameraId", DEFAULT_CAMERA_ID)
                scene_name = end_match.group("scene") or self.fixed_log_context.get(
                    "scene", "")
                test_name = end_match.group("test") or self.fixed_log_context.get(
                    "test", "")
                self.append_log_entry(
                    camera_id, scene_name, test_name, stripped, "LIVE_LOG")
                self.fixed_log_context = {}
                continue

            camera_id = self.fixed_log_context.get("cameraId", DEFAULT_CAMERA_ID)
            scene_name = self.fixed_log_context.get("scene", "")
            test_name = self.fixed_log_context.get("test", "")
            self.append_log_entry(
                camera_id, scene_name, test_name, stripped, "LIVE_LOG")

    def collect_incremental_live_log(self, log_path: Path, its_dir: Path) -> None:
        try:
            stat_result = log_path.stat()
        except OSError:
            return

        path_key = str(log_path)
        previous_offset = self.live_file_offsets.get(path_key, 0)
        if previous_offset > stat_result.st_size:
            previous_offset = 0

        if previous_offset == stat_result.st_size:
            return

        camera_id, scene_name, test_name = self.parse_live_log_path(log_path, its_dir)
        if not scene_name or not test_name:
            return
        self.set_active_execution(camera_id, scene_name, test_name, log_path.parent)

        try:
            with log_path.open("r", encoding="utf-8", errors="ignore") as file:
                file.seek(previous_offset)
                new_text = file.read()
                self.live_file_offsets[path_key] = file.tell()
        except OSError:
            return

        for line in new_text.replace("\r", "").split("\n"):
            stripped = line.strip()
            if stripped:
                self.append_log_entry(camera_id, scene_name, test_name, stripped, "LIVE_LOG")

    def collect_root_live_log(self, its_dir: Path) -> None:
        log_path = its_dir / RUN_ALL_TESTS_LIVE_LOG
        if not log_path.is_file():
            return

        try:
            stat_result = log_path.stat()
        except OSError:
            return

        path_key = str(log_path)
        previous_offset = self.live_file_offsets.get(path_key, 0)
        if previous_offset > stat_result.st_size:
            previous_offset = 0

        if previous_offset == stat_result.st_size:
            return

        try:
            with log_path.open("r", encoding="utf-8", errors="ignore") as file:
                file.seek(previous_offset)
                new_text = file.read()
                self.live_file_offsets[path_key] = file.tell()
        except OSError:
            return

        for line in new_text.replace("\r", "").split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            prefix_match = LIVE_LOG_PREFIX_RE.match(stripped)
            if prefix_match:
                scene_name = prefix_match.group("scene")
                test_name = prefix_match.group("test").replace(".py", "")
                text = prefix_match.group("text").strip() or stripped
                self.append_log_entry(DEFAULT_CAMERA_ID, scene_name, test_name, text, "LIVE_LOG")

    def collect_live_log_updates(self, its_dir: Path | None) -> None:
        if not its_dir or not its_dir.is_dir():
            return

        found_fixed_live_logs = self.collect_fixed_live_logs(its_dir)
        found_live_mobly_logs = self.collect_live_mobly_logs(its_dir)
        live_stdout_files = []
        for log_path in its_dir.rglob(f"*{LIVE_STDOUT_SUFFIX}"):
            if log_path.is_file():
                live_stdout_files.append(log_path)

        live_stdout_files.sort(key=self.path_mtime)
        for log_path in live_stdout_files:
            self.collect_incremental_live_log(log_path, its_dir)

        if not found_fixed_live_logs and not found_live_mobly_logs and not live_stdout_files:
            self.collect_root_live_log(its_dir)

    def get_active_camera_id(self, camera_ids: List[str]) -> str:
        active_execution = self.get_active_execution()
        if active_execution:
            camera_id = active_execution.get("cameraId", "")
            if camera_id in camera_ids:
                return camera_id
        current_event = self.get_current_event()
        if current_event:
            camera_id = current_event.get("cameraId", "")
            if camera_id in camera_ids:
                return camera_id
        return camera_ids[-1] if camera_ids else ""

    def get_latest_image(self, its_dir: Path | None = None) -> Path | None:
        search_dir = its_dir or self.get_latest_dir()
        if not search_dir:
            return None

        candidates = []
        for image_path in search_dir.rglob("*"):
            if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            try:
                candidates.append((image_path.stat().st_mtime, image_path))
            except OSError:
                continue

        return max(candidates, key=lambda item: item[0])[1] if candidates else None

    def get_current_event(self, camera_id: str | None = None) -> Dict[str, Any] | None:
        with self.replay_lock:
            if camera_id:
                event = self.current_events_by_camera.get(camera_id)
                return dict(event) if event else None
            return dict(self.current_event) if self.current_event else None

    def get_event_image(self, event: Dict[str, Any] | None = None, camera_id: str | None = None) -> Path | None:
        current_event = event or self.get_current_event(camera_id)
        if not current_event:
            return None

        artifact_dir = current_event.get("artifactDir")
        if not artifact_dir:
            return None

        return self.get_latest_image(Path(artifact_dir))

    def get_capture_info(self, camera_id: str | None = None) -> Dict[str, Any]:
        current_event = self.get_current_event(camera_id)
        if not current_event:
            return {
                "available": False,
                "imageUrl": "/latest-capture-image",
                "cameraId": camera_id or "",
                "cameraLabel": camera_id or "",
                "message": "Waiting for a CameraITS TC result.",
            }

        artifact_dir = Path(current_event["artifactDir"]) if current_event.get("artifactDir") else None
        image_path = self.get_event_image(current_event)
        if not image_path:
            return {
                "available": False,
                "imageUrl": "/latest-capture-image",
                "cameraId": current_event.get("cameraId", DEFAULT_CAMERA_ID),
                "cameraLabel": current_event.get("cameraLabel", current_event.get("cameraId", DEFAULT_CAMERA_ID)),
                "scene": current_event["scene"],
                "test": current_event["test"],
                "sequence": current_event.get("sequence", 0),
                "sourceDir": str(artifact_dir) if artifact_dir else "",
                "message": "No capture image for the current CameraITS TC.",
            }

        try:
            updated_at = image_path.stat().st_mtime
        except OSError:
            updated_at = time.time()

        return {
            "available": True,
            "imageUrl": "/latest-capture-image",
            "fileName": image_path.name,
            "cameraId": current_event.get("cameraId", DEFAULT_CAMERA_ID),
            "cameraLabel": current_event.get("cameraLabel", current_event.get("cameraId", DEFAULT_CAMERA_ID)),
            "scene": current_event["scene"],
            "test": current_event["test"],
            "sequence": current_event.get("sequence", 0),
            "relativePath": str(image_path.relative_to(artifact_dir)).replace("\\", "/") if artifact_dir else image_path.name,
            "sourceDir": str(artifact_dir) if artifact_dir else "",
            "updatedAt": updated_at,
        }

    def get_scene_name_from_path(self, path: Path, its_dir: Path) -> str | None:
        try:
            path_parts = path.relative_to(its_dir).parts
        except ValueError:
            path_parts = path.parts

        for part in path_parts:
            if part in SCENE_ORDER:
                return part
        return None

    def parse_test_summary_events(self, summary_file: Path, camera_id: str, scene_name: str) -> List[Dict[str, Any]]:
        try:
            text = summary_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        fallback_time = self.path_mtime(summary_file)
        events = {}
        for doc in re.split(r"(?m)^---\s*$", text):
            if not TEST_RECORD_RE.search(doc):
                continue
            name_match = TEST_NAME_RE.search(doc)
            result_match = TEST_RESULT_RE.search(doc)
            if not name_match or not result_match:
                continue

            completed_at = fallback_time
            end_time_match = TEST_END_TIME_RE.search(doc)
            if end_time_match:
                completed_at = int(end_time_match.group(1)) / 1000.0

            self.add_result_event(
                events,
                camera_id,
                scene_name,
                name_match.group(1),
                self.status_value(result_match.group(1)),
                completed_at,
                source_group=0,
                artifact_dir=summary_file.parent,
            )
        return sorted(events.values(), key=self.result_sort_key)

    def parse_test_log_events(self, log_file: Path, camera_id: str, scene_name: str) -> List[Dict[str, Any]]:
        try:
            text = log_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        completed_at = self.path_mtime(log_file)
        events = {}
        for match in TEST_LOG_RESULT_RE.finditer(text):
            self.add_result_event(
                events,
                camera_id,
                scene_name,
                match.group(1),
                self.status_value(match.group(2)),
                completed_at,
                source_group=0,
                artifact_dir=log_file.parent,
                log_file=log_file,
            )
        return sorted(events.values(), key=self.result_sort_key)

    def discover_tc_result_events(self, its_dir: Path) -> List[Dict[str, Any]]:
        events: Dict[tuple[str, str, str], Dict[str, Any]] = {}

        for log_file in its_dir.rglob("test_log.DEBUG"):
            camera_id = self.get_camera_id_from_path(log_file, its_dir)
            scene_name = self.get_scene_name_from_path(log_file, its_dir)
            if not scene_name:
                continue
            for event in self.parse_test_log_events(log_file, camera_id, scene_name):
                self.add_result_event(
                    events,
                    event["cameraId"],
                    event["scene"],
                    event["test"],
                    event["status"],
                    event["completedAt"],
                    event["sourceGroup"],
                    artifact_dir=Path(event["artifactDir"]) if event.get("artifactDir") else None,
                    log_file=Path(event["logFile"]) if event.get("logFile") else None,
                )

        for summary_file in its_dir.rglob("test_summary.yaml"):
            camera_id = self.get_camera_id_from_path(summary_file, its_dir)
            scene_name = self.get_scene_name_from_path(summary_file, its_dir)
            if not scene_name:
                continue
            for event in self.parse_test_summary_events(summary_file, camera_id, scene_name):
                self.add_result_event(
                    events,
                    event["cameraId"],
                    event["scene"],
                    event["test"],
                    event["status"],
                    event["completedAt"],
                    event["sourceGroup"],
                    artifact_dir=Path(event["artifactDir"]) if event.get("artifactDir") else None,
                    log_file=Path(event["logFile"]) if event.get("logFile") else None,
                )

        for scene_summary in its_dir.rglob("scene_test_summary.txt"):
            camera_id = self.get_camera_id_from_path(scene_summary, its_dir)
            scene_name = scene_summary.parent.name
            completed_at = self.path_mtime(scene_summary)
            try:
                lines = scene_summary.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue

            for line in lines:
                match = STATUS_LINE_RE.match(line.strip())
                parts = line.split()
                if not match or len(parts) < 2:
                    continue
                self.add_result_event(
                    events,
                    camera_id,
                    scene_name,
                    parts[1].replace(".py", ""),
                    self.status_value(match.group(1)),
                    completed_at,
                    source_group=1,
                )

        return sorted(events.values(), key=self.result_sort_key)

    def publish_event(self, event: Dict[str, Any]) -> None:
        self.replay_sequence += 1
        published_event = dict(event)
        published_event["sequence"] = self.replay_sequence
        camera_id = published_event.get("cameraId", DEFAULT_CAMERA_ID)
        self.visible_results.setdefault(camera_id, {}).setdefault(published_event["scene"], {})[published_event["test"]] = published_event["status"]
        self.current_event = published_event
        self.current_events_by_camera[camera_id] = published_event
        self.published_events.append(published_event)
        self.append_log_entry(
            camera_id,
            published_event["scene"],
            published_event["test"],
            f"[Test] {published_event['test']} {self.status_text(published_event['status'])}",
            "TC_LOG",
        )

    def read_event_log_lines(self, event: Dict[str, Any]) -> List[str]:
        log_file = event.get("logFile")
        if not log_file:
            return [f"[{event.get('cameraId', DEFAULT_CAMERA_ID)}] [Test] {event['test']} {self.status_text(event['status'])}"]

        try:
            text = Path(log_file).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return [f"[{event.get('cameraId', DEFAULT_CAMERA_ID)}] [Test] {event['test']} {self.status_text(event['status'])}"]

        filtered_lines = []

        for line in text.replace("\r", "").split("\n"):
            stripped = line.strip()

            if not stripped:
                continue
            
            # DEBUG / INFO 로그 라인
            if DEBUG_LOG_LINE_RE.match(stripped):
                if "[aaudio.hw_burst_min_usec]" in stripped:
                    continue

                filtered_lines.append(stripped)
                continue
            
            # Summary 라인
            if stripped.startswith(DEBUG_SUMMARY_PREFIXES):
                filtered_lines.append(stripped)

        return filtered_lines

    def get_released_log_data(self, since_sequence: int = 0) -> List[Dict[str, Any]]:
        with self.replay_lock:
            self.collect_live_log_updates(self.get_latest_dir())

            if since_sequence > self.log_sequence:
                since_sequence = 0
            return [
                dict(entry)
                for entry in self.log_entries
                if entry.get("sequence", 0) > since_sequence
            ]

    def release_pending_results(self) -> None:
        if not self.pending_results:
            return

        now = time.monotonic()
        if self.replay_interval == 0:
            while self.pending_results:
                event = self.pending_results.pop(0)
                self.publish_event(event)
            self.last_replay_emit_at = now
            return

        if self.last_replay_emit_at is not None and now - self.last_replay_emit_at < self.replay_interval:
            return

        event = self.pending_results.pop(0)
        self.publish_event(event)
        self.last_replay_emit_at = now

    def get_replayed_tc_results(self, its_dir: Path) -> Dict[str, Dict[str, Dict[str, int]]]:
        with self.replay_lock:
            self.reset_replay(its_dir)
            events = self.discover_tc_result_events(its_dir)
            visible_keys = {
                (camera_id, scene_name, test_name)
                for camera_id, camera_results in self.visible_results.items()
                for scene_name, scene_results in camera_results.items()
                for test_name in scene_results
            }
            pending_keys = {
                (event.get("cameraId", DEFAULT_CAMERA_ID), event["scene"], event["test"])
                for event in self.pending_results
            }

            for event in events:
                event_key = (event.get("cameraId", DEFAULT_CAMERA_ID), event["scene"], event["test"])
                if event_key in visible_keys:
                    continue
                if event_key in pending_keys:
                    continue
                self.pending_results.append(event)
                pending_keys.add(event_key)

            self.pending_results.sort(key=self.result_sort_key)
            self.release_pending_results()
            return self.copy_visible_results()

    def parse_tc_results(self, its_dir: Path) -> Dict[str, Dict[str, Dict[str, int]]]:
        return self.get_replayed_tc_results(its_dir)

    def get_updated_structure(
        self,
        file_results: Dict[str, Dict[str, int]] | None = None,
        active_execution: Dict[str, Any] | None = None,
    ) -> List[Dict]:
        if file_results is None:
            latest_dir = self.get_latest_dir()
            all_results = self.parse_tc_results(latest_dir) if latest_dir else {}
            active_camera_id = self.get_active_camera_id(self.get_camera_ids(latest_dir))
            file_results = all_results.get(active_camera_id, {}) if active_camera_id else {}
            active_execution = self.get_active_execution(active_camera_id or None)
        
        updated_list = []
        for item in MASTER_STRUCTURE:
            scene_name = item["scene"]
            new_tests = {}
            for test_key in item["tests"]:
                new_tests[test_key] = file_results.get(scene_name, {}).get(test_key, 0)

            if (
                active_execution
                and active_execution.get("scene") == scene_name
                and active_execution.get("test") in new_tests
            ):
                new_tests[active_execution["test"]] = 4
            updated_list.append({"scene": scene_name, "tests": new_tests})
        return updated_list

    # [이식] adapter에서 검증된 통계 점수화 산출 로직
    def generate_analysis_data(self, file_results: Dict[str, Dict[str, int]] | None = None) -> Dict[str, Any]:
        if file_results is None:
            latest_dir = self.get_latest_dir()
            all_results = self.parse_tc_results(latest_dir) if latest_dir else {}
            active_camera_id = self.get_active_camera_id(self.get_camera_ids(latest_dir))
            file_results = all_results.get(active_camera_id, {}) if active_camera_id else {}
        
        pass_count = 0
        fail_count = 0
        tests_by_metric = {
            "colorAccuracy": {"pass": 0, "fail": 0},
            "resolution": {"pass": 0, "fail": 0},
            "dynamicRange": {"pass": 0, "fail": 0},
            "defectDetect": {"pass": 0, "fail": 0},
        }

        metric_cycle = ("colorAccuracy", "resolution", "dynamicRange", "defectDetect")
        metric_index = 0

        for item in MASTER_STRUCTURE:
            scene_results = file_results.get(item["scene"], {})
            for test_key in item["tests"]:
                status_value = scene_results.get(test_key, 0)
                if status_value == 0:
                    continue

                metric_name = metric_cycle[metric_index % len(metric_cycle)]
                metric_index += 1

                if status_value == self.status_map["PASS"]:
                    pass_count += 1
                    tests_by_metric[metric_name]["pass"] += 1
                elif status_value == self.status_map["FAIL"]:
                    fail_count += 1
                    tests_by_metric[metric_name]["fail"] += 1

        total = pass_count + fail_count
        overall = max(0.0, min(100.0, (pass_count / total) * 100.0)) if total > 0 else 0.0
        
        def calc_score(counts):
            sub_total = counts["pass"] + counts["fail"]
            if sub_total == 0: return overall
            return max(0.0, min(100.0, (counts["pass"] / sub_total) * 100.0))

        status_str = "PASS" if pass_count > 0 and fail_count == 0 else "FAIL" if fail_count else "RUNNING"

        return {
            "status": status_str,
            "metrics": {
                "overallScore": overall,
                "colorAccuracy": calc_score(tests_by_metric["colorAccuracy"]),
                "sharpness": calc_score(tests_by_metric["resolution"]),
                "exposure": calc_score(tests_by_metric["dynamicRange"]),
            },
            "tests": {
                "colorAccuracy": calc_score(tests_by_metric["colorAccuracy"]),
                "resolution": calc_score(tests_by_metric["resolution"]),
                "dynamicRange": calc_score(tests_by_metric["dynamicRange"]),
                "defectDetect": calc_score(tests_by_metric["defectDetect"])
            }
        }

class ItsHandler(BaseHTTPRequestHandler):
    monitor: ITSMonitor
    def log_message(self, *args): pass

    def do_GET(self):
        parsed_url = urlparse(self.path)
        request_path = parsed_url.path

        if request_path == "/its-status.json":
            latest_dir = self.monitor.get_latest_dir()
            file_results = self.monitor.parse_tc_results(latest_dir) if latest_dir else {}
            camera_ids = self.monitor.get_camera_ids(latest_dir)
            active_camera_id = self.monitor.get_active_camera_id(camera_ids)
            active_execution = self.monitor.get_active_execution(active_camera_id or None)
            camera_trees = {
                camera_id: self.monitor.get_updated_structure(
                    file_results.get(camera_id, {}),
                    self.monitor.get_active_execution(camera_id),
                )
                for camera_id in camera_ids
            }
            camera_analysis = {
                camera_id: self.monitor.generate_analysis_data(file_results.get(camera_id, {}))
                for camera_id in camera_ids
            }
            camera_captures = {
                camera_id: self.monitor.get_capture_info(camera_id)
                for camera_id in camera_ids
            }
            camera_active_executions = {
                camera_id: self.monitor.get_active_execution(camera_id)
                for camera_id in camera_ids
            }
            active_results = file_results.get(active_camera_id, {}) if active_camera_id else {}
            # [통합 응답 패키징] 트리 배열과 시각화 지표를 동시에 전달합니다.
            response_data = {
                "tree": self.monitor.get_updated_structure(active_results, active_execution),
                "analysis": self.monitor.generate_analysis_data(active_results),
                "cameras": [
                    {"id": camera_id, "label": camera_id}
                    for camera_id in camera_ids
                ],
                "activeCameraId": active_camera_id,
                "cameraTrees": camera_trees,
                "cameraAnalysis": camera_analysis,
                "cameraCaptures": camera_captures,
                "cameraActiveExecutions": camera_active_executions,
                "run": {
                    "name": latest_dir.name if latest_dir else "",
                    "path": str(latest_dir) if latest_dir else "",
                },
                "activeExecution": active_execution,
                "capture": self.monitor.get_capture_info(active_camera_id or None)
            }
            payload = json.dumps(response_data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        elif request_path == "/latest-capture-image":
            query = parse_qs(parsed_url.query)
            camera_id = query.get("camera", [""])[0] or None
            image_path = self.monitor.get_event_image(camera_id=camera_id)
            if not image_path:
                self.send_response(404)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return

            try:
                payload = image_path.read_bytes()
            except OSError:
                self.send_response(404)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return

            content_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
        elif request_path == "/get-tc-log":
            try:
                query = parse_qs(parsed_url.query)
                camera_id = query.get("camera", [""])[0]
                scene_name = query.get("scene", [""])[0]
                test_name = query.get("test", [""])[0]
                matched_event = None

                for event in reversed(self.monitor.published_events):
                    if (
                        event.get("cameraId") == camera_id
                        and event.get("scene") == scene_name
                        and event.get("test") == test_name
                    ):
                        matched_event = event
                        break

                logs = []

                if matched_event:
                    logs = self.monitor.read_event_log_lines(
                        matched_event
                    )
                payload = json.dumps({
                    "logs": logs
                }).encode("utf-8")
                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "application/json"
                )
                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*"
                )
                self.end_headers()
                self.wfile.write(payload)

            except Exception as e:
                print(f"TC Log Error: {e}")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"logs":[]}')
        elif request_path == "/get-tc-capture":
            try:
                query = parse_qs(parsed_url.query)

                camera_id = query.get("camera", [""])[0]
                scene_name = query.get("scene", [""])[0]
                test_name = query.get("test", [""])[0]

                matched_event = None

                for event in reversed(
                    self.monitor.published_events
                ):
                    if (
                        event.get("cameraId") == camera_id
                        and event.get("scene") == scene_name
                        and event.get("test") == test_name
                    ):
                        matched_event = event
                        break

                if not matched_event:
                    self.send_response(404)
                    self.end_headers()
                    return

                image_path = self.monitor.get_event_image(
                    matched_event
                )

                if not image_path:
                    self.send_response(404)
                    self.end_headers()
                    return

                payload = image_path.read_bytes()

                content_type = (
                    mimetypes.guess_type(image_path.name)[0]
                    or "application/octet-stream"
                )

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    content_type
                )

                self.send_header(
                    "Content-Length",
                    str(len(payload))
                )

                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*"
                )

                self.send_header(
                    "Cache-Control",
                    "no-store"
                )

                self.end_headers()

                self.wfile.write(payload)

            except Exception as e:
                print(f"TC Capture Error: {e}")

                self.send_response(404)
                self.end_headers()
        elif request_path == "/get-live-logs":
            try:
                query = parse_qs(parsed_url.query)
                try:
                    since_sequence = int(query.get("since", ["0"])[0])
                except (TypeError, ValueError):
                    since_sequence = 0

                log_data = self.monitor.get_released_log_data(since_sequence)
                payload = json.dumps(log_data).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(payload)
            except Exception as e:
                print(f"Log Error: {e}")
                self.send_response(200) 
                self.end_headers()
                self.wfile.write(b"[]")
        else:
            self.send_response(404)
            self.end_headers()

def load_server_config(config_path: Path) -> Dict[str, Any]:
    parser = configparser.ConfigParser()

    if config_path.exists():
        parser.read(config_path, encoding="utf-8")

    server_config = parser["server"] if parser.has_section("server") else {}

    def get_config_value(*names: str, fallback: str) -> str:
        for name in names:
            if name in server_config:
                value = server_config.get(name, "").strip()
                if value:
                    return value
        return fallback

    results_dir = get_config_value(
        "results_dir",
        "results-dir",
        fallback=DEFAULT_SERVER_CONFIG["results_dir"],
    )
    port = get_config_value("port", fallback=DEFAULT_SERVER_CONFIG["port"])
    replay_interval = get_config_value(
        "replay_interval",
        "replay-interval",
        fallback=DEFAULT_SERVER_CONFIG["replay_interval"],
    )
    its_tools = get_config_value(
        "ITS_Tools",
        "its_tools",
        "its-tools",
        fallback=DEFAULT_SERVER_CONFIG["its_tools"],
    )

    return {
        "results_dir": Path(results_dir).expanduser(),
        "its_tools": Path(its_tools).expanduser() if its_tools else None,
        "port": int(port),
        "replay_interval": float(replay_interval),
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, type=Path)
    parser.add_argument("--results-dir", type=Path)
    parser.add_argument("--port", type=int)
    parser.add_argument("--replay-interval", type=float)
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_server_config(args.config)

    results_dir = args.results_dir or config["results_dir"]
    its_tools = config["its_tools"]
    port = args.port if args.port is not None else config["port"]
    replay_interval = args.replay_interval if args.replay_interval is not None else config["replay_interval"]

    ItsHandler.monitor = ITSMonitor(results_dir, replay_interval)
    server = ThreadingHTTPServer(("127.0.0.1", port), ItsHandler)
    print(f"================================================")
    print(f"   ITS Integrated Monitor Started")
    print(f"   Config  : {args.config.absolute()}")
    print(f"   Watching: {results_dir.absolute()}")
    if its_tools:
        print(f"   ITS Tools: {its_tools.absolute()}")
    print(f"   API URL : http://localhost:{port}/its-status.json")
    print(f"================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()
