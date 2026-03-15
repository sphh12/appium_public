# Pytest 직접 실행 가이드

## 사전 준비

pytest로 직접 실행할 경우, 아래 3가지가 미리 준비되어 있어야 합니다.

```bash
# 1. venv 활성화
source venv/bin/activate

# 2. Appium 서버 실행
npx appium

# 3. 에뮬레이터/시뮬레이터 실행
emulator -avd Pixel_8            # Android
open -a Simulator                # iOS (macOS)
```

> 쉘 스크립트(`run-aos.sh`, `run-ios.sh`)는 위 사전 작업을 자동으로 처리합니다.

---

## 기본 실행

```bash
pytest tests/android/<파일>.py -v --platform=android
pytest tests/ios/<파일>.py -v --platform=ios
```

---

## 환경별 실행 (APP_ENV)

`APP_ENV` 환경변수로 APK, resource-id 접두사, 계정 정보가 자동 전환됩니다.

```bash
# Staging (기본값)
APP_ENV=stage pytest tests/android/sample1_test.py -v --platform=android

# Live
APP_ENV=live pytest tests/android/sample1_test.py -v --platform=android

# Livetest
APP_ENV=livetest pytest tests/android/sample1_test.py -v --platform=android
```

| APP_ENV | APK 폴더 | resource-id 접두사 | 계정 | 키보드 |
|---------|----------|-------------------|------|--------|
| `stage` | `apk/stage/` | `...stag:id` | STG_ID / STG_PW | 숫자 키패드 |
| `live` | `apk/live/` | `...:id` | LIVE_ID / LIVE_PW | QWERTY |
| `livetest` | `apk/livetest/` | `...livetest:id` | LIVE_ID / LIVE_PW | QWERTY |

---

## 특정 테스트 실행

```bash
# 특정 클래스::메서드
pytest tests/android/sample1_test.py::TestAndroidSample::test_Login -v --platform=android

# 키워드 필터 (-k)
pytest tests/android/sample1_test.py -v --platform=android -k "Login"
pytest tests/android/sample1_test.py -v --platform=android -k "Login or Language"

# 여러 파일 동시 실행
pytest tests/android/sample1_test.py tests/android/basic_01_test.py -v --platform=android

# 전체 Android 테스트
pytest tests/android/ -v --platform=android

# 전체 iOS 테스트
pytest tests/ios/ -v --platform=ios
```

---

## 주요 옵션

### 기본 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `-v` | 상세 출력 (테스트별 PASS/FAIL 표시) | `pytest -v` |
| `-s` | print() 출력 표시 (캡처 비활성화) | `pytest -s` |
| `-x` | 첫 번째 실패 시 즉시 중단 | `pytest -x` |
| `-k "키워드"` | 테스트 이름 필터링 | `pytest -k "Login"` |
| `--tb=short` | 트레이스백 간략 표시 (기본) | `pytest --tb=short` |
| `--tb=long` | 트레이스백 상세 표시 | `pytest --tb=long` |
| `--tb=no` | 트레이스백 숨기기 | `pytest --tb=no` |

### Appium 전용 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--platform` | 플랫폼 선택 (android/ios) | `--platform=android` |
| `--app` | APK/IPA 경로 직접 지정 (config 덮어쓰기) | `--app /path/to/app.apk` |
| `--record-video` | 화면 녹화 (실패 시 Allure에 첨부) | `--record-video` |
| `--allure-attach` | 첨부 정책 (hybrid/all/fail-skip) | `--allure-attach all` |

### 첨부 정책 (`--allure-attach`)

| 모드 | PASS 시 | FAIL/SKIP/BROKEN 시 |
|------|---------|---------------------|
| `hybrid` (기본) | 없음 | 스크린샷 + XML + Capabilities + Logcat |
| `all` | 스크린샷 + XML | 스크린샷 + XML + Capabilities + Logcat |
| `fail-skip` | 없음 | 스크린샷 + XML + Capabilities + Logcat |

---

## 마커 (Marker)

테스트에 마커를 붙여 선택적으로 실행할 수 있습니다.

```bash
# 스모크 테스트만 실행
pytest tests/android/ -v --platform=android -m smoke

# 리그레션 테스트만 실행
pytest tests/android/ -v --platform=android -m regression

# Android 마커가 붙은 테스트만
pytest tests/ -v -m android
```

등록된 마커:

| 마커 | 설명 |
|------|------|
| `@pytest.mark.android` | Android 전용 |
| `@pytest.mark.ios` | iOS 전용 |
| `@pytest.mark.smoke` | 스모크 테스트 |
| `@pytest.mark.regression` | 리그레션 테스트 |
| `@pytest.mark.skip_initial_screens` | 초기 화면 처리 비활성화 |

---

## Allure 리포트 (수동)

pytest 직접 실행 시 Allure 결과 파일(`allure-results/`)은 자동 생성되지만, HTML 리포트 생성과 대시보드 업로드는 별도로 해야 합니다.

```bash
# 1. HTML 리포트 생성
allure generate allure-results -o allure-report --clean

# 2. 브라우저에서 열기
allure open allure-report

# 3. 또는 서버 모드로 열기 (자동 브라우저 오픈)
allure serve allure-results

# 4. 대시보드 업로드 (선택)
python tools/upload_to_dashboard.py
```

---

## 실행 예시 모음

```bash
# 가장 기본적인 실행
pytest tests/android/sample1_test.py -v --platform=android

# Livetest + 특정 테스트 + 상세 로그
APP_ENV=livetest pytest tests/android/sample1_test.py::TestAndroidSample::test_Login -v -s --platform=android

# 비디오 녹화 포함 + 전체 첨부
pytest tests/android/sample1_test.py -v --platform=android --record-video --allure-attach all

# 첫 실패 시 중단 + 상세 트레이스백
pytest tests/android/ -v -x --tb=long --platform=android

# APK 직접 지정
pytest tests/android/sample1_test.py -v --platform=android --app /path/to/custom.apk

# iOS 연락처 테스트
pytest tests/ios/ios_contacts_test.py -v --platform=ios
```

---

## pytest vs 쉘 스크립트 비교

| 항목 | pytest 직접 실행 | 쉘 스크립트 (run-aos.sh) |
|------|-----------------|------------------------|
| Appium 서버 | 수동 시작 필요 | 자동 시작 |
| 에뮬레이터 | 수동 시작 필요 | 자동 부팅 |
| venv 활성화 | 수동 필요 | 자동 처리 |
| 드라이버 확인 | 수동 확인 | 자동 확인/설치 |
| Allure 리포트 | 수동 생성 | 자동 생성 |
| 대시보드 업로드 | 수동 실행 | 자동 업로드 |
| 실행 속도 | 빠름 (사전 작업 없음) | 약간 느림 (체크 단계 포함) |
| 적합한 상황 | 개발/디버깅 중 빠른 반복 실행 | CI/CD, 전체 파이프라인 실행 |
