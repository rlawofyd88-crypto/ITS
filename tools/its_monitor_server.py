#!/usr/bin/env python3
import argparse
import json
import time
import os
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
            with open(sf, "r", encoding="utf-8") as f:
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
            # JS 구조와 동일하게 tests를 객체로 변환하며 값을 채움
            new_tests = {}
            for test_key in item["tests"]:
                # 파일에 결과가 있으면 그 값(1~3), 없으면 0(WAIT)
                new_tests[test_key] = file_results.get(scene_name, {}).get(test_key, 0)
            
            updated_list.append({"scene": scene_name, "tests": new_tests})
        
        return updated_list



class ItsHandler(BaseHTTPRequestHandler):
    monitor: ITSMonitor
    def log_message(self, *args): pass

    def do_GET(self):
        global last_read_positions
        global last_scene_name
        if self.path == "/its-status.json":
            payload = json.dumps(self.monitor.get_updated_structure()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
        elif self.path == "/get-live-logs":
            global last_scene_name
            try:
                latest_dir = self.monitor.get_latest_dir()
                log_data = []
        
                if latest_dir:
                    # 1. 최신 로그 파일들을 순회
                    log_files = sorted(latest_dir.rglob("test_log.INFO"), key=lambda p: p.stat().st_mtime)
                    
                    for log_file in log_files:
                        # [핵심 수정] 파일의 부모 폴더(예: test_jpeg)의 부모(예: scene1_1) 이름을 가져옵니다.
                        actual_scene_name = log_file.parent.parent.parent.name 
        
                        # 2. 진짜 Scene 폴더 이름이 바뀌었는지 체크
                        #print(f"last_scene_name: {last_scene_name}, actual_scene_name: {actual_scene_name}")
                        if last_scene_name and last_scene_name != actual_scene_name:
                            log_data.append({
                                "type": "SCENE_CHANGE", 
                                "text": f"--- SCENE_CHANGED_{actual_scene_name} ---" 
                            })
                        
                        last_scene_name = actual_scene_name # 현재 Scene 저장
        
                        # 3. 기존 파일 읽기 로직 시작
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
                                    # splitlines 대신 \n으로 쪼개서 마지막 줄 누락 방지
                                    lines = chunk.replace('\r', '').split('\n')
                                    for line in lines:
                                        clean_line = line.strip()
                                        if clean_line:
                                            log_data.append({"text": clean_line})

                # 응답 전송 부분
                payload = json.dumps(log_data).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(payload)

            except Exception as e:
                print(f"Log Error: {e}")
                # 에러 발생 시 빈 배열이라도 응답하여 브라우저 에러 방지
                self.send_response(200) 
                self.end_headers()
                self.wfile.write(b"[]")
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_time_ordered_logs(self):
        latest_dir = self.monitor.get_latest_dir()
        if not latest_dir:
            return []

        all_logs = []
        # 모든 scene 하위의 test_log.INFO 파일들을 탐색
        log_files = latest_dir.rglob("test_log.INFO") # 혹은 *.txt

        for log_file in log_files:
            # 파일 수정 시간을 기준으로 로그 라인 생성 (실제 파일 내용 대신 파일 정보를 활용)
            mtime = time.ctime(log_file.stat().st_mtime)
            scene_name = log_file.parent.parent.name
            test_name = log_file.parent.name

            # 실제 파일을 읽어 첫 3줄 정도만 가져와서 리스트화 (시뮬레이션용)
            try:
                with open(log_file, "r") as f:
                    content = [line.strip() for line in f.readlines()[:3]]
                    for line in content:
                        if line:
                            all_logs.append({
                                "time": mtime,
                                "scene": scene_name,
                                "test": test_name,
                                "text": line
                            })
            except:
                continue

        # 시간 순서대로 정렬
        return sorted(all_logs, key=lambda x: x['time'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="/tmp", type=Path)
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args()

    ItsHandler.monitor = ITSMonitor(args.results_dir)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), ItsHandler)

    print(f"================================================")
    print(f"   ITS Results Monitor Started")
    print(f"   Watching: {args.results_dir.absolute()}")
    print(f"   API URL : http://localhost:{args.port}/its-status.json")
    print(f"================================================")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()