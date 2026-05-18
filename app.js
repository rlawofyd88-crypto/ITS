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

let needsClear = false;
let externalDataActive = false;
const params = new URLSearchParams(window.location.search);
const dataEndpoint = params.get("data");
const monitorEndpoint = params.get("monitor") || "http://localhost:8765";
const liveFeedPath = params.get("feed") || `${monitorEndpoint}/latest-capture-image`;
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

function applyCaptureInfo(capture) {
  if (!capture || !capture.available) {
    return;
  }

  liveCaption.textContent = capture.fileName || "Latest CameraITS capture";
  liveCaption.title = capture.relativePath || capture.fileName || "";
  liveBadge.textContent = "CAPTURE";
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
      liveCaption.textContent = "Waiting for CameraITS capture image...";
      liveCaption.title = "";
      liveBadge.textContent = "WAIT";
    };
    dutMirror.src = nextUrl;
    cameraScene.classList.add("has-live-feed");
  } catch (error) {
    cameraScene.classList.remove("has-live-feed");
    liveCaption.textContent = "Waiting for CameraITS capture image...";
    liveCaption.title = "";
    liveBadge.textContent = "WAIT";
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
      tcLi.innerHTML = `
        <span class="tc-name">${formattedName}</span>
        <span class="tc-status ${currentStatus.className}">${currentStatus.text}</span>
      `;
      childUl.appendChild(tcLi);
    });

    groupLi.appendChild(childUl);
    tcListContainer.appendChild(groupLi);
  });
}

// 페이지 로드 시 실행
//document.addEventListener("DOMContentLoaded", renderTcTree);

async function updateStatus() {
  try {
    const response = await fetch(`${monitorEndpoint}/its-status.json`, { cache: "no-store" });
    const data = await response.json();

    if (data) {
      // 1. 좌측 TC 트리 목록 반영 및 리렌더링
      if (data.tree && Array.isArray(data.tree)) {
        itsTestStructure = data.tree; 
        renderTcTree();
      }
      
      // 2. 우측 02 / ANALYSIS 실시간 실제 분석 연동 데이터 반영
      if (data.analysis) {
        // 기존에 만들어두신 applyItsData 함수를 그대로 호출하여 화면 매핑을 처리합니다.
        applyItsData(data.analysis);
      }

      if (data.capture) {
        applyCaptureInfo(data.capture);
      }
    }
  } catch (error) {
    console.error("데이터 수신 오류:", error);
  }
}

let logQueue = [];
let renderedLogs = new Set(); // 이미 화면에 표시된 로그 저장 (중복 방지)
let isPausing = false;

async function fetchLiveLogs() {
    try {
        const response = await fetch(`${monitorEndpoint}/get-live-logs`, { cache: "no-store" });
        const logs = await response.json();
        
        logs.forEach(log => {
            if (log.type === "SCENE_CHANGE") {
                logQueue.push(log); // 플래그는 무조건 큐에 삽입
            } else {
                // 일반 로그만 중복 체크
                if (!renderedLogs.has(log.text) || log.text.includes("Test results:")) {
                    logQueue.push(log);
                    renderedLogs.add(log.text);
                }
            }
        });
    } catch (e) { console.error(e); }
}

function startLogSimulation() {
    const logViewer = document.getElementById("logViewer");
    
    const logInterval = setInterval(() => {
        if (isPausing || logQueue.length === 0) return;

        const log = logQueue.shift();

        // 1. Scene 변경 플래그를 만났을 때
        if (log.type === "SCENE_CHANGE") {
            // 바로 비우지 않고, "다음에 로그가 들어오면 비워라"라고 예약만 합니다.
            needsClear = true; 
            console.log("다음 Scene 로그 유입 시 화면을 초기화합니다.");
            return; 
        }

        // 2. 실제 로그를 출력하기 직전, 비우기 예약이 되어 있다면?
        if (needsClear) {
            logViewer.innerHTML = ""; // 여기서 비웁니다!
            renderedLogs.clear();    
            needsClear = false;       // 예약 해제
            console.log("새 Scene 시작을 위해 이전 로그를 클리어했습니다.");
        }

        // 3. 기존 출력 로직 시작
        const logLine = document.createElement("div");
        logLine.className = "log-line-raw";
        
        let text = log.text;

        if (text.includes("==========>")) {
            text = `<b style="color: #ffca28; font-size: 1.1em;">${text}</b>`;
        } else {
            text = text
                .replace("INFO", '<span class="log-info-tag">INFO</span>')
                .replace("PASS", '<span class="log-pass-tag">PASS</span>')
                .replace("FAIL", '<span class="log-fail-tag">FAIL</span>');
        }
        logLine.innerHTML = text;
        logViewer.appendChild(logLine);
        logViewer.scrollTop = logViewer.scrollHeight;

        if (text.includes("Test results:")) {
            isPausing = true;
            setTimeout(() => { isPausing = false; }, 1000);
        }
        
        // 성능 유지용
        if (logViewer.childElementCount > 300) {
            logViewer.removeChild(logViewer.firstChild);
        }
    }, 100);
}

// 2. 기존 초기화 로직 및 인터벌 유지
function init() {
  updateClock();
  renderTcTree(); // TC 리스트업 실행
  updateMetrics();
  startLogSimulation();
  setInterval(updateClock, 1000);
  setInterval(updateMetrics, 900);
  setInterval(updateStatus, 3000);
  setInterval(fetchLiveLogs, 5000); // 5초마다 서버에서 새 로그 가져옴
  refreshLiveFeed();
  setInterval(refreshLiveFeed, 1500);
  
  // 데이터 폴링 시작 (엔드포인트가 있을 경우)
  if (typeof pollItsData === "function") {
    setInterval(pollItsData, 1500);
  }
}

init();
