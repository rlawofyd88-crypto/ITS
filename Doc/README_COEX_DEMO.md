# COEX Android ITS Demo Dashboard

브라이센코리아 공식 홈페이지의 `/img/logo.png` 로고를 `assets/brycen-logo.png`로 내려받아 헤더에 배치했습니다.

## 화면 구성

전시 모니터 1대 기준으로 `index.html`을 전체 화면으로 띄우는 구성을 권장합니다.

1. 좌측 대형 영역: ITS 실시간 카메라/디바이스 입력
2. 우측 상단: ITS 분석 결과 시각화
3. 우측 하단: Raw Capture / Reference Check 비교

## 실행 방법

`C:\Users\jr.kim\Desktop\ITS\index.html` 파일을 Chrome 또는 Edge에서 열고 `F11`로 전체 화면 전환합니다.

## 실제 ITS Box 연결 방식

현장 안정성을 기준으로는 아래 순서를 추천합니다.

1. OBS Studio에서 Android 화면 또는 ITS Box 출력 영상을 캡처합니다.
2. 브라우저에는 이 대시보드를 전체 화면으로 띄웁니다.
3. 필요하면 OBS에서 브라우저 소스와 캡처 소스를 합성해 전시 모니터에 출력합니다.

대시보드 안에 실제 영상을 직접 넣고 싶다면 `index.html`의 `.camera-scene` 영역을 `<video>` 또는 캡처 이미지 스트림으로 교체하면 됩니다.

## Google Camera ITS 연동

Google Camera ITS는 Android CTS의 `cts/apps/CameraITS`에서 실행하는 호스트 기반 테스트입니다. 실제 연동은 아래처럼 분리하는 것을 권장합니다.

1. Google Camera ITS 실행: `python tools/run_all_tests.py`
2. WSL 기준 `/tmp/CameraITS_*` 결과 폴더 생성 확인
3. `tools/its_monitor_server.py`가 `/tmp`의 최신 결과 폴더를 읽어 `its-status.json`, 로그, 최신 캡처 이미지를 제공
4. 대시보드는 해당 API를 주기적으로 읽어 그래프와 `03 / Test Capture` 이미지를 갱신

예시:

```bash
python3 tools/its_monitor_server.py
```

실제 연동 시에는 브라우저 보안 정책 차이를 피하기 위해 대시보드 폴더도 로컬 서버로 띄우는 것을 권장합니다.

```bash
python3 -m http.server 8080
```

브라우저 주소:

```text
http://127.0.0.1:8080/index.html
```

데이터 계약은 `data/sample-its-status.json`을 기준으로 합니다.

실제 실행 결과를 정적 JSON으로 반영하고 싶다면:

```bash
python3 tools/export_its_status.py --results-dir "/tmp/CameraITS_result_dir" --output "./data/latest-its-status.json"
```

브라우저 주소:

```text
http://127.0.0.1:8080/index.html?data=http://127.0.0.1:8080/data/latest-its-status.json
```

## 전시 메시지

관람객에게는 다음 흐름으로 설명하면 짧고 선명합니다.

1. ITS Box가 Android 카메라 테스트 이미지를 실시간으로 수집합니다.
2. 수집된 프레임은 색 정확도, 선명도, 노출, 결함 탐지 항목으로 검사됩니다.
3. Raw Capture / Reference Check 화면에서 원본 캡처가 기준 차트와 얼마나 일치하는지 확인합니다.
4. 이 흐름은 GMS 인증 대응 가능한 ITS Box 기반 검증 프로세스입니다.

## 당일 체크리스트

1. 모니터 해상도는 1920x1080 이상 권장
2. 브라우저 확대/축소 100%
3. Windows 절전 모드 해제
4. Android 디바이스 화면 꺼짐 방지
5. 네트워크 없이도 대시보드가 열리는지 사전 확인
