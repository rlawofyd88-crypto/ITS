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
const runNameBadge = document.querySelector("#runNameBadge");
const cameraTabs = document.querySelector("#cameraTabs");

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
let liveFeedObjectUrl = null;
let currentCaptureKey = "";
let lastAppliedCaptureSequence = 0;
let statusUpdateInProgress = false;
let currentTcFocus = { cameraId: "", scene: "", test: "" };
let cameraList = [];
let knownCameraIds = [];
let selectedCameraId = "";
let cameraTrees = {};
let cameraAnalyses = {};
let cameraCaptures = {};

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
  const activeCameraId = data.capture?.cameraId || data.activeCameraId || "";

  cameraList = nextCameraList;
  knownCameraIds = nextCameraIds;
  cameraTrees = data.cameraTrees || {};
  cameraAnalyses = data.cameraAnalysis || {};
  cameraCaptures = data.cameraCaptures || {};

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

function applySelectedCameraData({ data = {}, scrollFocusedTc = false } = {}) {
  const selectedTree = getSelectedTree(data);
  if (Array.isArray(selectedTree)) {
    itsTestStructure = selectedTree;
    renderTcTree();
    applyCurrentTcFocus({ scroll: scrollFocusedTc, behavior: "auto" });
  }

  const selectedAnalysis = getSelectedAnalysis(data);
  if (selectedAnalysis) {
    applyItsData(selectedAnalysis);
  }

  const selectedCapture = getSelectedCapture(data);
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
    liveCaption.textContent = capture.test ? `${cameraPrefix}${capture.test} / No capture image` : "Waiting for CameraITS capture image...";
    liveCaption.title = capture.message || "";
    liveBadge.textContent = capture.test ? "NO IMG" : "WAIT";
    return changed;
  }

  liveCaption.textContent = `${cameraPrefix}${capture.fileName || "Latest CameraITS capture"}`;
  liveCaption.title = capture.relativePath || capture.fileName || capture.test || "";
  liveBadge.textContent = "CAPTURE";
  return changed;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isFocusedTc(sceneName, testName, cameraId = selectedCameraId) {
  return currentTcFocus.cameraId === cameraId &&
    currentTcFocus.scene === sceneName &&
    currentTcFocus.test === testName;
}

function applyCurrentTcFocus({ scroll = false, behavior = "smooth" } = {}) {
  const treeContainer = document.querySelector("#tcTreeContainer");
  if (!treeContainer || !currentTcFocus.scene || !currentTcFocus.test) {
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
      childUl.appendChild(tcLi);
    });

    groupLi.appendChild(childUl);
    tcListContainer.appendChild(groupLi);
  });
}

// 페이지 로드 시 실행
//document.addEventListener("DOMContentLoaded", renderTcTree);

function applyDashboardData(data, { scrollFocusedTc = false, followActiveCamera = false } = {}) {
  applyRunInfo(data.run);
  applyCameraState(data, { followActive: followActiveCamera });

  if (data.capture) {
    setCurrentTcFocus(data.capture);
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
        setCurrentTcFocus(data.capture, { scroll: true });
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
          
            if (log.type === "SCENE_CHANGE") {
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

function startLogSimulation() {
    const logViewer = document.getElementById("logViewer");

    setInterval(() => {
        if (isPausing || logQueue.length === 0 || !logViewer) return;

        const log = logQueue.shift();

        // 1. Scene 변경 플래그를 만났을 때
        if (log.type === "CAMERA_CHANGE") {
            needsClear = true;
            return;
        }

        // 2. 실제 로그를 출력하기 직전, 비우기 예약이 되어 있다면?
        if (needsClear) {
            logViewer.innerHTML = ""; // 여기서 비웁니다!
            renderedLogs.clear();
            needsClear = false;       // 예약 해제
        }

        // 3. 기존 출력 로직 시작
        const logLine = document.createElement("div");
        logLine.className = "log-line-raw";

        const rawText = log.text;
        let text = rawText;

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

        if (logAutoFollow) {
            logViewer.scrollTop = logViewer.scrollHeight;
        }

        if (rawText.includes("Test results:")) {
            isPausing = true;
            setTimeout(() => { isPausing = false; }, LOG_RESULT_PAUSE_MS);
        }

        // 성능 유지용
        while (logViewer.childElementCount > 300) {
            logViewer.removeChild(logViewer.firstChild);
        }
    }, LOG_RENDER_INTERVAL_MS);
}

function init() {
  updateClock();
  renderTcTree();
  updateMetrics();
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

  updateStatus().then(fetchLiveLogs);

  setInterval(updateStatus, TC_STATUS_POLL_MS);
  setInterval(fetchLiveLogs, LOG_POLL_MS);

  refreshLiveFeed();
  setInterval(refreshLiveFeed, TC_STATUS_POLL_MS);

  if (typeof pollItsData === "function") {
    setInterval(pollItsData, 1500);
  }
}

init();
