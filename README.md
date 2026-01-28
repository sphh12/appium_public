# Appium Mobile Test Framework

모바일 앱 자동화 테스트 프레임워크 (Android/iOS)

## Overview

Appium 기반 모바일 앱 테스트 자동화 프레임워크입니다.
- **Pytest** 기반 테스트 실행
- **Allure** 리포트 생성
- **Page Object Model** 패턴 적용
- Android/iOS 크로스 플랫폼 지원

## Tech Stack

| 구분 | 기술 |
|------|------|
| 테스트 프레임워크 | Pytest |
| 모바일 자동화 | Appium 2.x, UiAutomator2 (Android), XCUITest (iOS) |
| 리포트 | Allure Report |
| 언어 | Python 3.10+ |

## Quick Start

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd appium-mobile-test

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. Appium 서버 실행

```bash
# Appium 설치 (최초 1회)
npm install -g appium
appium driver install uiautomator2

# 서버 실행
appium
```

### 3. 앱 파일 배치

```bash
# apk 폴더 생성 및 앱 파일 복사
mkdir apk
cp /path/to/your_app.apk apk/
```

### 4. 설정 파일 수정

`config/capabilities.py`에서 앱 경로 수정:
```python
ANDROID_CAPS = {
    ...
    "app": os.path.join(PROJECT_ROOT, "apk", "your_app.apk"),
    ...
}
```

### 5. 테스트 실행

```bash
# 기본 실행
pytest tests/android/sample/

# Allure 리포트와 함께 실행
pytest tests/android/sample/ --alluredir=allure-results
allure serve allure-results
```

## 프로젝트 구조

```
appium-mobile-test/
├── apk/                    # APK/IPA 파일 (gitignore)
├── config/
│   └── capabilities.py     # Appium 설정
├── docs/                   # 문서
├── pages/                  # Page Object 클래스
├── shell/                  # 실행 스크립트
├── tests/
│   ├── android/           # Android 테스트
│   └── ios/               # iOS 테스트
├── tools/                  # 유틸리티 도구
├── utils/                  # 헬퍼 함수
├── conftest.py            # Pytest fixtures
├── pytest.ini             # Pytest 설정
└── requirements.txt       # Python 의존성
```

## 환경변수 설정

테스트 계정 정보는 환경변수로 설정하세요:

```bash
# PowerShell
$env:TEST_USERNAME = "your_username"
$env:TEST_PIN = "your_pin"
$env:RESOURCE_ID_PREFIX = "com.example.app:id"

# Bash
export TEST_USERNAME="your_username"
export TEST_PIN="your_pin"
export RESOURCE_ID_PREFIX="com.example.app:id"
```

실물 디바이스 연결 시:
```bash
$env:ANDROID_UDID = "device_serial"  # adb devices로 확인
```

## 주요 도구

### UI Dump (`tools/ui_dump.py`)

앱 화면의 UI 요소를 XML로 저장:

```bash
# 현재 화면 캡처
python tools/ui_dump.py

# Watch 모드 (화면 변화 자동 감지)
python tools/ui_dump.py -w
```

### Allure 대시보드

테스트 실행 이력 대시보드:

```bash
# 대시보드 서버 실행
python tools/serve.py
```

## 테스트 작성 가이드

### Page Object 패턴

```python
# pages/login_page.py
from pages.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy

class LoginPage(BasePage):
    USERNAME_FIELD = (AppiumBy.ID, "com.example.app:id/username")
    PASSWORD_FIELD = (AppiumBy.ID, "com.example.app:id/password")
    LOGIN_BUTTON = (AppiumBy.ID, "com.example.app:id/login_btn")

    def login(self, username: str, password: str):
        self.input_text(self.USERNAME_FIELD, username)
        self.input_text(self.PASSWORD_FIELD, password)
        self.click(self.LOGIN_BUTTON)
```

### 테스트 작성

```python
# tests/android/test_login.py
import pytest
import allure

@allure.feature("로그인")
class TestLogin:
    @allure.story("정상 로그인")
    def test_login_success(self, android_driver):
        login_page = LoginPage(android_driver)
        login_page.login("user@test.com", "password123")
        # assertions...
```

## 문제 해결

| 문제 | 해결 방법 |
|------|----------|
| Appium 서버 연결 실패 | `appium` 실행 확인, 포트 4723 확인 |
| 에뮬레이터 연결 실패 | `adb devices`로 연결 상태 확인 |
| 앱 설치 실패 | APK 경로 확인, 서명 상태 확인 |
| 요소 찾기 실패 | `ui_dump.py`로 실제 요소 확인 |

## 라이선스

MIT License

## 기여

Pull Request를 환영합니다.
