# ITS TC 전시 가이드

## 문서 목적

이 문서는 Camera ITS 대시보드를 전시 현장에서 설명해야 하는 담당자를 위한 안내서입니다.

아래 설명은 전시용으로 이해하기 쉽게 간략화한 내용입니다. 정식 인증 문구라기보다는 관람객에게 쉽게 설명하기 위한 운영 멘트로 사용해 주세요.

## 짧은 소개 멘트

Camera ITS는 안드로이드 카메라가 요구된 품질과 동작 기준을 안정적으로 만족하는지 자동으로 검증하는 테스트 프레임워크입니다.

각 TC는 카메라 기능의 한 가지 약속을 확인합니다. 예를 들어 노출 정확도, 초점 동작, 얼굴 검출, 줌 일관성, 색 안정성, 움직임 처리, 화면 기하 정확성 등을 검사합니다.

라이브 대시보드의 장점은 정적인 보고서를 보여주는 것이 아니라, 실제로 캡처하고 분석하고 결과를 갱신하는 과정을 실시간으로 보여줄 수 있다는 점입니다.

## 전시 담당자 기본 멘트

1. 왼쪽 영역에서 현재 어떤 scene과 어떤 TC가 실행 중인지 볼 수 있습니다.
2. 실시간 로그는 테스트 엔진이 실제로 동작하고 있음을 보여줍니다.
3. 캡처 영역은 현재 분석 중인 실제 이미지나 산출물을 보여줍니다.
4. PASS는 카메라 동작이 기대한 기준과 일치했다는 뜻입니다.
5. FAIL은 이미지 결과나 메타데이터가 기대값과 다르다는 뜻입니다.

## TC 설명

### scene0

- `test_jitter`: 프레임 간 출력이 비정상적으로 흔들리거나 불안정하지 않은지 확인합니다.
- `test_metadata`: 카메라 메타데이터가 정확하고 일관되게 보고되는지 확인합니다.
- `test_request_capture_match`: 요청한 촬영 설정이 실제 결과에 제대로 반영되는지 검증합니다.
- `test_sensor_events`: 센서 이벤트 시각과 카메라 타이밍이 잘 맞는지 확인합니다.
- `test_solid_color_test_pattern`: 카메라가 단색 테스트 패턴을 올바르게 생성하는지 검증합니다.
- `test_test_patterns`: 카메라의 내장 테스트 패턴 기능이 정상 동작하는지 확인합니다.
- `test_tonemap_curve`: 요청한 톤맵 커브가 결과 이미지에 제대로 반영되는지 검증합니다.
- `test_unified_timestamps`: 관련 출력들의 타임스탬프 기준이 통일되어 있는지 확인합니다.
- `test_vibration_restriction`: 카메라 동작 중 진동 제한 관련 정책이 지켜지는지 확인합니다.

### scene1_1

- `test_ae_precapture_trigger`: 자동 노출 precapture 시퀀스가 정상 동작하는지 확인합니다.
- `test_auto_vs_manual`: 자동 제어 결과와 동등한 수동 설정 결과를 비교합니다.
- `test_black_white`: 단순한 장면에서 black level과 white level 처리가 적절한지 확인합니다.
- `test_burst_capture`: 연속 촬영 중에도 안정적으로 동작하는지 검증합니다.
- `test_burst_sameness_manual`: 수동 제어 상태에서 burst 이미지들이 서로 일관된지 확인합니다.
- `test_crop_region_raw`: RAW 출력에서 crop 적용이 올바른지 검증합니다.
- `test_crop_regions`: crop region이 여러 출력에 정확히 반영되는지 확인합니다.
- `test_exposure_x_iso`: ISO와 노출 시간 조합에 대한 반응이 정상적인지 검증합니다.
- `test_latching`: 반복 요청 시 설정이 제대로 유지되는지 확인합니다.
- `test_linearity`: 노출 변화에 따라 밝기가 선형적으로 반응하는지 검증합니다.
- `test_locked_burst`: AE/AWB/AF lock 상태에서 burst 결과가 안정적인지 확인합니다.

### scene1_2

- `test_param_color_correction`: 색 보정 파라미터가 기대한 방식으로 동작하는지 검증합니다.
- `test_param_flash_mode`: flash mode 요청에 따라 결과가 제대로 달라지는지 확인합니다.
- `test_param_noise_reduction`: noise reduction 모드별 동작을 검증합니다.
- `test_param_shading_mode`: lens shading 보정이 모드에 따라 정상 동작하는지 확인합니다.
- `test_param_tonemap_mode`: tonemap 모드별 출력 차이와 동작을 검증합니다.
- `test_post_raw_sensitivity_boost`: RAW 이후 sensitivity boost 동작을 확인합니다.
- `test_raw_exposure`: RAW 노출 반응과 스케일링이 정상인지 검증합니다.
- `test_reprocess_noise_reduction`: 재처리 과정에서 noise reduction 동작을 확인합니다.
- `test_tonemap_sequence`: 여러 프레임에 걸친 tonemap 동작 일관성을 검증합니다.
- `test_yuv_plus_dng`: YUV와 DNG 동시 촬영이 정상 동작하는지 확인합니다.

### scene1_3

- `test_capture_result`: capture result에 포함된 상세 메타데이터가 유효한지 검증합니다.
- `test_dng_noise_model`: DNG noise model이 실제 캡처 특성과 맞는지 확인합니다.
- `test_ev_compensation`: 노출 보정 값에 대한 반응이 정상적인지 검증합니다.
- `test_exposure_time_priority`: exposure-time-priority 제어가 기대한 대로 동작하는지 확인합니다.
- `test_jpeg`: 기본 JPEG 촬영 동작과 결과 무결성을 검증합니다.
- `test_raw_burst_sensitivity`: RAW burst 상황에서 sensitivity 변화 반응을 확인합니다.
- `test_raw_sensitivity`: RAW 출력이 sensitivity 설정에 맞게 반응하는지 검증합니다.
- `test_sensitivity_priority`: sensitivity-priority 제어 동작을 확인합니다.
- `test_yuv_jpeg_all`: YUV와 JPEG 조합 촬영이 정상 지원되는지 확인합니다.
- `test_yuv_plus_jpeg`: YUV와 JPEG 동시 촬영 동작을 검증합니다.
- `test_yuv_plus_raw`: YUV와 RAW 동시 촬영 동작을 검증합니다.

### scene2_a

- `test_display_p3`: Display P3 색역 관련 동작이 정상인지 확인합니다.
- `test_effects`: 카메라 effect 모드들이 기대한 방식으로 동작하는지 검증합니다.
- `test_exposure_keys_consistent`: 노출 관련 메타데이터 값들 사이의 일관성을 확인합니다.
- `test_format_combos`: 출력 포맷 조합 지원이 정상적인지 검증합니다.
- `test_num_faces`: 장면 내 얼굴 수를 올바르게 검출하는지 확인합니다.
- `test_reprocess_uv_swap`: 재처리 과정에서 UV plane 처리 오류가 없는지 확인합니다.

### scene2_b

- `test_preview_num_faces`: preview 모드에서 얼굴 수 검출이 정상인지 확인합니다.
- `test_yuv_jpeg_capture_sameness`: YUV와 JPEG 캡처 결과가 서로 일관된지 확인합니다.

### scene2_c

- `test_camera_launch_perf_class`: 카메라 실행 속도가 성능 기준을 만족하는지 측정합니다.
- `test_default_camera_hdr`: 기본 카메라의 HDR 동작이 기대한 기준에 맞는지 검증합니다.
- `test_jpeg_capture_perf_class`: JPEG 캡처 속도가 성능 기준을 만족하는지 측정합니다.
- `test_num_faces`: 이 장면 조건에서 얼굴 수 검출이 정상인지 확인합니다.

### scene2_d

- `test_autoframing`: autoframing 동작과 피사체 프레이밍 로직을 확인합니다.
- `test_num_faces`: 이 장면에서 얼굴 수 검출이 정상인지 확인합니다.
- `test_preview_num_faces`: preview 상태에서 얼굴 수 검출이 정상인지 확인합니다.

### scene2_e

- `test_continuous_picture`: 연속 사진 촬영 동작이 정상인지 검증합니다.
- `test_num_faces`: 이 장면에서 얼굴 수 검출이 정상인지 확인합니다.

### scene2_f

- `test_preview_num_faces`: 이 장면 변형에서 preview 얼굴 검출이 정상인지 확인합니다.

### scene2_g

- `test_preview_num_faces`: 옆얼굴 형태의 장면에서도 얼굴 검출이 정상인지 확인합니다.

### scene3

- `test_edge_enhancement`: 선명화와 edge enhancement 동작을 검증합니다.
- `test_flip_mirror`: 이미지 방향, 좌우반전, 미러 처리가 정확한지 확인합니다.
- `test_imu_drift`: IMU drift가 관련 측정에 문제를 주지 않는지 확인합니다.
- `test_landscape_to_portrait`: 가로/세로 방향 전환 처리 동작을 검증합니다.
- `test_lens_movement_reporting`: 렌즈 이동 관련 메타데이터가 정확히 보고되는지 확인합니다.
- `test_reprocess_edge_enhancement`: 재처리 과정의 sharpening 동작을 검증합니다.

### scene4

- `test_30_60fps_preview_fov_match`: 30fps와 60fps preview 간 시야각 차이가 없는지 확인합니다.
- `test_aspect_ratio_and_crop`: 화면 비율과 crop 처리 정확성을 검증합니다.
- `test_multi_camera_alignment`: 여러 카메라 모듈 간 정렬 상태를 확인합니다.
- `test_preview_aspect_ratio_and_crop`: preview의 aspect ratio와 crop 동작을 검증합니다.
- `test_preview_stabilization_fov`: preview stabilization이 시야각에 미치는 영향을 확인합니다.
- `test_video_aspect_ratio_and_crop`: video 모드에서 aspect ratio와 crop 동작을 검증합니다.

### scene6

- `test_in_sensor_zoom`: 센서 기반 줌 동작이 정확한지 확인합니다.
- `test_low_latency_zoom`: 줌 응답 속도와 부드러움을 검증합니다.
- `test_preview_video_zoom_match`: preview zoom과 video zoom이 시각적으로 일치하는지 확인합니다.
- `test_preview_zoom`: preview 줌 배율과 프레이밍이 정상인지 확인합니다.
- `test_session_characteristics_zoom`: 줌 관련 session metadata가 정상인지 확인합니다.
- `test_zoom`: 정지화상 줌 동작 전반을 검증합니다.

### scene7

- `test_multi_camera_switch`: 카메라 모듈 전환이 자연스럽고 정확한지 확인합니다.

### scene8

- `test_ae_awb_regions`: AE와 AWB metering region 설정이 출력에 제대로 반영되는지 확인합니다.
- `test_color_correction_mode_cct`: 색온도 기반 color correction 동작을 검증합니다.

### scene9

- `test_jpeg_high_entropy`: 복잡한 장면에서도 JPEG 품질이 안정적인지 확인합니다.
- `test_jpeg_quality`: JPEG 품질 설정값 반영 동작을 검증합니다.

### scene_hdr

- `test_hdr_extension`: HDR extension 촬영 동작을 검증합니다.

### scene_low_light

- `test_low_light_boost_extension`: 저조도 boost extension 동작을 확인합니다.
- `test_night_extension`: night extension 동작이 정상인지 검증합니다.

### scene6_tele

- `test_preview_zoom_tele`: tele 카메라의 preview zoom 동작을 확인합니다.
- `test_zoom_tele`: tele 카메라의 정지화상 zoom 동작을 확인합니다.

### scene7_tele

- `test_multi_camera_switch_tele`: tele 카메라가 포함된 모듈 전환 동작을 검증합니다.

### scene_video

- `test_preview_frame_drop`: 움직임 장면에서 preview frame drop이 없는지 확인합니다.

## 실시간 로그만 보여주는 것보다 더 좋은 전시 아이디어

현재 실시간 로그는 기술 신뢰도를 보여주는 데는 좋지만, 전시에서는 그것만으로는 관람객의 이해와 몰입을 끌어내기 어렵습니다.

### 추천 전시 화면 구성

1. 메인 영역: 현재 scene 이름, 현재 TC 이름, 현재 카메라, 경과 시간 표시
2. 라이브 이미지 영역: 최신 캡처 이미지 또는 DUT 화면 미러링
3. 결과 요약 영역: PASS / FAIL / RUNNING 개수와 진행률 표시
4. 설명 패널: 현재 TC가 무엇을 검사하는지 한 줄 설명 표시
5. 로그 영역: 화면 하단이나 우측에 작게 두어 신뢰성 보강용으로 사용

### 이 방식이 더 좋은 이유

- 관람객은 텍스트 로그보다 이미지와 상태 카드에 더 빠르게 반응합니다.
- 전시 담당자가 raw log를 일일이 번역하지 않아도 됩니다.
- PASS와 FAIL이 실제 이미지, 현재 TC 설명과 함께 보이면 훨씬 직관적입니다.
- 멀리서도 무슨 데모인지 이해하기 쉬워집니다.

### 더 강한 전시 모드 아이디어

- 현재 테스트 카드 모드: 현재 TC, 목적, 라이브 이미지, 상태만 크게 표시
- Before / Reference / Current 비교 모드: 기준 이미지와 현재 캡처를 나란히 비교
- 카메라 품질 레이더 모드: 색, 노출, 줌, 기하, 안정성 같은 품질 축으로 요약
- 스토리 모드 자동 전환: 10초~20초마다 라이브 이미지, 현재 TC 설명, 점수 요약을 자동 순환

## 로그 충분성 점검 결과

현재 테스트 소스 기준으로 중간 진행 로그가 얼마나 있는지 간단히 점검했습니다.

- 검사한 `test_*.py` 파일 수: `108`
- 로그 호출이 `0`개인 파일 수: `4`
- 로그 호출이 `1`개 이하인 파일 수: `6`
- 로그 호출이 `2`개 이하인 파일 수: `12`
- 파일당 평균 로그 호출 수: 약 `8.72`

### 로그가 특히 적은 TC

- `scene0/test_sensor_events.py`
- `scene1_1/test_burst_sameness_manual.py`
- `scene1_1/test_latching.py`
- `scene1_1/test_linearity.py`
- `scene1_2/test_param_color_correction.py`
- `scene1_3/test_raw_burst_sensitivity.py`
- `scene2_c/test_camera_launch_perf_class.py`
- `scene2_c/test_jpeg_capture_perf_class.py`
- `scene2_e/test_continuous_picture.py`
- `scene3/test_landscape_to_portrait.py`
- `scene8/test_color_correction_mode_cct.py`

### 현재 로그에서 아쉬운 점

- 각 TC 시작 시점에 `TC START` 같은 명확한 시작 배너가 없습니다.
- `opening session`, `running 3A`, `capturing`, `analyzing`, `comparing`, `writing artifacts` 같은 단계 로그가 부족합니다.
- 오래 걸리는 테스트에서 heartbeat 로그가 없어 화면이 멈춘 것처럼 보일 수 있습니다.
- 저장된 이미지 경로, plot 경로, 핵심 metric 값 같은 요약 로그가 더 있으면 전시에 좋습니다.
- retry가 발생했을 때 이유가 더 친절하게 보여지면 좋습니다.
- scene 전환 메시지가 비개발자 기준으로는 아직 다소 기술적입니다.

## 다음 로그 개선 추천

1. `run_all_tests.py`에서 각 TC 시작 전에 한 줄짜리 `START` 배너를 추가합니다.
2. TC 이름별 설명 테이블을 두고 `이 테스트가 무엇을 검사하는지` 한 줄 로그를 같이 출력합니다.
3. 로그가 적은 TC에 capture, analysis, assertion 단계 로그를 추가합니다.
4. 5초~10초 이상 조용한 테스트에는 heartbeat 로그를 넣습니다.
5. HTML 화면에 raw log만이 아니라 현재 TC의 핵심 metric 하나를 함께 보여줍니다.

## 전시 운영 팁

- 관람객이 가까이 있을 때는 raw log를 보여주며 실제 엔진이 도는 모습을 강조하세요.
- 멀리 있는 관람객에게는 현재 TC 설명과 라이브 이미지가 더 중요합니다.
- 수동 scene 전환이 필요한 경우에는 실제 광학 조건과 촬영 환경까지 검증하는 테스트라는 점을 설명하면 이해가 쉽습니다.
