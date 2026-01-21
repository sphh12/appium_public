# README_CLONE

이 문서는 **처음 clone 후 바로 실행했을 때 실패했던 이유**와, **새 PC/노트북에서 재현 가능하게 만드는 체크리스트**를 정리합니다.

## Quick Start (원샷)
새 PC/노트북에서 아래 3단계로 끝내는 것을 목표로 합니다.

1) `home` 브랜치로 클론
- `git clone -b home --single-branch git@gitlab.com:sphh12/appium.git`

2) 원샷 세팅(권장: PowerShell)
- `powershell -ExecutionPolicy Bypass -File shell/bootstrap.ps1`

3) 실행
- `./shell/run-app.sh`

## 왜 clone 직후에 안 됐나?
`git clone`은 **소스 코드만** 가져옵니다. 하지만 Appium 테스트는 아래 요소들이 추가로 필요합니다.

- Appium 2 **드라이버(UiAutomator2 등)** 설치
- Allure **CLI** 설치(리포트 생성용)
- Android SDK/ADB 및 **에뮬레이터 연결 상태**
- (선택) 테스트가 기대하는 Android OS 버전과 실제 기기/에뮬레이터 버전 매칭

즉, clone만으로는 실행에 필요한 “환경”이 자동으로 갖춰지지 않아 실패할 수 있습니다.

## 클론(브랜치) 방법
기본 브랜치가 `main`이면 `git clone`만 했을 때 `main`이 체크아웃됩니다.
재현 가능한 실행 환경을 목표로 하면 `home` 브랜치를 권장합니다.

- 권장(원샷 세팅 포함):
  - `git clone -b home --single-branch git@gitlab.com:sphh12/appium.git`

- 테스트 코드만 확인/실행(원본 그대로):
  - `git clone -b test --single-branch git@gitlab.com:sphh12/appium.git`

- HTTPS로 클론해야 하면(회사 정책 등):
  - `git clone -b home --single-branch https://gitlab.com/sphh12/appium.git`

## 클론 후 체크리스트(Windows 기준)
아래 체크리스트는 “원샷 스크립트가 실패했을 때” 수동으로 원인을 찾는 용도입니다.

## 원샷(권장): 부트스트랩 스크립트
새 PC/노트북에서 아래 한 번으로 **venv 생성/의존성 설치/Appium 드라이버 설치/Allure(로컬) 준비**까지 진행합니다.

PowerShell(권장):
- `powershell -ExecutionPolicy Bypass -File shell/bootstrap.ps1`

Android 버전을 고정해서 매칭하고 싶으면(선택):
- `powershell -ExecutionPolicy Bypass -File shell/bootstrap.ps1 -AndroidPlatformVersion 12`

이후 실행:
- `./shell/run-app.sh`

### 1) Appium 서버 확인
PowerShell:

- 실행 중 확인
  - `try { (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:4723/status -TimeoutSec 3).StatusCode } catch { "NOT_RUNNING" }`

- 종료(포트 4723 점유 프로세스 종료)
  - `Stop-Process -Id (Get-NetTCPConnection -LocalPort 4723 -State Listen).OwningProcess -Force`

- 시작
  - `Start-Process appium -ArgumentList "--address","127.0.0.1","--port","4723" -NoNewWindow`

### 2) Appium 2 Android 드라이버(UiAutomator2) 설치
Appium 2는 드라이버가 별도 플러그인처럼 관리됩니다.

- 설치 여부 확인
  - `appium driver list --installed`

- 설치
  - `appium driver install uiautomator2`

### 3) ADB/에뮬레이터 연결 확인
- 디바이스 목록 확인
  - `adb devices -l`

`emulator-5554 device`처럼 **device** 상태여야 합니다.
`offline`이면 잠시 대기하거나 아래처럼 ADB를 재시작합니다.

- `adb kill-server`
- `adb start-server`

### 4) Allure 리포트 생성(Allure CLI)
`./shell/run-app.sh`는 테스트 후 `allure generate`를 호출합니다. 따라서 Allure CLI가 필요합니다.

- 설치 확인
  - `allure --version`

- 설치(권한 정책에 따라 전역 설치가 불가할 수도 있음)
  - 전역 설치: `npm install -g allure-commandline`
  - 전역 설치가 막힌 경우(권장): 프로젝트 폴더에서 `npm install` 후 `npx allure --version`

## 대표 실패 사례와 원인

### A) UiAutomator2 드라이버가 없음
- 증상:
  - `Could not find a driver for automationName 'UiAutomator2' and platformName 'Android'`
- 해결:
  - `appium driver install uiautomator2`

### B) Allure 커맨드가 없음
- 증상:
  - `allure: command not found`
- 해결:
  - `npm install -g allure-commandline`

### C) OS 버전 매칭 문제(예: Android 14를 강제했는데 실제는 12)
- 증상(예):
  - `Unable to find an active device or emulator with OS 14 ... available: emulator-5554 (12)`
- 해결:
  - 특정 OS 버전을 강제하지 않거나, 실제 실행 디바이스/에뮬레이터 버전에 맞춰 설정
  - 이 레포에서는 `ANDROID_PLATFORM_VERSION` 환경변수로 선택적으로 고정 가능

PowerShell 예:
- `setx ANDROID_PLATFORM_VERSION "12"`
- (현재 세션만) `$env:ANDROID_PLATFORM_VERSION="12"`

## 실행 예시
- Android 전체 실행(스크립트)
  - `./shell/run-app.sh`

- 특정 테스트만(스크립트)
  - `./shell/run-app.sh --test test_Login`

---

필요 시 회사 PC 환경(권한 제한/프록시 등)에 맞게 설치 방법을 추가로 정리하면 이 문서를 업데이트합니다.
