# macOS Appium 자동화 환경 세팅 가이드

> 2026-02-14 macOS (Apple Silicon) 기준 작성
> 2026-03-04 실제 세팅 경험 기반 보완 (gh auth, 에뮬레이터 튜닝, Git 멀티 리모트 등)

---

## 1. 세팅 순서 요약

| 순서 | 항목 | 명령어 |
|------|------|--------|
| 1 | GitHub CLI 설치 & 인증 | `brew install gh` → `gh auth login` → `gh auth setup-git` |
| 2 | 리포지토리 클론 | `gh repo clone your-username/appium-portfolio` |
| 3 | Homebrew 설치 | 수동 설치 (sudo 필요) |
| 4 | Node.js 20 설치 | `brew install node@20` |
| 5 | Python 3.10 설치 | `brew install python@3.10` |
| 6 | Java JDK 17 설치 | `brew install openjdk@17` |
| 7 | Allure 설치 | `brew install allure` |
| 8 | 환경변수 설정 | `~/.zshrc` 편집 |
| 9 | npm 패키지 설치 | `npm install` (Appium 드라이버 포함) |
| 10 | Python venv 생성 | `python3.10 -m venv venv` |
| 11 | pip 패키지 설치 | `pip install -r requirements.txt` |
| 12 | Android Studio 설치 | 수동 설치 (GUI) |
| 13 | 에뮬레이터 생성 | Android Studio Device Manager |
| 14 | 에뮬레이터 성능 튜닝 | `config.ini` 수정 (RAM, Heap, GPU) |
| 15 | .env 파일 생성 | `.env.example` 참고 |
| 16 | APK 파일 배치 | `apk/` 폴더에 복사 |
| 17 | 셸 스크립트 권한 | `chmod +x shell/*.sh` |
| 18 | Git 멀티 리모트 설정 | GitHub + GitLab 듀얼 push 구성 |

---

## 2. 상세 설치 절차

### 2.1 GitHub CLI 설치 & 리포지토리 클론

Homebrew가 이미 설치되어 있다면 GitHub CLI를 먼저 설치하고 리포지토리를 클론한다.

```bash
brew install gh
gh auth login
```

`gh auth login` 실행 시 대화형 프롬프트가 나온다:
- **Where do you use GitHub?** → `GitHub.com`
- **Preferred protocol** → `HTTPS`
- **Authenticate** → `Login with a web browser` 선택 후 브라우저에서 인증 완료

> **중요**: `gh auth login`만으로는 일반 `git pull/push` 명령이 인증되지 않는다.
> 반드시 아래 명령을 추가 실행하여 git credential helper를 설정해야 한다.

```bash
gh auth setup-git
```

이후 리포지토리를 클론한다:
```bash
gh repo clone your-username/appium-portfolio
cd appium
```

### 2.2 Homebrew 설치

비대화형 환경(Claude Code 등)에서는 sudo 권한 문제로 자동 설치 불가. **터미널에서 직접 실행** 필요.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

설치 후 셸에 PATH 추가:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 2.3 Node.js 설치

처음에 Node.js 18을 설치했으나 Appium 3.x가 Node.js 20+을 요구하여 **Node.js 20으로 재설치**함.

```bash
brew install node@20
```

> Node.js 18에서 발생한 에러: `ERR_REQUIRE_ESM` - Appium 3.x의 ES Module 호환 문제
>
> 2026-03-04 기준 설치된 버전: v20.20.0

### 2.4 Python 3.10 설치

macOS 기본 Python은 3.9.6으로 프로젝트 요구사항(3.10+) 미충족.

```bash
brew install python@3.10
```

> 2026-03-04 기준 설치된 버전: 3.10.19

### 2.5 Java JDK 17 설치

```bash
brew install openjdk@17
```

> 2026-03-04 기준 설치된 버전: 17.0.18

### 2.6 Allure 설치

```bash
brew install allure
```

> brew 병렬 설치 시 lock 충돌 발생함. **순차 설치 권장**.
>
> 2026-03-04 기준 설치된 버전: 2.37.0

### 2.7 환경변수 설정 (~/.zshrc)

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

### 2.8 프로젝트 의존성 설치

```bash
cd ~/appium
npm install
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **참고**: 이전 가이드에서는 `npx appium driver install uiautomator2`를 별도로 실행하도록 안내했으나,
> 현재 `package.json`에 Appium 드라이버(uiautomator2, xcuitest)가 의존성으로 포함되어 있어
> `npm install`만 실행하면 드라이버도 함께 설치된다. **별도 설치 불필요**.
>
> 2026-03-04 기준 `pip install -r requirements.txt` 실행 시 41개 패키지 설치됨.

### 2.9 Android Studio 설치

다운로드: https://developer.android.com/studio

- **Standard** 설치 선택
- License Agreement: `android-sdk-license`, `android-sdk-arm-dbt-license` 모두 **Accept**

### 2.10 에뮬레이터 생성

Android Studio → **Virtual Device Manager** → **Create Virtual Device**
- 디바이스: Pixel 8 (또는 원하는 기종)
- System Image: API 34 선택

### 2.11 에뮬레이터 성능 튜닝 (필수)

> **이 단계를 건너뛰면 테스트가 불안정해질 수 있다.**
> 2026-03-04 실제 세팅에서 기본 에뮬레이터 설정으로 테스트 실행 시,
> 3번째 테스트에서 **UiAutomator2 프록시 타임아웃(240초 초과)** 에러가 발생했다.
> 아래 성능 튜닝 후 동일 테스트 3건 모두 통과 (총 3분 56초).

에뮬레이터의 `config.ini` 파일을 직접 수정한다:

```bash
# 에뮬레이터 이름에 맞게 경로 변경 (예: Pixel_8)
vi ~/.android/avd/Pixel_8.avd/config.ini
```

아래 항목을 찾아 수정:

| 항목 | 기본값 | 권장값 | 설명 |
|------|--------|--------|------|
| `hw.ramSize` | 4096 | **8192** | 에뮬레이터 RAM (MB) |
| `vm.heapSize` | 228 | **512** | VM 힙 크기 (MB) |
| `hw.gpu.mode` | auto | **host** | GPU 렌더링 모드 (호스트 GPU 직접 사용) |

```ini
# 변경 전
hw.ramSize=4096
vm.heapSize=228
hw.gpu.mode=auto

# 변경 후
hw.ramSize=8192
vm.heapSize=512
hw.gpu.mode=host
```

> **왜 필요한가?**
> - `hw.ramSize=4096`: 기본 4GB는 앱 설치 + UiAutomator2 서버 실행 + 테스트 동시 진행 시 메모리 부족 발생
> - `vm.heapSize=228`: 기본 힙 크기가 작아 앱 렌더링 시 GC가 빈번하게 발생하여 응답 지연
> - `hw.gpu.mode=auto`: 자동 감지가 최적이 아닐 수 있음. `host`로 설정하면 Mac의 GPU를 직접 사용하여 렌더링 성능 향상
>
> **변경 후 에뮬레이터를 반드시 재시작**해야 적용된다 (Cold Boot 권장).

### 2.12 .env 파일 생성

```bash
cp .env.example .env
```

필수 항목 입력:
- `STG_ID` / `STG_PW` - Staging 테스트 계정
- `APP_RESOURCE_ID_PREFIX` - 앱 패키지 resource-id 접두사
  - 코드에 기본값이 있으므로 (`com.example.remittance.stag:id`) Staging 사용 시 생략 가능

APK 파일 배치:
- `apk/stage/` 폴더에 Staging APK 배치 (파일명 자동 인식)
- `apk/live/` 폴더에 Live APK 배치
- `apk/livetest/` 폴더에 LiveTest APK 배치

선택 항목:
- `BLOB_READ_WRITE_TOKEN` - Vercel Blob 읽기/쓰기 토큰 (대시보드 첨부파일 업로드용)
  - 미설정 시 테스트 통계만 대시보드에 업로드, 첨부파일(스크린샷/비디오/logcat)은 로컬에만 저장
  - 토큰 발급: Vercel > allure-dashboard 프로젝트 > Storage > Blob Store > Settings에서 발급
  - 이전에 발급받은 토큰이 있다면 기존 `.env` 파일에서 복사 (`vercel_blob_rw_` 로 시작)

### 2.13 셸 스크립트 실행 권한

macOS에서는 셸 스크립트에 실행 권한을 부여해야 함:
```bash
chmod +x ./shell/*.sh
```

### 2.14 Git 멀티 리모트 설정 (GitHub + GitLab 듀얼 Push)

프로젝트를 GitHub과 GitLab 양쪽에 push하는 구조로 사용하는 경우, 리모트를 다음과 같이 설정한다.

**1단계: 기존 origin 리모트를 github으로 이름 변경**

```bash
git remote rename origin github
```

**2단계: GitLab 리모트 추가**

```bash
# PAT(Personal Access Token) 방식
git remote add gitlab https://oauth2:<YOUR_GITLAB_PAT>@gitlab.com/your-username/appium-portfolio.git
```

> GitLab PAT 발급: GitLab → Settings → Access Tokens → `write_repository` 권한으로 생성

**3단계: Git 사용자 정보 설정**

```bash
git config user.name "이름"
git config user.email "이메일@example.com"
```

**4단계: 확인**

```bash
git remote -v
# github  https://github.com/your-username/appium-portfolio.git (fetch)
# github  https://github.com/your-username/appium-portfolio.git (push)
# gitlab  https://oauth2:***@gitlab.com/your-username/appium-portfolio.git (fetch)
# gitlab  https://oauth2:***@gitlab.com/your-username/appium-portfolio.git (push)
```

**Push 방법:**

```bash
# 양쪽 모두 push
git push github main
git push gitlab main
```

> 커밋 후 항상 GitHub과 GitLab 양쪽 모두 push하는 것이 규칙이다.

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

### 4.7 APK 파일 미발견

- **에러**: `No .apk file found in apk/stage/`
- **원인**: 환경별 APK 폴더에 .apk 파일이 없음
- **해결**: `apk/stage/`, `apk/live/`, `apk/livetest/` 폴더에 APK 파일 배치 (파일명 자동 인식)

### 4.8 UiAutomator2 "Not Installed" 오탐

- **에러**: 스크립트에서 `Appium driver (UiAutomator2): Not Installed`로 표시
- **원인**: 체크 스크립트의 드라이버 감지 로직이 이미 설치된 드라이버를 인식하지 못함
- **해결**: 실제로는 설치됨. `--skip-check` 옵션으로 우회 가능, 또는 `run-stg.sh`로 실행

### 4.9 .env 파일 누락 (로그인 실패)

- **에러**: `ValueError: username과 pin이 필요합니다. 환경변수 STG_ID/STG_PW를 설정하세요`
- **원인**: `.env` 파일이 없거나 테스트 계정 정보 미입력
- **해결**: `.env.example`을 복사하여 `.env` 생성 후 계정 정보 입력

### 4.10 UiAutomator2 프록시 타임아웃 (에뮬레이터 성능 문제)

- **에러**: `UiAutomator2 proxy timeout exceeded (240s)` - 3번째 테스트부터 발생
- **원인**: 에뮬레이터 기본 설정(RAM 4GB, Heap 228MB, GPU auto)이 Appium 테스트에 불충분. 테스트가 누적되면서 에뮬레이터가 느려지고 UiAutomator2 서버 응답이 타임아웃됨
- **해결**: `~/.android/avd/<에뮬레이터>.avd/config.ini`에서 `hw.ramSize=8192`, `vm.heapSize=512`, `hw.gpu.mode=host`로 변경 후 Cold Boot (상세: 섹션 2.11 참고)

### 4.11 gh auth login 후 git pull/push 실패

- **에러**: `git pull` 또는 `git push` 시 인증 에러 발생 (credential 관련)
- **원인**: `gh auth login`은 GitHub CLI 자체의 인증만 설정하며, 일반 git 명령의 credential helper는 별도 설정 필요
- **해결**: `gh auth setup-git` 실행하여 git credential helper에 GitHub CLI 인증을 연동

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
