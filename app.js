const clock = document.querySelector("#clock");
const fpsValue = document.querySelector("#fpsValue");
const latencyValue = document.querySelector("#latencyValue");
const frameValue = document.querySelector("#frameValue");
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
const liveCaption = document.querySelector("#liveCaption");
const liveBadge = document.querySelector("#liveBadge");
const cameraScene = document.querySelector("#cameraScene");

const tcListContainer = document.querySelector("#tcList");

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
const itsTestStructure = [
  {
    scene: "scene0",
    tests: ["test_jitter", "test_metadata", "test_request_capture_match", "test_sensor_events", "test_solid_color_test_pattern", "test_test_patterns", "test_tonemap_curve", "test_unified_timestamps", "test_vibration_restriction"]
  },
  {
    scene: "scene1_1",
    tests: ["test_ae_precapture_trigger", "test_auto_vs_manual", "test_black_white", "test_burst_capture", "test_burst_sameness_manual", "test_crop_region_raw", "test_crop_regions", "test_exposure_x_iso", "test_latching", "test_linearity", "test_locked_burst"]
  },
  {
    scene: "scene1_2",
    tests: ["test_param_color_correction", "test_param_flash_mode", "test_param_noise_reduction", "test_param_shading_mode", "test_param_tonemap_mode", "test_post_raw_sensitivity_boost", "test_raw_exposure", "test_reprocess_noise_reduction", "test_tonemap_sequence", "test_yuv_plus_dng"]
  },
  {
    scene: "scene1_3",
    tests: ["test_capture_result", "test_dng_noise_model", "test_ev_compensation", "test_exposure_time_priority", "test_jpeg", "test_raw_burst_sensitivity", "test_raw_sensitivity", "test_sensitivity_priority", "test_yuv_jpeg_all", "test_yuv_plus_jpeg", "test_yuv_plus_raw"]
  },
  {
    scene: "scene2_a",
    tests: ["test_display_p3", "test_effects", "test_exposure_keys_consistent", "test_format_combos", "test_num_faces", "test_reprocess_uv_swap"]
  },
  {
    scene: "scene2_b",
    tests: ["test_preview_num_faces", "test_yuv_jpeg_capture_sameness"]
  },
  {
    scene: "scene2_c",
    tests: ["test_camera_launch_perf_class", "test_default_camera_hdr", "test_jpeg_capture_perf_class", "test_num_faces"]
  },
  {
    scene: "scene2_d",
    tests: ["test_autoframing", "test_num_faces", "test_preview_num_faces"]
  },
  {
    scene: "scene2_e",
    tests: ["test_continuous_picture", "test_num_faces"]
  },
  {
    scene: "scene2_f",
    tests: ["test_preview_num_faces"]
  },
  {
    scene: "scene2_g",
    tests: ["test_preview_num_faces"]
  },
  {
    scene: "scene3",
    tests: ["test_edge_enhancement", "test_flip_mirror", "test_imu_drift", "test_landscape_to_portrait", "test_lens_movement_reporting", "test_reprocess_edge_enhancement"]
  },
  {
    scene: "scene4",
    tests: ["test_30_60fps_preview_fov_match", "test_aspect_ratio_and_crop", "test_multi_camera_alignment", "test_preview_aspect_ratio_and_crop", "test_preview_stabilization_fov", "test_video_aspect_ratio_and_crop"]
  },
  {
    scene: "scene6",
    tests: ["test_in_sensor_zoom", "test_low_latency_zoom", "test_preview_video_zoom_match", "test_preview_zoom", "test_session_characteristics_zoom", "test_zoom"]
  },
  {
    scene: "scene7",
    tests: ["test_multi_camera_switch"]
  },
  {
    scene: "scene8",
    tests: ["test_ae_awb_regions", "test_color_correction_mode_cct"]
  },
  {
    scene: "scene9",
    tests: ["test_jpeg_high_entropy", "test_jpeg_quality"]
  },
  {
    scene: "scene_hdr",
    tests: ["test_hdr_extension"]
  },
  {
    scene: "scene_low_light",
    tests: ["test_low_light_boost_extension", "test_night_extension"]
  },
  {
    scene: "scene6_tele",
    tests: ["test_preview_zoom_tele", "test_zoom_tele"]
  },
  {
    scene: "scene7_tele",
    tests: ["test_multi_camera_switch_tele"]
  },
  {
    scene: "scene_video",
    tests: ["test_preview_frame_drop"]
  }
];

let frame = 41280;
let externalDataActive = false;
const params = new URLSearchParams(window.location.search);
const dataEndpoint = params.get("data");
const liveFeedPath = params.get("feed") || "./data/live-demo-frame.png";
const liveStatePath = params.get("live_state") || "./data/live-demo-state.json";
let liveFeedObjectUrl = null;

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
  frame += Math.floor(28 + Math.random() * 5);
  fpsValue.textContent = jitter(30, 1.4);
  latencyValue.textContent = `${Math.round(38 + Math.random() * 12)} ms`;
  frameValue.textContent = String(frame).padStart(6, "0");

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
  try {
    const response = await fetch(`${liveFeedPath}?t=${Date.now()}`, { cache: "no-store" });
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
      cameraScene.classList.add("has-live-feed");
    };
    dutMirror.onerror = () => {
      URL.revokeObjectURL(nextUrl);
      cameraScene.classList.remove("has-live-feed");
    };
    dutMirror.src = nextUrl;
    cameraScene.classList.add("has-live-feed");
  } catch (error) {
    cameraScene.classList.remove("has-live-feed");
  }
}

async function refreshLiveState() {
  try {
    const response = await fetch(`${liveStatePath}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Live state returned ${response.status}`);
    }
    const state = await response.json();
    liveCaption.textContent = state.label || "ITS milestone captured";
    liveBadge.textContent = state.stage || "LIVE";
  } catch (error) {
    liveCaption.textContent = "Waiting for ITS milestone...";
    liveBadge.textContent = "LIVE";
  }
}

/**
 * TC 트리 렌더링 함수
 */
function renderTcTree() {
    if (!tcListContainer) return;
    tcListContainer.innerHTML = ""; 

    itsTestStructure.forEach((item) => {
        const groupLi = document.createElement("li");
        groupLi.className = "tc-group";
        groupLi.innerHTML = `<span class="group-title">${item.scene}</span>`;

        const childUl = document.createElement("ul");
        item.tests.forEach((rawTestName) => {
            const formattedName = formatTcName(rawTestName); // 이름 변환 적용
            const safeId = `${item.scene}-${rawTestName}`.replace(/\./g, "_"); // ID는 원본 이름 유지 (매핑용)

            const tcLi = document.createElement("li");
            tcLi.className = "tc-item";
            tcLi.id = safeId;
            tcLi.innerHTML = `
                <span class="tc-name">${formattedName}</span>
                <span class="tc-status">WAIT</span>
            `;
            childUl.appendChild(tcLi);
        });

        groupLi.appendChild(childUl);
        tcListContainer.appendChild(groupLi);
    });
}

/**
 * TC 결과 업데이트 함수
 */
function setTcResult(scene, testName, status) {
  const targetId = `${scene}-${testName}`.replace(/\./g, "_");
  const item = document.getElementById(targetId);
  if (!item) return;

  const statusLabel = item.querySelector(".tc-status");
  statusLabel.textContent = status.toUpperCase();
  statusLabel.className = `tc-status ${status.toLowerCase()}`;
}

// 2. 기존 초기화 로직 및 인터벌 유지
function init() {
  updateClock();
  renderTcTree(); // TC 리스트업 실행
  updateMetrics();
  
  // 멈췄던 인터벌들 재가동
  setInterval(updateClock, 1000);
  setInterval(updateMetrics, 900);
  
  // 데이터 폴링 시작 (엔드포인트가 있을 경우)
  if (typeof pollItsData === "function") {
    setInterval(pollItsData, 1500);
  }
}

init();