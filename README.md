# 📱 Appium Mobile Test Automation

> Appium + Python 기반의 End-to-End 모바일 자동화 테스트 프레임워크

GME Remittance 송금 앱의 핵심 시나리오를 Android/iOS 양쪽에서 자동 검증하고, 실행 결과를 자체 구축한 웹 대시보드로 시각화합니다.

---

## 🌐 Live Demo

> **▶ [Allure Dashboard 데모 보기](https://allure-dashboard-git-feat-public-demo-sph12test-6232s-projects.vercel.app)**
>
> 마스킹 처리된 실제 테스트 실행 데이터 확인 가능 · 누구나 접속 가능

### 데모에서 확인할 수 있는 것

| 기능 | 설명 |
|------|------|
| 📊 **실행 이력 타임라인** | 일자별 테스트 결과 추이, Pass Rate 그래프 |
| 🥧 **인터랙티브 차트** | Status / Platform 도넛 + Bar 차트, 클릭 필터링 |
| 🤖 **AI 실패 분석** | 외부 AI API로 실패 케이스 자동 분석 |
| 📎 **첨부파일 뷰어** | 스크린샷, 비디오, logcat 미리보기 |
| 🌓 **다크/라이트 모드** | localStorage 기반 테마 토글 |
| 📱 **반응형 디자인** | 모바일/태블릿/데스크톱 최적화 |

---

## ✨ 주요 특징

### 테스트 프레임워크
- **Cross-platform**: Android (UiAutomator2) + iOS (XCUITest) 동시 지원
- **Page Object Model**: `pages/`, `utils/` 분리 구조
- **자동 초기 화면 처리**: 언어 선택, 약관 동의, 보안 키보드 자동 입력
- **환경별 분기**: Staging / Live / Livetest APK 자동 선택
- **Class 단위 드라이버 공유**: 로그인 1회로 다중 시나리오 실행 (Local Transfer 등)

### 리포팅 & 대시보드
- **Allure Report 통합**: 자동 생성 + 브라우저 자동 오픈
- **Vercel 웹 대시보드** (Next.js 15 + Prisma 6 + PostgreSQL)
- **Vercel Blob**: 스크린샷/비디오/로그 첨부파일 클라우드 저장
- **AI 실패 분석**: 에러 + 스크린샷 + page_source를 외부 AI에 전송하여 자동 분석
- **Teams Webhook 알림**: 테스트 결과를 Teams 채널로 자동 전송

### 도구
- **UI Dump (Watch 모드)**: 화면 변화 자동 감지 + 민감정보 자동 마스킹
- **App Explorer**: 앱 화면 자동 탐색 + 팝업 자동 처리
- **트리거 시스템**: 대시보드에서 원격으로 테스트 실행 요청 가능

---

## 🚀 Quick Start

```bash
# 1. 클론 + 의존성
git clone https://github.com/sphh12/appium_public.git
cd appium_public
npm install
pip install -r requirements.txt

# 2. Appium 드라이버
npx appium driver install uiautomator2   # Android
npx appium driver install xcuitest       # iOS (macOS only)

# 3. 환경변수 + APK
cp .env.example .env
# .env에 테스트 계정 입력 / apk/stage/, apk/live/ 폴더에 APK 배치

# 4. 실행
python tools/run_allure.py -- tests/android/gme1_test.py -v --platform=android
```

리포트가 자동으로 생성되어 브라우저에 열리고, Vercel 대시보드에 업로드됩니다.

---

## 🛠 Tech Stack

| 영역 | 기술 |
|------|------|
| **Test Framework** | Appium 2.x · Pytest 7.x · Selenium WebDriver |
| **Language** | Python 3.10+ |
| **Reporting** | Allure Report 2.x · 자체 Web Dashboard |
| **Web Dashboard** | Next.js 15 · TypeScript · Tailwind CSS v4 · Prisma 6 |
| **Database / Storage** | PostgreSQL (Neon) · Vercel Blob |
| **AI Integration** | 외부 AI API (실패 분석) |
| **CI / Deploy** | Vercel (자동 배포) |
| **Notification** | Teams Incoming Webhook |

---

## 📂 프로젝트 구조

```
appium_public/
├── config/capabilities.py       # 디바이스 설정
├── pages/                       # Page Object Model
├── utils/
│   ├── auth.py                  # 로그인 + 보안 키보드 + 팝업 처리
│   ├── initial_screens.py       # 언어 선택 + 약관 동의
│   ├── language.py              # 앱 언어 설정
│   └── helpers.py               # 스크롤, 스크린샷, 진단 파일
├── tests/
│   ├── android/                 # Android 테스트 (gme1, basic_01, local_transfer 등)
│   └── ios/                     # iOS 테스트 (contacts, first 등)
├── tools/
│   ├── run_allure.py            # 테스트 + 리포트 + 대시보드 통합 실행
│   ├── upload_to_dashboard.py   # Vercel 업로드 + AI 분석
│   ├── teams_notify.py          # Teams Webhook 알림
│   ├── trigger_listener.py      # 대시보드 트리거 폴링
│   ├── ui_dump.py               # UI Dump (Watch 모드 + 민감정보 마스킹)
│   └── explore_app.py           # 앱 자동 탐색
├── shell/
│   ├── run-aos.sh / run-ios.sh  # 플랫폼별 간편 실행 스크립트
│   └── bootstrap.ps1            # Windows 초기 설정
├── conftest.py                  # pytest fixture (drivers, app info auto-extract)
└── .env.example                 # 환경변수 템플릿
```

---

## 💻 테스트 실행 옵션

### 권장: `run_allure.py`

테스트 실행 + Allure 리포트 + 대시보드 업로드를 한 번에 처리합니다.

```bash
# Android
python tools/run_allure.py -- tests/android/local_transfer_test.py -v --platform=android

# iOS
python tools/run_allure.py -- tests/ios/ios_contacts_test.py -v --platform=ios

# 옵션
--open              # 리포트 생성 후 브라우저 자동 오픈
--no-upload         # 대시보드 업로드 끄기
--record-video      # 비디오 녹화 + 실패 시 Allure 첨부
```

### Shell 스크립트

```bash
./shell/run-aos.sh --basic_01_test --live              # Live 환경
./shell/run-aos.sh --gme1_test --test test_Login       # 특정 테스트만
./shell/run-aos.sh --all --report                      # 전체 + 리포트 오픈
./shell/run-ios.sh --ios_contacts_test
```

### 수동 실행

```bash
# 터미널 1: Appium 서버
npx appium

# 터미널 2: 에뮬레이터
emulator -avd Pixel_6

# 터미널 3: 테스트
pytest tests/android/gme1_test.py -v --platform=android
```

---

## 🔧 환경 설정

### 환경 변수 (`.env`)

| 변수 | 설명 | 필수 |
|------|------|------|
| `STG_ID` / `STG_PW` | Staging 테스트 계정 | Staging 시 |
| `LIVE_ID` / `LIVE_PW` | Live 테스트 계정 | Live 시 |
| `SIMPLE_PIN` | 간편비밀번호 4자리 | 로그인 후 |
| `APP_ENV` | APK 환경 (`stage`/`live`/`livetest`) | 기본: stage |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob 토큰 | 첨부파일 업로드 시 |
| `TEAMS_WEBHOOK_URL` | Teams Webhook URL | 알림 사용 시 |
| `DASHBOARD_URL` | 웹 대시보드 URL | 업로드 시 |

### APK 파일

```
apk/stage/<APK_파일>     # Staging
apk/live/<APK_파일>      # Live
apk/livetest/<APK_파일>  # Livetest
```

폴더 내 첫 번째 `.apk` 파일이 자동으로 인식됩니다.

### 시스템 환경 변수

**macOS** (`~/.zshrc`):
```bash
export JAVA_HOME=$(/usr/libexec/java_home)
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator
```

**Windows**: 시스템 환경 변수에 `JAVA_HOME`, `ANDROID_HOME` 추가, PATH에 `%JAVA_HOME%\bin`, `%ANDROID_HOME%\platform-tools` 추가

---

## 📦 필수 프로그램

| 프로그램 | macOS | Windows |
|----------|-------|---------|
| Node.js 18+ | `brew install node` | https://nodejs.org/ |
| Python 3.10+ | `brew install python@3.10` | https://www.python.org/ |
| Java JDK 17 | `brew install --cask temurin` | https://adoptium.net/ |
| Android Studio | `brew install --cask android-studio` | https://developer.android.com/studio |
| Allure | `brew install allure` | `scoop install allure` |

---

## 🐛 문제 해결

| 에러 | 해결 |
|------|------|
| `ConnectionRefusedError` | `npx appium`으로 서버 실행 |
| `No device found` | `adb devices`로 확인, 에뮬레이터 시작 |
| `App not found` | `apk/<env>/` 폴더에 APK 배치 |
| `NoSuchElementException` | `python tools/ui_dump.py -w`로 Locator 확인 |
| `JAVA_HOME is not set` | 시스템 환경 변수에 추가 |

---

## 🔗 참고 링크

- [📊 공개 데모 대시보드](https://allure-dashboard-git-feat-public-demo-sph12test-6232s-projects.vercel.app)
- [Appium 공식 문서](https://appium.io/docs/en/latest/)
- [Pytest 문서](https://docs.pytest.org/)
- [Allure Report](https://docs.qameta.io/allure/)
