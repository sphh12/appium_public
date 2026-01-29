# Clone & 초기 환경 구성 가이드 (Windows 기준)

이 문서는 **소스코드 clone 이후, 로컬에서 Appium 테스트를 돌릴 수 있는 최소 환경을 구성**하는 방법만 정리합니다.

---

## 1) Clone

저장소를 클론합니다.

- SSH (권장)
  - `git clone git@github.com:<username>/appium_public.git`

- HTTPS
  - `git clone https://github.com/<username>/appium_public.git`

---

## 2) 원샷 세팅(권장): 부트스트랩 스크립트

새 PC/노트북에서는 아래 1회 실행으로 **venv 생성/의존성 설치/Appium 드라이버 설치/Allure(로컬) 준비**까지 진행하는 것을 권장합니다.

- PowerShell
  - `powershell -ExecutionPolicy Bypass -File shell/bootstrap.ps1`

Android 버전을 고정해서 맞추고 싶으면(선택):

- `powershell -ExecutionPolicy Bypass -File shell/bootstrap.ps1 -AndroidPlatformVersion 12`

---

## 3) 필수 구성 요소 체크(수동 점검용)

부트스트랩이 실패했거나, 회사 PC 권한/프록시 등으로 자동 설치가 막히는 경우 아래 항목을 순서대로 점검합니다.

### 3.1 Python 가상환경 + 패키지

- venv 활성화(예)
  - `./venv/Scripts/activate`

- Python 패키지 설치
  - `pip install -r requirements.txt`

### 3.2 Node.js / Appium 2

- Appium 설치/버전 확인
  - `appium --version`

- Appium 2 Android 드라이버(UiAutomator2) 설치
  - 설치 여부 확인: `appium driver list --installed`
  - 설치: `appium driver install uiautomator2`

### 3.3 Android SDK / ADB / 에뮬레이터

- ADB 디바이스 확인
  - `adb devices -l`

`device` 상태가 최소 1개는 떠야 합니다. `offline`이면 아래처럼 재시작합니다.

- `adb kill-server`
- `adb start-server`

### 3.4 Appium 서버(로컬)

- 실행 중 확인
  - `try { (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:4723/status -TimeoutSec 3).StatusCode } catch { "NOT_RUNNING" }`

### 3.5 Allure CLI (리포트 생성용)

Allure 리포트를 생성/열람하려면 Allure CLI가 필요합니다.

- 설치 확인
  - `allure --version`

- 설치(환경에 따라 선택)
  - Scoop: `scoop install allure`
  - Chocolatey: `choco install allure`
  - 전역 설치가 막힌 경우: `npm install` 후 `npx allure --version`

---

## 4) (선택) 환경 세팅

### Android OS 버전 고정

실제 에뮬레이터/디바이스 OS 버전과 테스트 설정을 맞춰야 하는 경우에만 사용합니다.

- PowerShell (영구)
  - `setx ANDROID_PLATFORM_VERSION "12"`

- PowerShell (현재 세션)
  - `$env:ANDROID_PLATFORM_VERSION="12"`

---

## 5) 자주 겪는 초기 셋업 이슈

### A) UiAutomator2 드라이버가 없음

- 증상
  - `Could not find a driver for automationName 'UiAutomator2' ...`

- 해결
  - `appium driver install uiautomator2`

### B) Allure 커맨드가 없음

- 증상
  - `allure: command not found`

- 해결
  - `scoop install allure` 또는 `choco install allure`

---

필요 시 회사 PC 환경(권한 제한/프록시 등)에 맞게 설치 방법을 추가로 정리해서 이 문서를 업데이트합니다.
