# its_monitor_server.py 수정본

#!/usr/bin/env python3
import argparse
import json
import time
import os
import re
import glob
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, List, Dict

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

STATUS_LINE_RE = re.compile(r"^(PASS|FAIL|SKIP)\s+", re.IGNORECASE)

last_read_positions = {}
last_scene_name = ""

class ITSMonitor:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.status_map = {"PASS": 1, "SKIP": 2, "FAIL": 3}

    def get_latest_dir(self) -> Path | None:
        candidates = [p for p in self.root_dir.glob("CameraITS_*") if p.is_dir()]
        return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None

    def parse_summaries(self, its_dir: Path) -> Dict[str, Dict[str, int]]:
        found_data = {}
        for sf in its_dir.rglob("scene_test_summary.txt"):
            scene_name = sf.parent.name
            found_data[scene_name] = {}
            with open(sf, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        status, test_name = parts[0].upper(), parts[1].replace(".py", "")
                        found_data[scene_name][test_name] = self.status_map.get(status, 0)
        return found_data

    def get_updated_structure(self) -> List[Dict]:
        latest_dir = self.get_latest_dir()
        file_results = self.parse_summaries(latest_dir) if latest_dir else {}
        
        updated_list = []
        for item in MASTER_STRUCTURE:
            scene_name = item["scene"]
            new_tests = {}
            for test_key in item["tests"]:
                new_tests[test_key] = file_results.get(scene_name, {}).get(test_key, 0)
            updated_list.append({"scene": scene_name, "tests": new_tests})
        return updated_list

    # [이식] adapter에서 검증된 통계 점수화 산출 로직
    def generate_analysis_data(self) -> Dict[str, Any]:
        latest_dir = self.get_latest_dir()
        
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

        if latest_dir:
            summary_files = sorted(latest_dir.rglob("scene_test_summary.txt"))
            for summary_file in summary_files:
                try:
                    lines = summary_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                    for line in lines:
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
                except:
                    continue

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
        global last_read_positions
        global last_scene_name
        
        if self.path == "/its-status.json":
            # [통합 응답 패키징] 트리 배열과 시각화 지표를 동시에 전달합니다.
            response_data = {
                "tree": self.monitor.get_updated_structure(),
                "analysis": self.monitor.generate_analysis_data()
            }
            payload = json.dumps(response_data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
            
        elif self.path == "/get-live-logs":
            # (기존의 완벽해진 /get-live-logs 로직 그대로 유지)
            try:
                latest_dir = self.monitor.get_latest_dir()
                log_data = []
                if latest_dir:
                    log_files = sorted(latest_dir.rglob("test_log.INFO"), key=lambda p: p.stat().st_mtime)
                    for log_file in log_files:
                        actual_scene_name = log_file.parent.parent.name 
                        if last_scene_name and last_scene_name != actual_scene_name:
                            log_data.append({
                                "type": "SCENE_CHANGE", 
                                "text": f"--- SCENE_CHANGED_{actual_scene_name} ---" 
                            })
                        last_scene_name = actual_scene_name
        
                        file_path = str(log_file)
                        if file_path not in last_read_positions:
                            last_read_positions[file_path] = 0
                        
                        current_size = log_file.stat().st_size
                        if current_size > last_read_positions[file_path]:
                            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                                f.seek(last_read_positions[file_path])
                                chunk = f.read()
                                if chunk:
                                    last_read_positions[file_path] = f.tell()
                                    lines = chunk.replace('\r', '').split('\n')
                                    for line in lines:
                                        clean_line = line.strip()
                                        if clean_line:
                                            log_data.append({"text": clean_line})

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="/tmp", type=Path)
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()

    ItsHandler.monitor = ITSMonitor(args.results_dir)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), ItsHandler)
    print(f"================================================")
    print(f"   ITS Integrated Monitor Started")
    print(f"   Watching: {args.results_dir.absolute()}")
    print(f"   API URL : http://localhost:{args.port}/its-status.json")
    print(f"================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()