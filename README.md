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

---

## Quick Start

```bash
# 1. 저장소 클론
git clone https://gitlab.com/sphh12/appium.git
cd appium

# 2. 의존성 설치
npm install
pip install -r requirements.txt

# 3. Appium 드라이버 설치
npx appium driver install uiautomator2

# 4. 테스트 실행 (Git Bash에서)
./run-app.sh --gme1_test
```

> 처음 설정하는 경우 [상세 설치 가이드](#설치-방법)를 참고하세요.

---

## 테스트 실행

### Shell 스크립트 (권장)

```bash
# 단일 테스트 파일 실행
./run-app.sh --gme1_test
./run-app.sh --xml_test

# 특정 테스트만 실행
./run-app.sh --gme1_test --test test_Login

# 여러 파일 실행
./run-app.sh --files "tests/android/gme1_test.py tests/android/xml_test.py"

# 전체 테스트 + Allure 리포트
./run-app.sh --all --report
```

스크립트가 자동으로 처리하는 것:
- Appium 서버 시작
- 에뮬레이터 연결
- Python 가상환경 활성화
- 테스트 실행

### 수동 실행

```bash
# 터미널 1: Appium 서버
npm run appium:start

# 터미널 2: 에뮬레이터
emulator -avd Pixel_6

# 터미널 3: 테스트
.\venv\Scripts\activate
pytest tests/android/gme1_test.py -v --platform=android
```

---

## 프로젝트 구조

```
appium/
├── config/
│   └── capabilities.py      # 디바이스 설정
├── pages/
│   ├── base_page.py         # 공통 페이지 기능
│   └── sample_page.py       # 페이지 객체
├── tests/
│   ├── android/             # Android 테스트
│   │   ├── gme1_test.py     # 메인 테스트
│   │   └── xml_test.py      # XML 시나리오 테스트
│   └── ios/                 # iOS 테스트
├── tools/
│   └── run_allure.py        # Allure 리포트 생성
├── shell/
│   └── run-app.sh           # 테스트 실행 스크립트
├── apk/                     # APK 파일 (Git 미포함)
├── conftest.py              # pytest 설정
├── requirements.txt         # Python 패키지
└── package.json             # Node.js 패키지
```

---

## 사용 예시

### 테스트 코드 작성

```python
# tests/android/sample_test.py
import pytest
from pages.login_page import LoginPage

@pytest.mark.android
def test_login(driver):
    login_page = LoginPage(driver)
    login_page.enter_credentials("user@test.com", "password123")
    login_page.tap_login_button()
    assert login_page.is_logged_in()
```

### XML 기반 시나리오 테스트

```python
# XML 파일에서 시나리오 로드
./run-app.sh --xml_test
```

---

## 환경 설정

### APK 파일

APK 파일은 Git에 포함되지 않습니다. 별도로 준비해야 합니다:

1. 팀 공유 폴더 또는 CI/CD에서 APK 다운로드
2. `apk/` 폴더에 복사
3. 예: `apk/[Stg]GME_7.13.0.apk`

### 환경 변수

| 변수명 | 값 (예시) |
|--------|----------|
| `JAVA_HOME` | `C:\Program Files\Eclipse Adoptium\jdk-17` |
| `ANDROID_HOME` | `C:\Users\{사용자명}\AppData\Local\Android\Sdk` |

PATH에 추가:
```
%JAVA_HOME%\bin
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\emulator
```

### Capabilities 설정

```json
{
  "platformName": "Android",
  "appium:automationName": "UiAutomator2",
  "appium:deviceName": "Android Emulator",
  "appium:platformVersion": "14",
  "appium:app": "./apk/[Stg]GME_7.13.0.apk",
  "appium:noReset": false,
  "appium:autoGrantPermissions": true
}
```

---

## Allure 리포트

### 설치 (최초 1회)

```bash
# Windows
scoop install allure
# 또는
choco install allure
```

### 리포트 생성

```bash
# 테스트 실행 + 리포트 생성
python tools/run_allure.py -- tests/android/gme1_test.py -v --platform=android

# 리포트 열기
allure serve allure-results
```

### 대시보드

실행 이력을 `allure-reports/YYYYMMDD_HHMMSS/` 형태로 보관합니다.

```bash
# 대시보드 서버 실행
python -m http.server 8000

# 브라우저에서 접속
# http://127.0.0.1:8000/allure-reports/dashboard/
```

상세 가이드: [docs/ALLURE_REPORT_GUIDE.md](docs/ALLURE_REPORT_GUIDE.md)

---

## 설치 방법

> 빠른 클론 가이드: [docs/README_CLONE.md](docs/README_CLONE.md)

### 필수 프로그램

| 프로그램 | 다운로드 |
|----------|----------|
| Node.js 18+ | https://nodejs.org/ |
| Python 3.10+ | https://www.python.org/downloads/ |
| Java JDK 17 | https://adoptium.net/ |
| Android Studio | https://developer.android.com/studio |
| Git | https://git-scm.com/ |

### 설치 순서

1. **필수 프로그램 설치** (위 표 참고)

2. **환경 변수 설정**
   - `JAVA_HOME`, `ANDROID_HOME` 설정
   - PATH에 bin 경로들 추가

3. **Android 에뮬레이터 생성**
   - Android Studio → Tools → Device Manager
   - Pixel 6 + API 34 권장

4. **프로젝트 설정**
   ```bash
   git clone https://gitlab.com/sphh12/appium.git
   cd appium
   npm install
   npx appium driver install uiautomator2
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

5. **설치 확인**
   ```bash
   npx appium --version
   npx appium driver list --installed
   ```

---

## 문제 해결

| 에러 | 원인 | 해결 |
|------|------|------|
| `ConnectionRefusedError` | Appium 서버 미실행 | `npm run appium:start` |
| `No device found` | 에뮬레이터 미연결 | `adb devices`로 확인, 에뮬레이터 시작 |
| `App not found` | APK 파일 없음 | `apk/` 폴더에 APK 복사 |
| `NoSuchElementException` | Locator 오류 | Appium Inspector로 확인 |
| `command not found` (Windows) | PowerShell에서 실행 | Git Bash 사용 |
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

---

## 참고 링크

- [Appium 공식 문서](https://appium.io/docs/en/latest/)
- [Appium Inspector](https://github.com/appium/appium-inspector/releases)
- [Pytest 문서](https://docs.pytest.org/)
- [Allure Report](https://docs.qameta.io/allure/)
