# macOS Appium 자동화 환경 세팅 가이드

> 2026-02-14 macOS (Apple Silicon) 기준 작성

---

## 1. 세팅 순서 요약

| 순서 | 항목 | 명령어 |
|------|------|--------|
| 1 | Homebrew 설치 | 수동 설치 (sudo 필요) |
| 2 | Node.js 20 설치 | `brew install node@20` |
| 3 | Python 3.10 설치 | `brew install python@3.10` |
| 4 | Java JDK 17 설치 | `brew install openjdk@17` |
| 5 | Allure 설치 | `brew install allure` |
| 6 | 환경변수 설정 | `~/.zshrc` 편집 |
| 7 | npm 패키지 설치 | `npm install` |
| 8 | Appium 드라이버 설치 | `npx appium driver install uiautomator2` |
| 9 | Python venv 생성 | `python3.10 -m venv venv` |
| 10 | pip 패키지 설치 | `pip install -r requirements.txt` |
| 11 | Android Studio 설치 | 수동 설치 (GUI) |
| 12 | 에뮬레이터 생성 | Android Studio Device Manager |
| 13 | .env 파일 생성 | `.env.example` 참고 |
| 14 | APK 파일 배치 | `apk/` 폴더에 복사 |

---

## 2. 상세 설치 절차

### 2.1 Homebrew 설치

비대화형 환경(Claude Code 등)에서는 sudo 권한 문제로 자동 설치 불가. **터미널에서 직접 실행** 필요.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

설치 후 셸에 PATH 추가:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 2.2 Node.js 설치

처음에 Node.js 18을 설치했으나 Appium 3.x가 Node.js 20+을 요구하여 **Node.js 20으로 재설치**함.

```bash
brew install node@20
```

> Node.js 18에서 발생한 에러: `ERR_REQUIRE_ESM` - Appium 3.x의 ES Module 호환 문제

### 2.3 Python 3.10 설치

macOS 기본 Python은 3.9.6으로 프로젝트 요구사항(3.10+) 미충족.

```bash
brew install python@3.10
```

### 2.4 Java JDK 17 설치

```bash
brew install openjdk@17
```

### 2.5 Allure 설치

```bash
brew install allure
```

> brew 병렬 설치 시 lock 충돌 발생함. **순차 설치 권장**.

### 2.6 환경변수 설정 (~/.zshrc)

```bash
# Homebrew
eval "$(/opt/homebrew/bin/brew shellenv)"

# Node.js 20
export PATH="/opt/homebrew/opt/node@20/bin:$PATH"

# Python 3.10
export PATH="/opt/homebrew/opt/python@3.10/libexec/bin:$PATH"

# Java JDK 17
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

# Android SDK
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
```

설정 후 반드시 적용:
```bash
source ~/.zshrc
```

### 2.7 프로젝트 의존성 설치

```bash
cd ~/appium
npm install
npx appium driver install uiautomator2
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.8 Android Studio 설치

다운로드: https://developer.android.com/studio

- **Standard** 설치 선택
- License Agreement: `android-sdk-license`, `android-sdk-arm-dbt-license` 모두 **Accept**

### 2.9 에뮬레이터 생성

Android Studio → **Virtual Device Manager** → **Create Virtual Device**
- 디바이스: Pixel 9 (또는 원하는 기종)
- System Image: API 34+ 선택

### 2.10 .env 파일 생성

```bash
cp .env.example .env
```

필수 항목 입력:
- `STG_ID` / `STG_PW` - Staging 테스트 계정
- `STG_APK` - APK 파일명 (apk/ 폴더 내 실제 파일명과 일치해야 함)
- `GME_RESOURCE_ID_PREFIX` - 앱 패키지 resource-id 접두사

### 2.11 셸 스크립트 실행 권한

macOS에서는 셸 스크립트에 실행 권한을 부여해야 함:
```bash
chmod +x ./shell/*.sh
```

---

## 3. 테스트 실행

```bash
source ~/.zshrc
source venv/bin/activate
./shell/run-stg.sh --basic_01_test.py
```

---

## 4. 발생했던 에러 및 해결

### 4.1 Homebrew 설치 실패

- **에러**: `Need sudo access on macOS`
- **원인**: 비대화형 환경에서 sudo 사용 불가
- **해결**: 터미널에서 직접 설치

### 4.2 brew 병렬 설치 lock 충돌

- **에러**: `A brew install process has already locked /opt/homebrew/Cellar/pkgconf`
- **원인**: 여러 brew install을 동시에 실행하면 공유 의존성에서 lock 충돌 발생
- **해결**: 순차적으로 하나씩 설치

### 4.3 Node.js 18 + Appium 3.x 비호환

- **에러**: `ERR_REQUIRE_ESM: require() of ES Module not supported`
- **원인**: Appium 3.x가 Node.js 20+ 필요 (package.json: `^20.19.0 || ^22.12.0 || >=24.0.0`)
- **해결**: `brew install node@20`으로 업그레이드, `.zshrc` PATH도 node@20으로 변경

### 4.4 셸 스크립트 Permission denied

- **에러**: `bash: ./shell/run-stg.sh: Permission denied`
- **원인**: macOS에서 git clone 시 실행 권한이 보존되지 않음
- **해결**: `chmod +x ./shell/*.sh`

### 4.5 .zshrc 줄바꿈 문제 (^M)

- **에러**: `command not found: ^M`, ANDROID_HOME 경로 끝에 `\r` 포함
- **원인**: .zshrc 파일이 Windows 줄바꿈(CRLF)으로 저장됨
- **해결**: `sed -i '' 's/\r$//' ~/.zshrc`

### 4.6 ANDROID_HOME 미설정 (ADB not found)

- **에러**: `ADB not found`, `The Android SDK root folder does not exist`
- **원인**: 환경변수가 현재 터미널 세션에 로드되지 않음 / .zshrc의 \r 문제
- **해결**: `source ~/.zshrc` 실행 또는 터미널 재시작

### 4.7 APK 파일명 불일치

- **에러**: `The application at '/Users/sph/appium/apk/GME_7.14.1_stg.apk' does not exist`
- **원인**: `.env`의 `STG_APK` 값과 실제 `apk/` 폴더 내 파일명이 다름
- **해결**: `.env`의 `STG_APK`를 실제 파일명(`[Stg]GME_7.13.0.apk`)으로 수정

### 4.8 UiAutomator2 "Not Installed" 오탐

- **에러**: 스크립트에서 `Appium driver (UiAutomator2): Not Installed`로 표시
- **원인**: 체크 스크립트의 드라이버 감지 로직이 이미 설치된 드라이버를 인식하지 못함
- **해결**: 실제로는 설치됨. `--skip-check` 옵션으로 우회 가능, 또는 `run-stg.sh`로 실행

### 4.9 .env 파일 누락 (로그인 실패)

- **에러**: `ValueError: username과 pin이 필요합니다. 환경변수 STG_ID/STG_PW를 설정하세요`
- **원인**: `.env` 파일이 없거나 테스트 계정 정보 미입력
- **해결**: `.env.example`을 복사하여 `.env` 생성 후 계정 정보 입력

---

## 5. macOS vs Windows 차이점

| 항목 | Windows | macOS |
|------|---------|-------|
| 터미널 | Git Bash 권장 | 기본 Terminal (zsh) |
| 패키지 매니저 | choco / scoop | Homebrew |
| 환경변수 설정 | 시스템 환경변수 | `~/.zshrc` |
| Python venv 활성화 | `.\venv\Scripts\activate` | `source venv/bin/activate` |
| 셸 스크립트 권한 | 불필요 | `chmod +x` 필요 |
| SDK 기본 경로 | `%LOCALAPPDATA%\Android\Sdk` | `~/Library/Android/sdk` |
| JAVA_HOME 경로 | `C:\Program Files\Eclipse Adoptium\jdk-17` | `/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home` |

---

## 6. 관련 문서

- [클론 가이드](README_CLONE.md)
- [Allure 리포트 가이드](ALLURE_REPORT_GUIDE.md)
- [코딩 가이드라인](CODING_GUIDELINES.md)
- [UI Dump 가이드](UI_DUMP_GUIDE.md)
- [iOS 세팅 가이드](IOS_SETUP_GUIDE.md) *(작성 예정)*
