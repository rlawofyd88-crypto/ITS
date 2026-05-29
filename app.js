const clock = document.querySelector("#clock");
const scoreValue = document.querySelector("#scoreValue");
const colorValue = document.querySelector("#colorValue");
const sharpnessValue = document.querySelector("#sharpnessValue");
const exposureValue = document.querySelector("#exposureValue");
const resultBadge = document.querySelector("#resultBadge");
const colorScore = document.querySelector("#colorScore");
const resolutionScore = document.querySelector("#resolutionScore");
const dynamicRangeScore = document.querySelector("#dynamicRangeScore");
const defectScore = document.querySelector("#defectScore");
const colorBar = document.querySelector("#colorBar");
const resolutionBar = document.querySelector("#resolutionBar");
const dynamicRangeBar = document.querySelector("#dynamicRangeBar");
const defectBar = document.querySelector("#defectBar");
//const compareSlider = document.querySelector("#compareSlider");
//const referenceImage = document.querySelector("#referenceImage");
//const divider = document.querySelector("#divider");
const dutMirror = document.querySelector("#dutMirror");
const liveBadge = document.querySelector("#liveBadge");
const cameraScene = document.querySelector("#cameraScene");
const runNameBadge = document.querySelector("#runNameBadge");
const cameraTabs = document.querySelector("#cameraTabs");

const tcListContainer = document.querySelector("#tcList");

const logTabsContainer = document.querySelector("#logTabs");
const logPanelsContainer = document.querySelector("#logPanels");

const captureTabsContainer = document.querySelector("#captureTabs");

const capturePanelsContainer = document.querySelector(".capture-panels");
const currentTestScene = document.querySelector("#currentTestScene");
const currentTestName = document.querySelector("#currentTestName");
const currentTestOrder = document.querySelector("#currentTestOrder");
const currentTestDescription = document.querySelector("#currentTestDescription");
const logFilterGroup = document.querySelector("#logFilterGroup");

let tcLogTabs = [];

let currentCaptureTabKey = "";

const MAX_TC_LOG_TABS = 5;

/**
 * 스네이크 케이스(test_example_name)를 파스칼 케이스(ExampleName)로 변환합니다.
 * @param {string} name 
 */
function formatTcName(name) {
    return name
        .replace(/^test_/, '') // 앞의 'test_' 제거
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join('');
}
// --- CameraITS 테스트 구조 정의 ---
let itsTestStructure = [
  {
    scene: "scene0",
    tests: {
      test_jitter: 0,
      test_metadata: 0,
      test_request_capture_match: 0,
      test_sensor_events: 0,
      test_solid_color_test_pattern: 0,
      test_test_patterns: 0,
      test_tonemap_curve: 0,
      test_unified_timestamps: 0,
      test_vibration_restriction: 0
    }
  },
  {
    scene: "scene1_1",
    tests: {
      test_ae_precapture_trigger: 0,
      test_auto_vs_manual: 0,
      test_black_white: 0,
      test_burst_capture: 0,
      test_burst_sameness_manual: 0,
      test_crop_region_raw: 0,
      test_crop_regions: 0,
      test_exposure_x_iso: 0,
      test_latching: 0,
      test_linearity: 0,
      test_locked_burst: 0
    }
  },
  {
    scene: "scene1_2",
    tests: {
      test_param_color_correction: 0,
      test_param_flash_mode: 0,
      test_param_noise_reduction: 0,
      test_param_shading_mode: 0,
      test_param_tonemap_mode: 0,
      test_post_raw_sensitivity_boost: 0,
      test_raw_exposure: 0,
      test_reprocess_noise_reduction: 0,
      test_tonemap_sequence: 0,
      test_yuv_plus_dng: 0
    }
  },
  {
    scene: "scene1_3",
    tests: {
      test_capture_result: 0,
      test_dng_noise_model: 0,
      test_ev_compensation: 0,
      test_exposure_time_priority: 0,
      test_jpeg: 0,
      test_raw_burst_sensitivity: 0,
      test_raw_sensitivity: 0,
      test_sensitivity_priority: 0,
      test_yuv_jpeg_all: 0,
      test_yuv_plus_jpeg: 0,
      test_yuv_plus_raw: 0
    }
  },
  {
    scene: "scene2_a",
    tests: {
      test_display_p3: 0,
      test_effects: 0,
      test_exposure_keys_consistent: 0,
      test_format_combos: 0,
      test_num_faces: 0,
      test_reprocess_uv_swap: 0
    }
  },
  {
    scene: "scene2_b",
    tests: {
      test_preview_num_faces: 0,
      test_yuv_jpeg_capture_sameness: 0
    }
  },
  {
    scene: "scene2_c",
    tests: {
      test_camera_launch_perf_class: 0,
      test_default_camera_hdr: 0,
      test_jpeg_capture_perf_class: 0,
      test_num_faces: 0
    }
  },
  {
    scene: "scene2_d",
    tests: {
      test_autoframing: 0,
      test_num_faces: 0,
      test_preview_num_faces: 0
    }
  },
  {
    scene: "scene2_e",
    tests: {
      test_continuous_picture: 0,
      test_num_faces: 0
    }
  },
  {
    scene: "scene2_f",
    tests: {
      test_preview_num_faces: 0
    }
  },
  {
    scene: "scene2_g",
    tests: {
      test_preview_num_faces: 0
    }
  },
  {
    scene: "scene3",
    tests: {
      test_edge_enhancement: 0,
      test_flip_mirror: 0,
      test_imu_drift: 0,
      test_landscape_to_portrait: 0,
      test_lens_movement_reporting: 0,
      test_reprocess_edge_enhancement: 0
    }
  },
  {
    scene: "scene4",
    tests: {
      test_30_60fps_preview_fov_match: 0,
      test_aspect_ratio_and_crop: 0,
      test_multi_camera_alignment: 0,
      test_preview_aspect_ratio_and_crop: 0,
      test_preview_stabilization_fov: 0,
      test_video_aspect_ratio_and_crop: 0
    }
  },
  {
    scene: "scene6",
    tests: {
      test_in_sensor_zoom: 0,
      test_low_latency_zoom: 0,
      test_preview_video_zoom_match: 0,
      test_preview_zoom: 0,
      test_session_characteristics_zoom: 0,
      test_zoom: 0
    }
  },
  {
    scene: "scene7",
    tests: {
      test_multi_camera_switch: 0
    }
  },
  {
    scene: "scene8",
    tests: {
      test_ae_awb_regions: 0,
      test_color_correction_mode_cct: 0
    }
  },
  {
    scene: "scene9",
    tests: {
      test_jpeg_high_entropy: 0,
      test_jpeg_quality: 0
    }
  },
  {
    scene: "scene_hdr",
    tests: {
      test_hdr_extension: 0
    }
  },
  {
    scene: "scene_low_light",
    tests: {
      test_low_light_boost_extension: 0,
      test_night_extension: 0
    }
  },
  {
    scene: "scene6_tele",
    tests: {
      test_preview_zoom_tele: 0,
      test_zoom_tele: 0
    }
  },
  {
    scene: "scene7_tele",
    tests: {
      test_multi_camera_switch_tele: 0
    }
  },
  {
    scene: "scene_video",
    tests: {
      test_preview_frame_drop: 0
    }
  }
];

const tcDescriptionMap = {
  scene0: {
    test_jitter: "프레임 간 출력이 비정상적으로 흔들리거나 불안정하지 않은지 확인합니다.",
    test_metadata: "카메라 메타데이터가 정확하고 일관되게 보고되는지 확인합니다.",
    test_request_capture_match: "요청한 촬영 설정이 실제 결과에 제대로 반영되는지 검증합니다.",
    test_sensor_events: "센서 이벤트 시각과 카메라 타이밍이 잘 맞는지 확인합니다.",
    test_solid_color_test_pattern: "카메라가 단색 테스트 패턴을 올바르게 생성하는지 검증합니다.",
    test_test_patterns: "카메라의 내장 테스트 패턴 기능이 정상 동작하는지 확인합니다.",
    test_tonemap_curve: "요청한 톤맵 커브가 결과 이미지에 제대로 반영되는지 검증합니다.",
    test_unified_timestamps: "관련 출력들의 타임스탬프 기준이 통일되어 있는지 확인합니다.",
    test_vibration_restriction: "카메라 동작 중 진동 제한 관련 정책이 지켜지는지 확인합니다."
  },
  scene1_1: {
    test_ae_precapture_trigger: "자동 노출 precapture 시퀀스가 정상 동작하는지 확인합니다.",
    test_auto_vs_manual: "자동 제어 결과와 동등한 수동 설정 결과를 비교합니다.",
    test_black_white: "단순한 장면에서 black level과 white level 처리가 적절한지 확인합니다.",
    test_burst_capture: "연속 촬영 중에도 안정적으로 동작하는지 검증합니다.",
    test_burst_sameness_manual: "수동 제어 상태에서 burst 이미지들이 서로 일관된지 확인합니다.",
    test_crop_region_raw: "RAW 출력에서 crop 적용이 올바른지 검증합니다.",
    test_crop_regions: "crop region이 여러 출력에 정확히 반영되는지 확인합니다.",
    test_exposure_x_iso: "ISO와 노출 시간 조합에 대한 반응이 정상적인지 검증합니다.",
    test_latching: "반복 요청 시 설정이 제대로 유지되는지 확인합니다.",
    test_linearity: "노출 변화에 따라 밝기가 선형적으로 반응하는지 검증합니다.",
    test_locked_burst: "AE/AWB/AF lock 상태에서 burst 결과가 안정적인지 확인합니다."
  },
  scene1_2: {
    test_param_color_correction: "색 보정 파라미터가 기대한 방식으로 동작하는지 검증합니다.",
    test_param_flash_mode: "flash mode 요청에 따라 결과가 제대로 달라지는지 확인합니다.",
    test_param_noise_reduction: "noise reduction 모드별 동작을 검증합니다.",
    test_param_shading_mode: "lens shading 보정이 모드에 따라 정상 동작하는지 확인합니다.",
    test_param_tonemap_mode: "tonemap 모드별 출력 차이와 동작을 검증합니다.",
    test_post_raw_sensitivity_boost: "RAW 이후 sensitivity boost 동작을 확인합니다.",
    test_raw_exposure: "RAW 노출 반응과 스케일링이 정상인지 검증합니다.",
    test_reprocess_noise_reduction: "재처리 과정에서 noise reduction 동작을 확인합니다.",
    test_tonemap_sequence: "여러 프레임에 걸친 tonemap 동작 일관성을 검증합니다.",
    test_yuv_plus_dng: "YUV와 DNG 동시 촬영이 정상 동작하는지 확인합니다."
  },
  scene1_3: {
    test_capture_result: "capture result에 포함된 상세 메타데이터가 유효한지 검증합니다.",
    test_dng_noise_model: "DNG noise model이 실제 캡처 특성과 맞는지 확인합니다.",
    test_ev_compensation: "노출 보정 값에 대한 반응이 정상적인지 검증합니다.",
    test_exposure_time_priority: "exposure-time-priority 제어가 기대한 대로 동작하는지 확인합니다.",
    test_jpeg: "기본 JPEG 촬영 동작과 결과 무결성을 검증합니다.",
    test_raw_burst_sensitivity: "RAW burst 상황에서 sensitivity 변화 반응을 확인합니다.",
    test_raw_sensitivity: "RAW 출력이 sensitivity 설정에 맞게 반응하는지 검증합니다.",
    test_sensitivity_priority: "sensitivity-priority 제어 동작을 확인합니다.",
    test_yuv_jpeg_all: "YUV와 JPEG 조합 촬영이 정상 지원되는지 확인합니다.",
    test_yuv_plus_jpeg: "YUV와 JPEG 동시 촬영 동작을 검증합니다.",
    test_yuv_plus_raw: "YUV와 RAW 동시 촬영 동작을 검증합니다."
  },
  scene2_a: {
    test_display_p3: "Display P3 색역 관련 동작이 정상인지 확인합니다.",
    test_effects: "카메라 effect 모드들이 기대한 방식으로 동작하는지 검증합니다.",
    test_exposure_keys_consistent: "노출 관련 메타데이터 값들 사이의 일관성을 확인합니다.",
    test_format_combos: "출력 포맷 조합 지원이 정상적인지 검증합니다.",
    test_num_faces: "장면 내 얼굴 수를 올바르게 검출하는지 확인합니다.",
    test_reprocess_uv_swap: "재처리 과정에서 UV plane 처리 오류가 없는지 확인합니다."
  },
  scene2_b: {
    test_preview_num_faces: "preview 모드에서 얼굴 수 검출이 정상인지 확인합니다.",
    test_yuv_jpeg_capture_sameness: "YUV와 JPEG 캡처 결과가 서로 일관된지 확인합니다."
  },
  scene2_c: {
    test_camera_launch_perf_class: "카메라 실행 속도가 성능 기준을 만족하는지 측정합니다.",
    test_default_camera_hdr: "기본 카메라의 HDR 동작이 기대한 기준에 맞는지 검증합니다.",
    test_jpeg_capture_perf_class: "JPEG 캡처 속도가 성능 기준을 만족하는지 측정합니다.",
    test_num_faces: "이 장면 조건에서 얼굴 수 검출이 정상인지 확인합니다."
  },
  scene2_d: {
    test_autoframing: "autoframing 동작과 피사체 프레이밍 로직을 확인합니다.",
    test_num_faces: "이 장면에서 얼굴 수 검출이 정상인지 확인합니다.",
    test_preview_num_faces: "preview 상태에서 얼굴 수 검출이 정상인지 확인합니다."
  },
  scene2_e: {
    test_continuous_picture: "연속 사진 촬영 동작이 정상인지 검증합니다.",
    test_num_faces: "이 장면에서 얼굴 수 검출이 정상인지 확인합니다."
  },
  scene2_f: {
    test_preview_num_faces: "이 장면 변형에서 preview 얼굴 검출이 정상인지 확인합니다."
  },
  scene2_g: {
    test_preview_num_faces: "옆얼굴 형태의 장면에서도 얼굴 검출이 정상인지 확인합니다."
  },
  scene3: {
    test_edge_enhancement: "선명화와 edge enhancement 동작을 검증합니다.",
    test_flip_mirror: "이미지 방향, 좌우반전, 미러 처리가 정확한지 확인합니다.",
    test_imu_drift: "IMU drift가 관련 측정에 문제를 주지 않는지 확인합니다.",
    test_landscape_to_portrait: "가로/세로 방향 전환 처리 동작을 검증합니다.",
    test_lens_movement_reporting: "렌즈 이동 관련 메타데이터가 정확히 보고되는지 확인합니다.",
    test_reprocess_edge_enhancement: "재처리 과정의 sharpening 동작을 검증합니다."
  },
  scene4: {
    test_30_60fps_preview_fov_match: "30fps와 60fps preview 간 시야각 차이가 없는지 확인합니다.",
    test_aspect_ratio_and_crop: "화면 비율과 crop 처리 정확성을 검증합니다.",
    test_multi_camera_alignment: "여러 카메라 모듈 간 정렬 상태를 확인합니다.",
    test_preview_aspect_ratio_and_crop: "preview의 aspect ratio와 crop 동작을 검증합니다.",
    test_preview_stabilization_fov: "preview stabilization이 시야각에 미치는 영향을 확인합니다.",
    test_video_aspect_ratio_and_crop: "video 모드에서 aspect ratio와 crop 동작을 검증합니다."
  },
  scene6: {
    test_in_sensor_zoom: "센서 기반 줌 동작이 정확한지 확인합니다.",
    test_low_latency_zoom: "줌 응답 속도와 부드러움을 검증합니다.",
    test_preview_video_zoom_match: "preview zoom과 video zoom이 시각적으로 일치하는지 확인합니다.",
    test_preview_zoom: "preview 줌 배율과 프레이밍이 정상인지 확인합니다.",
    test_session_characteristics_zoom: "줌 관련 session metadata가 정상인지 확인합니다.",
    test_zoom: "정지화상 줌 동작 전반을 검증합니다."
  },
  scene7: {
    test_multi_camera_switch: "카메라 모듈 전환이 자연스럽고 정확한지 확인합니다."
  },
  scene8: {
    test_ae_awb_regions: "AE와 AWB metering region 설정이 출력에 제대로 반영되는지 확인합니다.",
    test_color_correction_mode_cct: "색온도 기반 color correction 동작을 검증합니다."
  },
  scene9: {
    test_jpeg_high_entropy: "복잡한 장면에서도 JPEG 품질이 안정적인지 확인합니다.",
    test_jpeg_quality: "JPEG 품질 설정값 반영 동작을 검증합니다."
  },
  scene_hdr: {
    test_hdr_extension: "HDR extension 촬영 동작을 검증합니다."
  },
  scene_low_light: {
    test_low_light_boost_extension: "저조도 boost extension 동작을 확인합니다.",
    test_night_extension: "night extension 동작이 정상인지 검증합니다."
  },
  scene6_tele: {
    test_preview_zoom_tele: "tele 카메라의 preview zoom 동작을 확인합니다.",
    test_zoom_tele: "tele 카메라의 정지화상 zoom 동작을 확인합니다."
  },
  scene7_tele: {
    test_multi_camera_switch_tele: "tele 카메라가 포함된 모듈 전환 동작을 검증합니다."
  },
  scene_video: {
    test_preview_frame_drop: "움직임 장면에서 preview frame drop이 없는지 확인합니다."
  }
};

const tcOrderList = itsTestStructure.flatMap((item) =>
  Object.keys(item.tests).map((testName) => ({
    scene: item.scene,
    test: testName
  }))
);
const tcOrderMap = new Map(
  tcOrderList.map((entry, index) => [
    `${entry.scene}:${entry.test}`,
    index + 1
  ])
);
const totalTcCount = tcOrderList.length;

let needsClear = false;
let externalDataActive = false;
const params = new URLSearchParams(window.location.search);
const dataEndpoint = params.get("data");
const monitorEndpoint = params.get("monitor") || "http://localhost:8775";
const hasCustomLiveFeed = params.has("feed");
const liveFeedPath = params.get("feed") || `${monitorEndpoint}/latest-capture-image`;
const liveStatePath = params.get("live_state") || "./data/live-demo-state.json";
const TC_STATUS_POLL_MS = 500;
const LOG_POLL_MS = 500;
const LOG_RENDER_INTERVAL_MS = 16;
const LOG_RESULT_PAUSE_MS = 60;
const LOG_OUTPUT_MAX_WAIT_MS = 420;
const LOG_OUTPUT_IDLE_SLEEP_MS = 20;
const LOG_OUTPUT_EMPTY_DELAY_MS = 40;
const LOG_TIMESTAMP_RE = /^(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})\.(\d+)/;
let liveFeedObjectUrl = null;
let currentCaptureKey = "";
let lastAppliedCaptureSequence = 0;
let statusUpdateInProgress = false;
let currentTcFocus = { cameraId: "", scene: "", test: "" };
let pendingTcUpdates = [];
let pendingTcFocus = null;
let cameraList = [];
let knownCameraIds = [];
let selectedCameraId = "";
let cameraTrees = {};
let cameraAnalyses = {};
let cameraCaptures = {};
let cameraActiveExecutions = {};
let currentLogFilter = "ALL";

function getLogLevel(text) {
  if (text.includes(" DEBUG ") || text.startsWith("DEBUG ") || text.includes("DEBUG:")) {
    return "DEBUG";
  }
  if (text.includes(" INFO ") || text.startsWith("INFO ") || text.includes("INFO:")) {
    return "INFO";
  }
  return "INFO";
}

function shouldShowLogLevel(level) {
  if (currentLogFilter === "ALL") {
    return true;
  }
  return level === currentLogFilter;
}

function applyLogFilterToPanels() {
  document.querySelectorAll(".log-line-raw").forEach((line) => {
    const level = line.dataset.logLevel || "INFO";
    line.classList.toggle("log-line-hidden", !shouldShowLogLevel(level));
  });
}

function setLogFilter(filter) {
  currentLogFilter = filter;
  if (logFilterGroup) {
    logFilterGroup.querySelectorAll(".log-filter-button").forEach((button) => {
      button.classList.toggle("active", button.dataset.logFilter === filter);
    });
  }
  applyLogFilterToPanels();
}

function updateClock() {
  const now = new Date();
  clock.textContent = new Intl.DateTimeFormat("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(now);
}

function jitter(base, spread, digits = 1) {
  return (base + (Math.random() - 0.5) * spread).toFixed(digits);
}

function updateMetrics() {
  if (externalDataActive) {
    return;
  }

  const score = Math.round(92 + Math.random() * 5);
  scoreValue.textContent = score;
  scoreValue.parentElement.style.setProperty("--score", score);
  colorValue.textContent = `${jitter(98, 1.6)}%`;
  sharpnessValue.textContent = `${jitter(92, 2.2)}%`;
  exposureValue.textContent = `${jitter(96, 1.8)}%`;
}

function setBar(barElement, textElement, value) {
  const score = Math.max(0, Math.min(100, Math.round(value)));
  barElement.style.setProperty("--bar", `${score}%`);
  textElement.textContent = score;
}

function setBadge(status) {
  const normalized = String(status || "RUNNING").toUpperCase();
  resultBadge.textContent = normalized;
  resultBadge.classList.toggle("fail", normalized === "FAIL");
  resultBadge.classList.toggle("running", normalized !== "PASS" && normalized !== "FAIL");
}

function applyItsData(data) {
  externalDataActive = true;
  const metrics = data.metrics || {};
  const tests = data.tests || {};
  const score = Math.round(metrics.overallScore ?? 0);

  scoreValue.textContent = score;
  scoreValue.parentElement.style.setProperty("--score", score);
  colorValue.textContent = `${Number(metrics.colorAccuracy ?? 0).toFixed(1)}%`;
  sharpnessValue.textContent = `${Number(metrics.sharpness ?? 0).toFixed(1)}%`;
  exposureValue.textContent = `${Number(metrics.exposure ?? 0).toFixed(1)}%`;

  setBar(colorBar, colorScore, tests.colorAccuracy ?? metrics.colorAccuracy ?? 0);
  setBar(resolutionBar, resolutionScore, tests.resolution ?? metrics.sharpness ?? 0);
  setBar(dynamicRangeBar, dynamicRangeScore, tests.dynamicRange ?? metrics.exposure ?? 0);
  setBar(defectBar, defectScore, tests.defectDetect ?? metrics.overallScore ?? 0);
  setBadge(data.status);
}

function applyRunInfo(runInfo) {
  if (!runNameBadge) {
    return;
  }

  const runName = runInfo?.name || "CameraITS_*";
  runNameBadge.textContent = runName;
  runNameBadge.title = runInfo?.path || runName;
  runNameBadge.classList.toggle("waiting", !runInfo?.name);
}

function getCameraIdList(cameras) {
  return (Array.isArray(cameras) ? cameras : [])
    .map((camera) => camera?.id || "")
    .filter(Boolean);
}

function renderCameraTabs() {
  if (!cameraTabs) {
    return;
  }

  cameraTabs.innerHTML = "";
  if (!cameraList.length) {
    cameraTabs.classList.add("hidden");
    return;
  }

  cameraTabs.classList.remove("hidden");
  cameraList.forEach((camera) => {
    const cameraId = camera.id;
    const tabButton = document.createElement("button");
    tabButton.type = "button";
    tabButton.className = "camera-tab";
    tabButton.textContent = camera.label || cameraId;
    tabButton.dataset.cameraId = cameraId;
    tabButton.classList.toggle("active", cameraId === selectedCameraId);
    tabButton.setAttribute("aria-pressed", cameraId === selectedCameraId ? "true" : "false");
    tabButton.addEventListener("click", () => {
      selectedCameraId = cameraId;
      renderCameraTabs();
      applySelectedCameraData({ scrollFocusedTc: true });
    });
    cameraTabs.appendChild(tabButton);
  });
}

function applyCameraState(data, { followActive = false } = {}) {
  const nextCameraList = Array.isArray(data.cameras) ? data.cameras : [];
  const nextCameraIds = getCameraIdList(nextCameraList);
  const newCameraIds = nextCameraIds.filter((cameraId) => !knownCameraIds.includes(cameraId));
  const activeCameraId = data.activeExecution?.cameraId || data.capture?.cameraId || data.activeCameraId || "";

  cameraList = nextCameraList;
  knownCameraIds = nextCameraIds;
  cameraTrees = data.cameraTrees || {};
  cameraAnalyses = data.cameraAnalysis || {};
  cameraCaptures = data.cameraCaptures || {};
  cameraActiveExecutions = data.cameraActiveExecutions || {};

  if (!selectedCameraId || !nextCameraIds.includes(selectedCameraId)) {
    selectedCameraId = activeCameraId || nextCameraIds[0] || "";
  }

  if (newCameraIds.length > 0) {
    selectedCameraId = activeCameraId && newCameraIds.includes(activeCameraId)
      ? activeCameraId
      : newCameraIds[newCameraIds.length - 1];
  }

  if (followActive && activeCameraId && nextCameraIds.includes(activeCameraId)) {
    selectedCameraId = activeCameraId;
  }

  renderCameraTabs();
}

function getSelectedTree(data) {
  if (selectedCameraId && cameraTrees[selectedCameraId]) {
    return cameraTrees[selectedCameraId];
  }
  return Array.isArray(data.tree) ? data.tree : itsTestStructure;
}

function getSelectedAnalysis(data) {
  if (selectedCameraId && cameraAnalyses[selectedCameraId]) {
    return cameraAnalyses[selectedCameraId];
  }
  return data.analysis || null;
}

function getSelectedCapture(data) {
  if (selectedCameraId && cameraCaptures[selectedCameraId]) {
    return cameraCaptures[selectedCameraId];
  }
  return data.capture || null;
}

function getSelectedActiveExecution(data) {
  if (selectedCameraId && cameraActiveExecutions[selectedCameraId]) {
    return cameraActiveExecutions[selectedCameraId];
  }
  return data.activeExecution || null;
}

function applySelectedCameraData({ data = {}, scrollFocusedTc = false } = {}) {
  const selectedTree = getSelectedTree(data);
  const selectedCapture = getSelectedCapture(data);
  const selectedActiveExecution = getSelectedActiveExecution(data);

  if (selectedActiveExecution?.scene && selectedActiveExecution?.test) {
      setCurrentTcFocus(
          {
              cameraId:
                  selectedActiveExecution.cameraId || selectedCameraId || "",

              scene:
                  selectedActiveExecution.scene,

              test:
                  selectedActiveExecution.test
          },
          {
              scroll: scrollFocusedTc,
              behavior: scrollFocusedTc ? "smooth" : "auto"
          }
      );
  }

  if (selectedCapture) {

      const sceneResults =
          selectedTree.find(
              (item) => item.scene === selectedCapture.scene
          );

      if (sceneResults) {

          const status =
              sceneResults.tests?.[
                  selectedCapture.test
              ];

          if (status !== undefined) {

              const alreadyQueued = pendingTcUpdates.some(
                  (item) =>
                      item.cameraId === selectedCapture.cameraId &&
                      item.scene === selectedCapture.scene &&
                      item.test === selectedCapture.test
              );

              if (!alreadyQueued) {
                  pendingTcUpdates.push({
                      cameraId:
                          selectedCapture.cameraId,

                      scene:
                          selectedCapture.scene,

                      test:
                          selectedCapture.test,

                      status
                  });
              }
          }
      }
  }
  const selectedAnalysis = getSelectedAnalysis(data);
  if (selectedAnalysis) {
    applyItsData(selectedAnalysis);
  }

  if (selectedCapture) {
    const captureChanged = applyCaptureInfo(selectedCapture);
    if (captureChanged) {
      refreshLiveFeed();
    }
    lastAppliedCaptureSequence = Math.max(
      lastAppliedCaptureSequence,
      Number(selectedCapture.sequence || 0)
    );
  }
}

function applyCaptureInfo(capture) {
  if (!capture) {
    return false;
  }

  const captureKey = `${capture.sequence || 0}:${capture.cameraId || ""}:${capture.scene || ""}:${capture.test || ""}:${capture.fileName || ""}`;
  const changed = captureKey !== currentCaptureKey;
  currentCaptureKey = captureKey;

  const cameraPrefix = capture.cameraId ? `${capture.cameraId} / ` : "";
  if (!capture.available) {
    liveBadge.textContent = capture.test ? "NO IMG" : "WAIT";
    return changed;
  }

  liveBadge.textContent = "CAPTURE";
  return changed;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parseLogTimestamp(text) {
    const match = text.match(LOG_TIMESTAMP_RE);

    if (!match) {
        return null;
    }

    const [
        ,
        month,
        day,
        hour,
        minute,
        second,
        millis
    ] = match;

    return (
        (((Number(hour) * 60)
            + Number(minute)) * 60
            + Number(second)) * 1000
        + Number(millis)
    );
}

function isFocusedTc(sceneName, testName, cameraId = selectedCameraId) {
  return currentTcFocus.cameraId === cameraId &&
    currentTcFocus.scene === sceneName &&
    currentTcFocus.test === testName;
}

function getCurrentTcDescription(sceneName, testName) {
  return tcDescriptionMap?.[sceneName]?.[testName]
    || "현재 테스트의 세부 설명을 준비 중입니다.";
}

function updateCurrentTestGuide() {
  if (!currentTestScene || !currentTestName || !currentTestOrder || !currentTestDescription) {
    return;
  }

  const sceneName = currentTcFocus.scene || tcOrderList[0]?.scene || "scene0";
  const testName = currentTcFocus.test || tcOrderList[0]?.test || "test_jitter";
  const order = tcOrderMap.get(`${sceneName}:${testName}`) || 1;

  currentTestScene.textContent = sceneName;
  currentTestName.textContent = testName;
  currentTestOrder.textContent = `( ${order} / ${totalTcCount} )`;
  currentTestDescription.textContent = getCurrentTcDescription(sceneName, testName);
}

function applyCurrentTcFocus({ scroll = false, behavior = "smooth" } = {}) {
  const treeContainer = document.querySelector("#tcTreeContainer");
  if (!treeContainer || !currentTcFocus.scene || !currentTcFocus.test) {
    updateCurrentTestGuide();
    return;
  }

  let focusedItem = null;
  treeContainer.querySelectorAll(".tc-item").forEach((tcItem) => {
    const matches = isFocusedTc(tcItem.dataset.scene, tcItem.dataset.test, tcItem.dataset.cameraId);
    tcItem.classList.toggle("tc-focused", matches);
    if (matches) {
      tcItem.setAttribute("aria-current", "step");
      focusedItem = tcItem;
    } else {
      tcItem.removeAttribute("aria-current");
    }
  });

  if (!scroll || !focusedItem || !tcAutoFollow) {
    updateCurrentTestGuide();
    return;
  }

  requestAnimationFrame(() => {
    const containerRect = treeContainer.getBoundingClientRect();
    const itemRect = focusedItem.getBoundingClientRect();
    const itemTop = itemRect.top - containerRect.top + treeContainer.scrollTop;
    const centeredTop = itemTop - (treeContainer.clientHeight - itemRect.height) / 2;

    treeContainer.scrollTo({
      top: Math.max(0, centeredTop),
      behavior
    });
  });
  updateCurrentTestGuide();
}

function setCurrentTcFocus(capture, options = {}) {
  const cameraId = capture?.cameraId || selectedCameraId || "";
  const sceneName = capture?.scene || "";
  const testName = capture?.test || "";
  if (!sceneName || !testName) {
    return false;
  }

  const changed = !isFocusedTc(sceneName, testName, cameraId);
  currentTcFocus = { cameraId, scene: sceneName, test: testName };
  applyCurrentTcFocus({
    scroll: Boolean(options.scroll),
    behavior: options.behavior || (changed ? "smooth" : "auto")
  });
  updateCurrentTestGuide();
  return changed;
}

async function waitForLogOutput(logCount) {
  const minimumDelay = logCount > 0
    ? Math.min(LOG_OUTPUT_MAX_WAIT_MS, Math.max(32, logCount * LOG_RENDER_INTERVAL_MS))
    : LOG_OUTPUT_EMPTY_DELAY_MS;
  const startedAt = Date.now();

  await sleep(minimumDelay);

  while ((logQueue.length > 0 || isPausing) && Date.now() - startedAt < LOG_OUTPUT_MAX_WAIT_MS) {
    await sleep(LOG_OUTPUT_IDLE_SLEEP_MS);
  }
}

async function pollItsData() {
  if (!dataEndpoint) {
    return;
  }

  try {
    const response = await fetch(`${dataEndpoint}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`ITS endpoint returned ${response.status}`);
    }
    const data = await response.json();
    applyItsData(data);
  } catch (error) {
    setBadge("SIM");
    externalDataActive = false;
  }
}

async function refreshLiveFeed() {
  const livePanel = document.querySelector(
    '.capture-panel[data-capture-tab-id="live"]'
  );

  // LIVE Capture Tab 이 활성 상태가 아니면 polling 중단
  if (!livePanel?.classList.contains("active")) {
    return;
  }

  try {
    const feedParams = new URLSearchParams({ t: String(Date.now()) });
    if (!hasCustomLiveFeed && selectedCameraId) {
      feedParams.set("camera", selectedCameraId);
    }
    const separator = liveFeedPath.includes("?") ? "&" : "?";
    const response = await fetch(`${liveFeedPath}${separator}${feedParams.toString()}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Live feed returned ${response.status}`);
    }
    const blob = await response.blob();
    if (!blob.size) {
      throw new Error("Live feed is empty");
    }
    const nextUrl = URL.createObjectURL(blob);
    dutMirror.onload = () => {
      if (liveFeedObjectUrl) {
        URL.revokeObjectURL(liveFeedObjectUrl);
      }
      liveFeedObjectUrl = nextUrl;
      dutMirror.classList.remove("hidden");
      cameraScene.classList.add("has-live-feed");
    };
    dutMirror.onerror = () => {
      URL.revokeObjectURL(nextUrl);
      if (liveFeedObjectUrl) {
        URL.revokeObjectURL(liveFeedObjectUrl);
        liveFeedObjectUrl = null;
      }
      dutMirror.removeAttribute("src");
      dutMirror.classList.add("hidden");
      cameraScene.classList.remove("has-live-feed");
    };
    dutMirror.src = nextUrl;
    cameraScene.classList.add("has-live-feed");
  } catch (error) {
    if (liveFeedObjectUrl) {
      URL.revokeObjectURL(liveFeedObjectUrl);
      liveFeedObjectUrl = null;
    }
    dutMirror.removeAttribute("src");
    dutMirror.classList.add("hidden");
    cameraScene.classList.remove("has-live-feed");
  }
}

/**
 * TC 트리 렌더링 함수
 * 테스트 구조(itsTestStructure)를 바탕으로 좌측 리스트를 렌더링합니다.
 */
function renderTcTree() {
  const tcListContainer = document.querySelector("#tcList");
  if (!tcListContainer) return;
  
  tcListContainer.innerHTML = "";

  const statusMap = {
    0: { text: "WAIT", className: "wait" },
    1: { text: "PASS", className: "pass" },
    2: { text: "SKIP", className: "skip" },
    3: { text: "FAIL", className: "fail" }
  };

  itsTestStructure.forEach((item) => {
    const groupLi = document.createElement("li");
    groupLi.className = "tc-group";
    groupLi.innerHTML = `<span class="group-title">${item.scene}</span>`;

    const childUl = document.createElement("ul");
    childUl.className = "tc-list";

    Object.entries(item.tests).forEach(([rawName, statusValue]) => {
      const formattedName = formatTcName(rawName);
      const currentStatus = statusMap[statusValue] || statusMap[0];

      const tcLi = document.createElement("li");
      tcLi.className = "tc-item";
      tcLi.dataset.cameraId = selectedCameraId;
      tcLi.dataset.scene = item.scene;
      tcLi.dataset.test = rawName;
      if (isFocusedTc(item.scene, rawName, selectedCameraId)) {
        tcLi.classList.add("tc-focused");
        tcLi.setAttribute("aria-current", "step");
      }
      tcLi.innerHTML = `
        <span class="tc-name">${formattedName}</span>
        <span class="tc-status ${currentStatus.className}">${currentStatus.text}</span>
      `;
      if (statusValue !== 0) {
          tcLi.classList.add("clickable");

          tcLi.addEventListener("click", () => {
              openTcLogTab(
                  selectedCameraId,
                  item.scene,
                  rawName
              );
          });
      }
      childUl.appendChild(tcLi);
    });

    groupLi.appendChild(childUl);
    tcListContainer.appendChild(groupLi);
  });
}

function activateLogTab(tabId) {
    // 모든 panel 비활성화
    document.querySelectorAll(".log-panel").forEach((panel) => {
        panel.classList.remove("active");
    });

    // 모든 tab 비활성화
    document.querySelectorAll(".log-tab").forEach((tab) => {
        tab.classList.remove("active");
    });

    // 대상 panel 활성화
    const targetPanel = document.querySelector(
        `.log-panel[data-tab-id="${tabId}"]`
    );

    if (targetPanel) {
        targetPanel.classList.add("active");
    }

    // 대상 tab 활성화
    const targetTab = document.querySelector(
        `.log-tab[data-tab-id="${tabId}"]`
    );

    if (targetTab) {
        targetTab.classList.add("active");
    }

    // LIVE 탭 복귀 시 Auto Follow 복구
    if (tabId === "live") {
        const liveViewer =
            document.getElementById("logViewer");
    
        logAutoFollow = true;
    
        // Capture 도 LIVE 로 동기화
        activateCaptureTab("live");
    
        if (liveViewer) {
            requestAnimationFrame(() => {
                liveViewer.scrollTop =
                    liveViewer.scrollHeight;
            });
        }
    }
}

function activateCaptureTab(tabId) {
    // LIVE 복귀 시 TC capture 정리
    if (tabId === "live") {
        currentCaptureTabKey = "";

        const oldPanel = document.querySelector(
            '.capture-panel[data-capture-tab-id="tc-capture"]'
        );

        if (oldPanel?.dataset.objectUrl) {
            URL.revokeObjectURL(
                oldPanel.dataset.objectUrl
            );
        }

        document
            .querySelector(
                '.capture-tab[data-capture-tab-id="tc-capture"]'
            )
            ?.remove();

        oldPanel?.remove();
    }

    // 모든 panel 비활성화
    document
        .querySelectorAll(".capture-panel")
        .forEach((panel) => {
            panel.classList.remove("active");
        });

    // 모든 tab 비활성화
    document
        .querySelectorAll(".capture-tab")
        .forEach((tab) => {
            tab.classList.remove("active");
        });

    // 대상 panel 활성화
    const targetPanel = document.querySelector(
        `.capture-panel[data-capture-tab-id="${tabId}"]`
    );

    if (targetPanel) {
        targetPanel.classList.add("active");
    
        // LIVE 탭 복귀 시 즉시 최신 Capture 반영
        if (tabId === "live") {
            requestAnimationFrame(() => {
                refreshLiveFeed();
            });
        }
    }

    // 대상 tab 활성화
    const targetTab = document.querySelector(
        `.capture-tab[data-capture-tab-id="${tabId}"]`
    );

    if (targetTab) {
        targetTab.classList.add("active");
    }
}

function createTcLogTab(
    tabId,
    title,
    logs,
    cameraId,
    sceneName,
    testName
) {
    const existingTab = tcLogTabs.find(
        (tab) => tab.id === tabId
    );

    if (existingTab) {
        activateLogTab(tabId);
    
        showTcCaptureTab(
            cameraId,
            sceneName,
            testName
        );
      
        return;
    }

    // 최대 탭 제한
    if (tcLogTabs.length >= MAX_TC_LOG_TABS) {
        const oldest = tcLogTabs.shift();

        document
            .querySelector(`.log-tab[data-tab-id="${oldest.id}"]`)
            ?.remove();

        document
            .querySelector(`.log-panel[data-tab-id="${oldest.id}"]`)
            ?.remove();
    }

    // 탭 버튼 생성
    const tabButton = document.createElement("button");

    tabButton.className = "camera-tab log-tab";
    tabButton.dataset.tabId = tabId;
    tabButton.textContent = title;

    tabButton.addEventListener("click", () => {
        activateLogTab(tabId);

        showTcCaptureTab(
            cameraId,
            sceneName,
            testName
        );
    });

    logTabsContainer.appendChild(tabButton);

    // 패널 생성
    const panel = document.createElement("div");

    panel.className = "log-viewer log-panel";
    panel.dataset.tabId = tabId;

    logs.forEach((line) => {
        const logLine = document.createElement("div");

        logLine.className = "log-line-raw";
        logLine.dataset.logLevel = getLogLevel(line);

        let formattedText = line;

        if (formattedText.includes("==========>")) {
            formattedText =
                `<b style="color: #ffca28; font-size: 1.1em;">`
                + `${formattedText}`
                + `</b>`;
        } else {
            formattedText = formattedText
                .replace(
                    "INFO",
                    '<span class="log-info-tag">INFO</span>'
                )
                .replace(
                    "PASS",
                    '<span class="log-pass-tag">PASS</span>'
                )
                .replace(
                    "FAIL",
                    '<span class="log-fail-tag">FAIL</span>'
                );
        }

        logLine.innerHTML = formattedText;

        panel.appendChild(logLine);
    });
    applyLogFilterToPanels();

    logPanelsContainer.appendChild(panel);

    tcLogTabs.push({
        id: tabId,
        cameraId,
        sceneName,
        testName
    });

    activateLogTab(tabId);
}
async function openTcLogTab(cameraId, sceneName, testName) {
    try {
        const response = await fetch(
            `${monitorEndpoint}/get-tc-log`
            + `?camera=${encodeURIComponent(cameraId)}`
            + `&scene=${encodeURIComponent(sceneName)}`
            + `&test=${encodeURIComponent(testName)}`,
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        createTcLogTab(
            `${cameraId}:${sceneName}:${testName}`,
            formatTcName(testName),
            data.logs || [],
            cameraId,
            sceneName,
            testName
        );

        showTcCaptureTab(
            cameraId,
            sceneName,
            testName
        );
    } catch (error) {
        console.error(error);
    }
}

function createEmptyCapturePanel() {
    return `
        <div class="device-frame">
            <div class="scanline"></div>

            <div
                class="camera-scene has-live-feed"
                aria-label="simulated live camera feed"
            >
                <img
                    class="dut-mirror"
                    src="./data/live-dut-feed.png"
                    alt="No Capture Image"
                />

                <div class="target-card target-main">
                    <span class="android-mark">
                        ANDROID
                    </span>

                    <span class="lens lens-a"></span>
                    <span class="lens lens-b"></span>
                    <span class="lens lens-c"></span>
                </div>

                <div class="focus-box focus-primary"></div>

                <div class="focus-box focus-secondary"></div>

                <div class="exposure-ruler">
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
}

async function showTcCaptureTab(
    cameraId,
    sceneName,
    testName
) {
    const tabId = "tc-capture";

    const captureKey =
        `${cameraId}:${sceneName}:${testName}`;

    // 동일 Capture 재선택이면 skip
    if (currentCaptureTabKey === captureKey) {
        activateCaptureTab(tabId);
        return;
    }

    currentCaptureTabKey = captureKey;

    const oldPanel = document.querySelector(
        '.capture-panel[data-capture-tab-id="tc-capture"]'
    );

    // 기존 Object URL 정리
    if (oldPanel?.dataset.objectUrl) {
        URL.revokeObjectURL(
            oldPanel.dataset.objectUrl
        );
    }

    // 기존 TC Capture 제거
    document
        .querySelector(
            '.capture-tab[data-capture-tab-id="tc-capture"]'
        )
        ?.remove();
      
    oldPanel?.remove();

    // 새 탭 생성
    const tabButton =
        document.createElement("button");

    tabButton.className =
        "camera-tab capture-tab";

    tabButton.dataset.captureTabId =
        tabId;

    tabButton.textContent =
        formatTcName(testName);

    tabButton.addEventListener(
        "click",
        () => {
            activateCaptureTab(tabId);
        }
    );

    captureTabsContainer.appendChild(
        tabButton
    );

    // 패널 생성
    const panel =
        document.createElement("div");

    panel.className =
        "capture-panel";

    panel.dataset.captureTabId =
        tabId;

    const response = await fetch(
        `${monitorEndpoint}/get-tc-capture`
        + `?camera=${encodeURIComponent(cameraId)}`
        + `&scene=${encodeURIComponent(sceneName)}`
        + `&test=${encodeURIComponent(testName)}`,
        {
            cache: "no-store"
        }
    );

    if (response.ok) {
        const blob = await response.blob();

        if (blob.size) {
            const imageUrl = URL.createObjectURL(blob);
                panel.dataset.objectUrl = imageUrl;

            panel.innerHTML = `
                <div class="device-frame">
                    <div class="scanline"></div>

                    <div class="camera-scene has-live-feed">
                        <img
                            class="dut-mirror"
                            src="${imageUrl}"
                            alt="${formatTcName(testName)}"
                        />

                        <div class="target-card target-main">
                            <span class="android-mark">
                                ANDROID
                            </span>

                            <span class="lens lens-a"></span>
                            <span class="lens lens-b"></span>
                            <span class="lens lens-c"></span>
                        </div>

                        <div class="focus-box focus-primary"></div>

                        <div class="focus-box focus-secondary"></div>

                        <div class="exposure-ruler">
                            <span></span>
                            <span></span>
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            `;
        } else {
            panel.innerHTML = createEmptyCapturePanel();
        }
    } else {
        panel.innerHTML = createEmptyCapturePanel();
    }

    capturePanelsContainer.appendChild(
        panel
    );

    activateCaptureTab(tabId);
}

// 페이지 로드 시 실행
//document.addEventListener("DOMContentLoaded", renderTcTree);

function applyDashboardData(data, { scrollFocusedTc = false, followActiveCamera = false } = {}) {
  applyRunInfo(data.run);
  applyCameraState(data, { followActive: followActiveCamera });

  if (data.capture) {
    pendingTcFocus = data.capture;
  }

  applySelectedCameraData({ data, scrollFocusedTc });
}

async function updateStatus() {
  if (statusUpdateInProgress) {
    return;
  }

  statusUpdateInProgress = true;

  try {
    const response = await fetch(`${monitorEndpoint}/its-status.json`, { cache: "no-store" });
    const data = await response.json();

    if (data) {
      const captureSequence = Number(data.capture?.sequence || 0);
      const hasNewCapture = captureSequence && captureSequence > lastAppliedCaptureSequence;
      if (hasNewCapture) {
        applyCameraState(data, { followActive: true });
        syncLogSequenceToCapture(data.capture);
        const logCount = await fetchLiveLogs();
        await waitForLogOutput(logCount);
      }

      applyDashboardData(data, {
        scrollFocusedTc: hasNewCapture,
        followActiveCamera: hasNewCapture
      });
    }
  } catch (error) {
    console.error("데이터 수신 오류:", error);
  } finally {
    statusUpdateInProgress = false;
  }
}

let logQueue = [];
let renderedLogs = new Set();
let isPausing = false;
let lastLogSequence = 0;

let logAutoFollow = true;
let logAutoFollowRestoreTimer = null;

let tcAutoFollow = true;
let tcAutoFollowRestoreTimer = null;

function clearLogViewer() {
    const logViewer = document.getElementById("logViewer");
    if (logViewer) {
        logViewer.innerHTML = "";
    }
    logQueue = [];
    renderedLogs.clear();
    needsClear = false;
    isPausing = false;
}

function syncLogSequenceToCapture(capture) {
    const captureSequence = Number(capture?.sequence || 0);
    if (!captureSequence || captureSequence <= lastLogSequence + 1) {
        return;
    }

    lastLogSequence = captureSequence - 1;
    clearLogViewer();
}

async function fetchLiveLogs() {
    try {
        const response = await fetch(`${monitorEndpoint}/get-live-logs?since=${lastLogSequence}`, { cache: "no-store" });
        const logs = await response.json();
        let queuedCount = 0;
        
        logs.forEach(log => {
            if (Number.isFinite(log.sequence)) {
                lastLogSequence = Math.max(lastLogSequence, log.sequence);
            }
          
            if (log.type === "CAMERA_CHANGE") {
                logQueue.push(log);
                queuedCount += 1;
            } else {
                const logKey = `${log.sequence}:${log.text}`;
            
                if (!renderedLogs.has(logKey)) {
                    logQueue.push(log);
                    renderedLogs.add(logKey);
                    queuedCount += 1;
                }
            }
        });
        return queuedCount;
    } catch (e) {
        console.error(e);
        return 0;
    }
}

async function startLogSimulation() {
    const logViewer =
        document.getElementById("logViewer");

    let previousTimestamp = null;

    while (true) {

        if (
            isPausing ||
            logQueue.length === 0 ||
            !logViewer
        ) {
            await sleep(LOG_OUTPUT_IDLE_SLEEP_MS);
            continue;
        }

        const log = logQueue.shift();

        // CAMERA CHANGE
        if (log.type === "CAMERA_CHANGE") {
            needsClear = true;
            previousTimestamp = null;
            continue;
        }

        // 실제 로그 출력 직전 clear
        if (needsClear) {
            logViewer.innerHTML = "";
            renderedLogs.clear();
            needsClear = false;
        }

        const rawText = log.text;

        // summary line 은 즉시 출력
        const isSummaryLine =
            rawText.startsWith("Total time elapsed")
            || rawText.startsWith("Artifacts are saved in")
            || rawText.startsWith("Test summary saved in")
            || rawText.startsWith("Test results:");

        const currentTimestamp =
            parseLogTimestamp(rawText);

        // timestamp 기반 delay
        if (
            !isSummaryLine &&
            previousTimestamp !== null &&
            currentTimestamp !== null
        ) {
            const delta =
                currentTimestamp - previousTimestamp;

            // 너무 긴 delay 방지
            const clampedDelay =
                Math.max(
                    0,
                    Math.min(delta, 300)
                );

            if (clampedDelay > 0) {
                await sleep(clampedDelay);
            }
        }

        if (currentTimestamp !== null) {
            previousTimestamp = currentTimestamp;
        }

        // 로그 출력
        const logLine =
            document.createElement("div");

        logLine.className = "log-line-raw";
        logLine.dataset.logLevel = getLogLevel(rawText);

        let text = rawText;

        if (text.includes("==========>")) {
            text =
                `<b style="color: #ffca28; font-size: 1.1em;">${text}</b>`;
        } else {
            text = text
                .replace(
                    "INFO",
                    '<span class="log-info-tag">INFO</span>'
                )
                .replace(
                    "PASS",
                    '<span class="log-pass-tag">PASS</span>'
                )
                .replace(
                    "FAIL",
                    '<span class="log-fail-tag">FAIL</span>'
                );
        }

        logLine.innerHTML = text;

        logViewer.appendChild(logLine);
        applyLogFilterToPanels();

        if (logAutoFollow) {
            logViewer.scrollTop =
                logViewer.scrollHeight;
        }

        // TC sync
        if (rawText.includes("Test results:")) {

            const nextTcUpdate =
                pendingTcUpdates.shift();

            if (nextTcUpdate) {

                const targetScene =
                    itsTestStructure.find(
                        (scene) =>
                            scene.scene === nextTcUpdate.scene
                    );

                if (
                    targetScene &&
                    targetScene.tests[
                        nextTcUpdate.test
                    ] !== undefined
                ) {
                    targetScene.tests[
                        nextTcUpdate.test
                    ] = nextTcUpdate.status;
                }

                renderTcTree();

                setCurrentTcFocus(
                    {
                        cameraId:
                            nextTcUpdate.cameraId,

                        scene:
                            nextTcUpdate.scene,

                        test:
                            nextTcUpdate.test
                    },
                    {
                        scroll: true,
                        behavior: "smooth"
                    }
                );

                applyCurrentTcFocus({
                    scroll: false,
                    behavior: "auto"
                });
            }
        }

        while (logViewer.childElementCount > 300) {
            logViewer.removeChild(
                logViewer.firstChild
            );
        }
    }
}

function init() {
  updateClock();
  renderTcTree();
  updateMetrics();
  updateCurrentTestGuide();
  startLogSimulation();

  const tcTreeContainer = document.getElementById("tcTreeContainer");
  
  if (tcTreeContainer) {
    tcTreeContainer.addEventListener("scroll", () => {
      const distanceFromBottom =
      tcTreeContainer.scrollHeight
      - tcTreeContainer.scrollTop
      - tcTreeContainer.clientHeight;
      
      const isNearBottom = distanceFromBottom < 32;

      // 사용자가 수동 탐색 중
      if (!isNearBottom) {
        tcAutoFollow = false;

        if (tcAutoFollowRestoreTimer) {
          clearTimeout(tcAutoFollowRestoreTimer);
        }
        
        tcAutoFollowRestoreTimer = setTimeout(() => {
          tcAutoFollow = true;
        }, 5000);
        
        return;
      }
      
      tcAutoFollow = true;
    });
  }

  const logViewer = document.getElementById("logViewer");

  if (logViewer) {
    logViewer.addEventListener("scroll", () => {
      const distanceFromBottom =
        logViewer.scrollHeight
        - logViewer.scrollTop
        - logViewer.clientHeight;

      const isNearBottom = distanceFromBottom < 32;

      // 사용자가 위로 스크롤하면 Auto Follow 중단
      if (!isNearBottom) {
        logAutoFollow = false;

        // 기존 복구 타이머 제거
        if (logAutoFollowRestoreTimer) {
          clearTimeout(logAutoFollowRestoreTimer);
        }

        // 5초간 추가 입력 없으면 자동 복구
        logAutoFollowRestoreTimer = setTimeout(() => {
          logAutoFollow = true;

          logViewer.scrollTop = logViewer.scrollHeight;
        }, 5000);

        return;
      }

      // 하단 근처 도달 시 즉시 재활성화
      logAutoFollow = true;
    });
  }

  setInterval(updateClock, 1000);
  setInterval(updateMetrics, 900);

  updateStatus();

  setInterval(updateStatus, TC_STATUS_POLL_MS);
  setInterval(fetchLiveLogs, LOG_POLL_MS);

  refreshLiveFeed();
  setInterval(refreshLiveFeed, TC_STATUS_POLL_MS);

  if (typeof pollItsData === "function") {
    setInterval(pollItsData, 1500);
  }
  const liveTabButton = document.querySelector(
      '.log-tab[data-tab-id="live"]'
  );

  if (liveTabButton) {
      liveTabButton.addEventListener("click", () => {
          activateLogTab("live");
      });
  }

  if (logFilterGroup) {
    logFilterGroup.querySelectorAll(".log-filter-button").forEach((button) => {
      button.addEventListener("click", () => {
        setLogFilter(button.dataset.logFilter || "ALL");
      });
    });
  }

  setLogFilter("ALL");

  const liveCaptureTab =
      document.querySelector(
          '.capture-tab[data-capture-tab-id="live"]'
      );

  if (liveCaptureTab) {
      liveCaptureTab.addEventListener(
          "click",
          () => {
              activateCaptureTab("live");
          }
      );
  }
}

init();
