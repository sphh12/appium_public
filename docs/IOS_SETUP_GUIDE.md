# iOS 자동화 환경 세팅 가이드

> 2026-02-14 macOS (Apple Silicon) 기준 작성
> 전제조건: [MAC_SETUP_GUIDE.md](MAC_SETUP_GUIDE.md)의 Android 세팅이 완료된 상태

---

## 1. 전체 구조 이해

```
Python 테스트 코드 (pytest)
    ↓ HTTP 요청
Appium Server (localhost:4723)
    ↓
XCUITest Driver (iOS 전용 드라이버)
    ↓
iOS Simulator 또는 실제 iPhone
```

- **Appium**: 테스트 명령을 전달하는 서버
- **XCUITest Driver**: Appium 명령을 iOS가 이해하는 언어로 변환하는 통역사
- **Xcode + Simulator**: 앱이 실행되는 가상 iPhone 환경

---

## 2. 세팅 순서 요약

| 순서 | 항목 | 소요 시간 | 비고 |
|------|------|----------|------|
| 1 | Xcode 설치 | 30분~1시간 | App Store에서 설치 (~15GB) |
| 2 | iOS 시뮬레이터 다운로드 | 10~20분 | Xcode 내 Platform 설정 (~8GB) |
| 3 | Xcode 라이선스 동의 + 경로 설정 | 1분 | 터미널 명령어 |
| 4 | XCUITest 드라이버 설치 | 1분 | `appium driver install xcuitest` |
| 5 | Appium 서버 재시작 | 1분 | 드라이버 인식을 위해 필수 |
| 6 | 환경 검증 | 1분 | `appium-doctor --ios` |
| 7 | 시뮬레이터 테스트 실행 | 1분 | 동작 확인 |

> Homebrew, Node.js, Appium, Python은 Android 세팅에서 이미 설치됨. 중복 설치 불필요.

---

## 3. 상세 설치 절차

### 3.1 Xcode 설치

App Store에서 "Xcode" 검색 후 설치.

- 용량: 약 12~15GB
- 설치 시 컴포넌트 선택 화면이 나오면 **iOS** 체크 필수
- macOS는 기본 선택됨 (Built-in)
- watchOS, tvOS, visionOS는 불필요 (체크 해제)

### 3.2 iOS 시뮬레이터 다운로드

설치 시 iOS를 선택하지 못했다면 나중에 추가 가능:

**방법 1) Xcode GUI:**
```
Xcode → Settings (⌘ + ,) → Platforms → 좌측 하단 "+" → iOS 선택 → 다운로드
```

**방법 2) 터미널:**
```bash
xcodebuild -downloadPlatform iOS
```

### 3.3 Xcode 라이선스 동의 + 경로 설정

```bash
# Xcode 개발자 도구 경로 지정
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

# 라이선스 동의
sudo xcodebuild -license accept
```

확인:
```bash
xcodebuild -version
# 예상 출력: Xcode 26.2 / Build version 17C52
```

### 3.4 XCUITest 드라이버 설치

```bash
appium driver install xcuitest
```

확인:
```bash
appium driver list --installed
# xcuitest@10.x.x [installed (npm)] 이 보여야 함
```

### 3.5 Appium 서버 재시작

> 드라이버 설치 전에 Appium 서버가 실행 중이었다면, **반드시 재시작**해야 새 드라이버를 인식합니다.

```bash
# 기존 서버 종료
lsof -ti:4723 | xargs kill -9

# 재시작
appium --relaxed-security
```

서버 로그에서 아래 내용이 보여야 정상:
```
XCUITestDriver has been successfully loaded
Available drivers:
  - uiautomator2@x.x.x (automationName 'UiAutomator2')
  - xcuitest@x.x.x (automationName 'XCUITest')
```

### 3.6 환경 검증

```bash
npm install -g @appium/doctor
appium-doctor --ios
```

**필수 항목** (모두 ✔ 이어야 함):
- Xcode is installed
- Xcode Command Line Tools are installed
- Node.js is installed
- DevToolsSecurity is enabled

**선택 항목** (✖ 이어도 기본 테스트에 지장 없음):

| 항목 | 용도 | 필요 시점 |
|------|------|----------|
| ffmpeg | 화면 녹화 | 테스트 영상 녹화 |
| ios-deploy | 실물 iPhone에 앱 설치 | 실기기 테스트 |
| idb | Facebook 디버깅 도구 | 고급 디바이스 제어 |
| applesimutils | 시뮬레이터 권한 설정 | 위치/알림 권한 자동 제어 |

필요 시 설치:
```bash
brew install ffmpeg
brew install ios-deploy
brew install libimobiledevice ideviceinstaller
```

---

## 4. 시뮬레이터 관리 명령어

```bash
# 사용 가능한 시뮬레이터 목록
xcrun simctl list devices available

# 시뮬레이터 부팅
xcrun simctl boot "iPhone 17"

# 시뮬레이터 UI 열기
open -a Simulator

# 시뮬레이터 종료
xcrun simctl shutdown "iPhone 17"

# 전체 시뮬레이터 종료
xcrun simctl shutdown all
```

---

## 5. Safari 테스트 시 추가 설정

Safari 브라우저 테스트 시 Web Inspector 활성화 필요:

```bash
# 시뮬레이터가 부팅된 상태에서 실행
xcrun simctl spawn "iPhone 17" defaults write com.apple.mobilesafari WebKitDeveloperExtras -bool true
xcrun simctl spawn "iPhone 17" defaults write com.apple.mobilesafari WebInspectorEnabled -bool true
```

Safari 테스트용 capabilities에 아래 옵션 추가 권장:
```python
caps = {
    "browserName": "Safari",
    "webviewConnectTimeout": 30000,       # Safari 연결 대기 (기본 5초 → 30초)
    "safariInitialUrl": "https://www.google.com",  # 초기 URL 설정
}
```

---

## 6. 테스트 실행

```bash
# Appium 서버 시작 (터미널 1)
appium --relaxed-security

# 테스트 실행 (터미널 2)
source venv/bin/activate
pytest tests/ios/test_ios_first.py -v -s
```

---

## 7. 프로젝트 내 iOS 관련 파일 구조

```
appium/
├── config/
│   └── capabilities.py          ← IOS_CAPS 설정 (이미 존재)
├── conftest.py                  ← ios_driver 픽스처 (이미 존재)
├── tests/
│   ├── android/                 ← Android 테스트
│   └── ios/                     ← iOS 테스트
│       ├── test_ios_first.py    ← 시뮬레이터 동작 확인 테스트
│       └── sample/              ← 샘플 테스트
└── docs/
    └── IOS_SETUP_GUIDE.md       ← 이 문서
```

---

## 8. 발생했던 에러 및 해결

### 8.1 XCUITest 드라이버를 찾을 수 없음

- **에러**: `Could not find a driver for automationName 'XCUITest' and platformName 'iOS'`
- **원인**: xcuitest 드라이버 설치 전에 Appium 서버가 실행되어 드라이버를 인식하지 못함
- **해결**: Appium 서버 종료 후 재시작 (`lsof -ti:4723 | xargs kill -9` → `appium --relaxed-security`)

### 8.2 Safari Web Inspector 연결 타임아웃

- **에러**: `The remote debugger did not return any connected web applications after 5068ms`
- **원인**: 시뮬레이터의 Safari Web Inspector가 비활성화 상태 + 기본 타임아웃(5초)이 너무 짧음
- **해결**:
  1. Web Inspector 활성화: `xcrun simctl spawn "iPhone 17" defaults write com.apple.mobilesafari WebKitDeveloperExtras -bool true`
  2. capabilities에 `"webviewConnectTimeout": 30000` 추가

### 8.3 Appium/Node.js가 PATH에 없음

- **에러**: `appium: command not found`, `node: command not found`
- **원인**: `~/.zprofile`(또는 `~/.zshrc`)의 Homebrew PATH 설정이 현재 터미널 세션에 미적용
- **해결**: `eval "$(/opt/homebrew/bin/brew shellenv)"` 실행 또는 터미널 재시작

---

## 9. Android vs iOS 차이점 (Appium 기준)

| 항목 | Android | iOS |
|------|---------|-----|
| 자동화 엔진 | UiAutomator2 | XCUITest |
| 필수 IDE | Android Studio | Xcode |
| 테스트 디바이스 | 에뮬레이터 / 실물 디바이스 | 시뮬레이터 / 실물 디바이스 |
| 앱 파일 형식 | `.apk` | `.app` (시뮬레이터) / `.ipa` (실기기) |
| 요소 탐색 도구 | uiautomatorviewer / Appium Inspector | Appium Inspector |
| 드라이버 픽스처 | `android_driver` | `ios_driver` |
| 실행 OS 제한 | Windows / macOS / Linux | **macOS 전용** |
| 디바이스 ID 확인 | `adb devices` | `xcrun simctl list devices` |
