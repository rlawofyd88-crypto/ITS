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

// --- CameraITS 테스트 구조 정의 ---
// 실제 데이터 연동 전까지 샘플 데이터를 생성.
const itsTestStructure = [
  { scene: "scene0", tests: ["test_burst_capture", "test_jitter", "test_metadata"] },
  { scene: "scene1_1", tests: ["test_3a", "test_ae_precapture_trigger", "test_crop_region_raw"] },
  { scene: "scene1_2", tests: ["test_raw_sensitivity", "test_yuv_plus_raw"] },
  { scene: "scene2_a", tests: ["test_effects", "test_format_combos"] },
  { scene: "scene3", tests: ["test_lens_movement_reporting", "test_reprocess_edge_enhancement"] },
  { scene: "scene4", tests: ["test_aspect_ratio_and_crop"] }
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

// function updateCompare(value) {
//   const rightInset = 100 - value;
//   referenceImage.style.clipPath = `inset(0 ${rightInset}% 0 0)`;
//   divider.style.left = `${value}%`;
// }

// compareSlider.addEventListener("input", (event) => {
//   updateCompare(Number(event.target.value));
// });

// --- TC 리스트 렌더링 함수 ---
function renderTcTree() {
  tcListContainer.innerHTML = ""; // 초기화

  itsTestStructure.forEach((item) => {
    const groupLi = document.createElement("li");
    groupLi.className = "tc-group";

    // Scene 이름 (폴더명 형식)
    groupLi.innerHTML = `<span class="group-title">${item.scene}</span>`;

    const childUl = document.createElement("ul");
    item.tests.forEach((testName) => {
      // ID 생성 시 공백이나 특수문자 처리를 위해 안전한 ID 생성
      const safeId = `${item.scene}-${testName}`.replace(/\./g, "_");

      const tcLi = document.createElement("li");
      tcLi.className = "tc-item";
      tcLi.id = safeId;
      tcLi.innerHTML = `
        <span class="tc-name">${testName}</span>
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
 * @param {string} scene - scene0, scene1_1 등
 * @param {string} testName - 테스트 파일명
 * @param {'PASS' | 'FAIL' | 'SKIP' | 'RUNNING'} status
 */
function setTcResult(scene, testName, status) {
  const targetId = `${scene}-${testName}`.replace(/\./g, "_");
  const item = document.getElementById(targetId);
  if (!item) return;

  const statusLabel = item.querySelector(".tc-status");
  statusLabel.textContent = status;
  statusLabel.className = `tc-status ${status.toLowerCase()}`;
}

updateClock();
renderTcTree();
updateMetrics();
//updateCompare(Number(compareSlider.value));
setInterval(updateClock, 1000);
setInterval(updateMetrics, 900);
pollItsData();
setInterval(pollItsData, 1500);
refreshLiveFeed();
setInterval(refreshLiveFeed, 1000);
refreshLiveState();
setInterval(refreshLiveState, 1500);
setTcResult('tc-1-1', 'PASS');