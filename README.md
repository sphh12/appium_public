# Appium Mobile Test

## Overview

GME Remittance 앱의 E2E 자동화 테스트 프로젝트입니다.
Appium + Python 기반으로 Android/iOS 핵심 시나리오를 자동 검증합니다.

### Tech Stack

| 기술 | 버전 |
|------|------|
| Python | 3.10+ |
| Node.js | 18+ |
| Appium | 2.x |
| Pytest | 7.x |
| Allure Report | 2.x |
| Next.js (대시보드) | 15 |

---

## Quick Start

```bash
# 1. 저장소 클론
git clone https://github.com/sphh12/appium.git
cd appium

# 2. 의존성 설치
npm install
pip install -r requirements.txt

# 3. Appium 드라이버 설치
npx appium driver install uiautomator2   # Android
npx appium driver install xcuitest       # iOS (macOS만)

# 4. 환경변수 설정
cp .env.example .env
# .env 파일에 테스트 계정/APK 정보 입력

# 5. 테스트 실행
python tools/run_allure.py -- tests/android/gme1_test.py -v --platform=android
```

> 처음 설정하는 경우 [상세 설치 가이드](#설치-방법)를 참고하세요.

---

## 테스트 실행

### run_allure.py (권장)

테스트 실행 + Allure 리포트 생성 + 웹 대시보드 업로드를 한번에 처리합니다.
필수 패키지가 없으면 자동으로 설치합니다.

```bash
# Android 테스트
python tools/run_allure.py -- tests/android/gme1_test.py -v --platform=android

# iOS 테스트
python tools/run_allure.py -- tests/ios/ios_contacts_test.py -v --platform=ios

# 리포트 생성 후 브라우저에서 열기
python tools/run_allure.py --open -- tests/android/gme1_test.py -v --platform=android

# 대시보드 업로드 끄기
python tools/run_allure.py --no-upload -- tests/android/gme1_test.py -v --platform=android

# 비디오 녹화 포함
python tools/run_allure.py -- tests/android/gme1_test.py -v --platform=android --record-video
```

### Shell 스크립트 (권장)

```bash
# Android 테스트
./shell/run-aos.sh --basic_01_test          # Staging (기본)
./shell/run-aos.sh --basic_01_test --live   # Live
./shell/run-aos.sh --gme1_test --test test_Login  # 특정 테스트만

# iOS 테스트
./shell/run-ios.sh --ios_contacts_test

# 전체 테스트 + 리포트 열기
./shell/run-aos.sh --all --report
```

> - 파일명에서 `.py`는 생략 가능 (`--basic_01_test` = `--basic_01_test.py`)
> - `--stg` (기본) / `--live`로 실행 환경(APK) 지정 가능
> - 테스트 실행 → Allure 리포트 생성 → 웹 대시보드 업로드까지 자동 처리

### 수동 실행

```bash
# 터미널 1: Appium 서버
npx appium

# 터미널 2: 에뮬레이터/시뮬레이터
emulator -avd Pixel_6              # Android
open -a Simulator                  # iOS (macOS)

# 터미널 3: 테스트
pytest tests/android/gme1_test.py -v --platform=android
pytest tests/ios/ios_contacts_test.py -v --platform=ios
```

---

## 프로젝트 구조

```
appium/
├── config/
│   └── capabilities.py              # 디바이스 설정 (ANDROID_CAPS, IOS_CAPS)
├── pages/
│   ├── base_page.py                 # 공통 페이지 기능
│   └── sample_page.py               # 페이지 객체 예시
├── utils/
│   ├── auth.py                      # 로그인 모듈 (로그인/PIN 입력/팝업 처리)
│   ├── initial_screens.py           # 초기 화면 처리 (언어 선택/약관 동의)
│   ├── language.py                  # 앱 언어 설정
│   └── helpers.py                   # 유틸리티 (스크롤, 스크린샷 등)
├── tests/
│   ├── android/                     # Android 테스트
│   │   ├── gme1_test.py             # 메인 테스트 (로그인/홈)
│   │   ├── basic_01_test.py         # 기본 기능 테스트
│   │   ├── test_01.py               # 초기 화면 테스트
│   │   └── xml_test.py              # XML 시나리오 테스트
│   └── ios/                         # iOS 테스트
│       ├── ios_contacts_test.py     # 연락처 권한 테스트
│       └── test_ios_first.py        # iOS 기본 테스트
├── tools/
│   ├── run_allure.py                # Allure 리포트 생성 + 대시보드 업로드
│   ├── upload_to_dashboard.py       # Vercel 대시보드 업로드 (Blob 첨부파일 포함)
│   ├── update_dashboard.py          # 로컬 HTML 대시보드 업데이트
│   ├── export_summary.py            # Allure 경량 HTML 요약 Export
│   ├── explore_app.py               # 앱 화면 자동 탐색 스크립트
│   ├── ui_dump.py                   # Android UI 덤프 도구
│   ├── ui_dump_ios.py               # iOS UI 덤프 도구
│   ├── serve.py                     # 로컬 HTTP 서버
│   ├── debug_keyboard.py            # 보안 키보드 디버깅 도구
│   └── test_login_live.py           # Live 로그인 테스트 도구
├── shell/
│   ├── run-app.sh                   # 전체 기능 실행 스크립트
│   ├── run-aos.sh                   # Android 간편 실행
│   ├── run-ios.sh                   # iOS 간편 실행
│   └── bootstrap.ps1                # Windows 초기 설정 스크립트
├── docs/                            # 가이드 문서
├── apk/                             # APK 파일 (Git 미포함)
├── ui_dumps/                        # UI 덤프 XML 저장소
├── allure-results/                  # Allure 테스트 결과 (타임스탬프별)
├── allure-reports/                  # Allure HTML 리포트
├── conftest.py                      # pytest fixture 설정
├── requirements.txt                 # Python 패키지
├── package.json                     # Node.js 패키지
├── .env                             # 환경변수 (Git 미포함)
└── .env.example                     # 환경변수 템플릿
```

---

## Allure 리포트 & 웹 대시보드

### 웹 대시보드 (Vercel)

테스트 실행 결과가 자동으로 웹 대시보드에 업로드됩니다.

- **대시보드 URL**: https://allure-dashboard-three.vercel.app
- 실행 이력 목록, 테스트 통계, 첨부파일(스크린샷/비디오/로그) 확인 가능
- `run_allure.py` 실행 시 `--upload` 옵션이 기본 활성화됨

### Allure 설치 (최초 1회)

```bash
# macOS
brew install allure

# Windows
scoop install allure
# 또는
choco install allure
```

### 리포트 생성

```bash
# 테스트 실행 + 리포트 생성 + 대시보드 업로드
python tools/run_allure.py -- tests/android/gme1_test.py -v --platform=android

# 리포트만 열기 (업로드 없이)
python tools/run_allure.py --no-upload --open -- tests/android/gme1_test.py -v --platform=android
```

### 로컬 리포트 확인

실행 이력은 `allure-reports/YYYYMMDD_HHMMSS/` 형태로 로컬에도 보관됩니다.

```bash
# 최신 리포트
open allure-reports/LATEST/index.html

# 로컬 대시보드 (간단 서버 필요)
python -m http.server 8000
# http://127.0.0.1:8000/allure-reports/dashboard/
```

상세 가이드: [docs/ALLURE_REPORT_GUIDE.md](docs/ALLURE_REPORT_GUIDE.md)

---

## 환경 설정

### 환경 변수

`.env.example`을 `.env`로 복사한 후 실제 값을 입력합니다.

| 변수 | 설명 | 필수 |
|------|------|------|
| `STG_ID` / `STG_PW` | Staging 테스트 계정 | Staging 시 |
| `LIVE_ID` / `LIVE_PW` | Live 테스트 계정 | Live 시 |
| `SIMPLE_PIN` | 간편비밀번호 4자리 | 로그인 후 |
| `GME_RESOURCE_ID_PREFIX` | resource-id 접두사 | 선택 |
| `STG_APK` / `LIVE_APK` | APK 파일명 | 앱 설치 시 |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob 토큰 (첨부파일 업로드용) | 선택 |
| `APPIUM_HOST` / `APPIUM_PORT` | Appium 서버 주소 | 선택 |
| `ANDROID_UDID` | 실물 디바이스 시리얼 | 실기기 시 |

### APK 파일

APK 파일은 Git에 포함되지 않습니다:

1. `apk/` 폴더에 APK 복사
2. `.env`에 파일명 설정 (`STG_APK`, `LIVE_APK`)

### 환경 변수 (시스템)

**macOS:**
```bash
# ~/.zshrc에 추가
export JAVA_HOME=$(/usr/libexec/java_home)
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator
```

**Windows:**

| 변수명 | 값 (예시) |
|--------|----------|
| `JAVA_HOME` | `C:\Program Files\Eclipse Adoptium\jdk-17` |
| `ANDROID_HOME` | `C:\Users\{사용자명}\AppData\Local\Android\Sdk` |

PATH에 추가: `%JAVA_HOME%\bin`, `%ANDROID_HOME%\platform-tools`, `%ANDROID_HOME%\emulator`

---

## 설치 방법

> 빠른 클론 가이드: [docs/README_CLONE.md](docs/README_CLONE.md)

### 필수 프로그램

| 프로그램 | macOS | Windows |
|----------|-------|---------|
| Node.js 18+ | `brew install node` | https://nodejs.org/ |
| Python 3.10+ | `brew install python@3.10` | https://www.python.org/downloads/ |
| Java JDK 17 | `brew install --cask temurin` | https://adoptium.net/ |
| Android Studio | `brew install --cask android-studio` | https://developer.android.com/studio |
| Allure | `brew install allure` | `scoop install allure` |
| Git | 기본 설치됨 | https://git-scm.com/ |

### 설치 순서

1. **필수 프로그램 설치** (위 표 참고)

2. **환경 변수 설정** (위 [환경 설정](#환경-설정) 참고)

3. **Android 에뮬레이터 생성**
   - Android Studio → Tools → Device Manager
   - Pixel 6 + API 34 권장

4. **프로젝트 설정**
   ```bash
   git clone https://github.com/sphh12/appium.git
   cd appium
   npm install
   npx appium driver install uiautomator2
   pip install -r requirements.txt
   cp .env.example .env
   # .env 파일 편집
   ```

5. **iOS 설정 (macOS만)**
   ```bash
   npx appium driver install xcuitest
   # Xcode + 시뮬레이터 설치 필요
   ```
   상세 가이드: [docs/IOS_SETUP_GUIDE.md](docs/IOS_SETUP_GUIDE.md)

6. **설치 확인**
   ```bash
   npx appium --version
   npx appium driver list --installed
   python -c "import pytest; print(pytest.__version__)"
   ```

---

## 문서

| 문서 | 설명 |
|------|------|
| [ALLURE_REPORT_GUIDE.md](docs/ALLURE_REPORT_GUIDE.md) | Allure 리포트 탭별 설명, 분석 루틴, 진단 파일 활용 |
| [UI_DUMP_GUIDE.md](docs/UI_DUMP_GUIDE.md) | UI Dump 도구 사용법, XML 분석, Locator 전략 |
| [CODING_GUIDELINES.md](docs/CODING_GUIDELINES.md) | 테스트 스크립트 작성 규칙 |
| [APP_STRUCTURE.md](docs/APP_STRUCTURE.md) | GME 앱 화면 구조, resource-id 정리 |
| [IOS_SETUP_GUIDE.md](docs/IOS_SETUP_GUIDE.md) | iOS 자동화 환경 세팅 (Xcode, XCUITest) |
| [IOS_TEST_GUIDE.md](docs/IOS_TEST_GUIDE.md) | iOS 테스트 작성 가이드 |
| [MAC_SETUP_GUIDE.md](docs/MAC_SETUP_GUIDE.md) | macOS Appium 환경 세팅 |
| [README_CLONE.md](docs/README_CLONE.md) | 클론 후 초기 환경 구성 |

---

## 문제 해결

| 에러 | 원인 | 해결 |
|------|------|------|
| `ConnectionRefusedError` | Appium 서버 미실행 | `npx appium` |
| `No device found` | 에뮬레이터 미연결 | `adb devices`로 확인, 에뮬레이터 시작 |
| `App not found` | APK 파일 없음 | `apk/` 폴더에 APK 복사 |
| `NoSuchElementException` | Locator 오류 | `python tools/ui_dump.py -w`로 확인 |
| `No module named 'pytest'` | Python 패키지 미설치 | `pip install -r requirements.txt` |
| `JAVA_HOME is not set` | 환경 변수 미설정 | 시스템 환경 변수에 추가 |

---

## Appium Inspector

UI 요소를 탐색하는 도구입니다.

**다운로드:** https://github.com/appium/appium-inspector/releases

**설정:**
| 항목 | 값 |
|------|-----|
| Remote Host | `127.0.0.1` |
| Remote Port | `4723` |
| Remote Path | `/` |

> Appium Inspector 대신 `python tools/ui_dump.py -w` (Watch 모드)를 사용하면 더 빠르게 UI 요소를 확인할 수 있습니다.

---

## 참고 링크

- [Appium 공식 문서](https://appium.io/docs/en/latest/)
- [Appium Inspector](https://github.com/appium/appium-inspector/releases)
- [Pytest 문서](https://docs.pytest.org/)
- [Allure Report](https://docs.qameta.io/allure/)
- [웹 대시보드](https://allure-dashboard-three.vercel.app)
