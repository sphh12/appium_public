# Appium Mobile Test

GME Remittance 앱 자동화 테스트 프로젝트

## 요구 사항

- Node.js 18+
- Python 3.10+
- Java JDK 17+
- Android Studio (에뮬레이터 및 SDK)
- Git (Git Bash 포함)
- Appium Inspector (선택사항)

---

## 새 환경에서 설정하기 (처음 사용자용)

처음 클론/초기 세팅만 빠르게 보고 싶으면 아래 문서를 참고하세요.

- [docs/README_CLONE.md](docs/README_CLONE.md)

다른 PC에서 이 프로젝트를 처음 설정할 때 아래 단계를 순서대로 진행하세요.

### STEP 1: 필수 프로그램 설치

#### 1.1 Node.js 설치
- 다운로드: https://nodejs.org/ (LTS 버전 권장)
- 설치 후 확인:
  ```bash
  node --version   # v18.x.x 이상
  npm --version    # 9.x.x 이상
  ```

#### 1.2 Java JDK 설치
- 다운로드: https://adoptium.net/ (Temurin JDK 17)
- 설치 경로 예시: `C:\Program Files\Eclipse Adoptium\jdk-17`

#### 1.3 Python 설치
- 다운로드: https://www.python.org/downloads/ (3.10 이상)
- 설치 시 **"Add Python to PATH"** 체크 필수!
- 설치 후 확인:
  ```bash
  python --version   # Python 3.10.x 이상
  pip --version
  ```

#### 1.4 Android Studio 설치
- 다운로드: https://developer.android.com/studio
- 설치 시 포함 항목:
  - Android SDK
  - Android SDK Platform-Tools
  - Android Emulator
- 설치 후 SDK Manager에서 추가 설치:
  - Android 14 (API 34) 또는 원하는 버전
  - Intel x86 Emulator Accelerator (HAXM) - Intel CPU인 경우

#### 1.5 Git 설치
- 다운로드: https://git-scm.com/
- 설치 시 Git Bash 포함 (shell 스크립트 실행에 필요)

### STEP 2: 환경 변수 설정

Windows 시스템 환경 변수에 다음을 추가합니다:

| 변수명 | 값 (예시) |
|--------|-----------|
| `JAVA_HOME` | `C:\Program Files\Eclipse Adoptium\jdk-17` |
| `ANDROID_HOME` | `C:\Users\{사용자명}\AppData\Local\Android\Sdk` |

**PATH에 추가:**
```
%JAVA_HOME%\bin
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\emulator
%ANDROID_HOME%\tools
%ANDROID_HOME%\tools\bin
```

**환경 변수 설정 방법:**
1. Windows 검색 → "환경 변수" → "시스템 환경 변수 편집"
2. "환경 변수" 버튼 클릭
3. 시스템 변수에서 "새로 만들기"로 `JAVA_HOME`, `ANDROID_HOME` 추가
4. Path 변수 편집 → 위 경로들 추가

**설정 확인:**
```bash
echo %JAVA_HOME%
echo %ANDROID_HOME%
java -version
adb --version
emulator -version
```

### STEP 3: Android 에뮬레이터 생성

1. Android Studio 실행
2. `Tools` → `Device Manager`
3. `Create Device` 클릭
4. 기기 선택 (예: Pixel 6)
5. 시스템 이미지 선택 (예: API 34, x86_64)
6. 에뮬레이터 이름 설정 (예: `Pixel_6`)
7. `Finish`

### STEP 4: 프로젝트 클론 및 설정

```bash
# 1. 저장소 클론
git clone https://gitlab.com/sphh12/appium.git
cd appium

# 2. Node.js 패키지 설치
npm install

# 3. Appium 드라이버 설치
npx appium driver install uiautomator2
npx appium driver install xcuitest  # Mac only

# 4. Python 가상환경 생성
python -m venv venv

# 5. 가상환경 활성화 (Windows)
.\venv\Scripts\activate
# 또는 Git Bash에서:
source venv/Scripts/activate

# 6. Python 패키지 설치
pip install -r requirements.txt
```

### STEP 5: 설치 확인

```bash
# Appium 버전 확인
npx appium --version

# 설치된 드라이버 확인
npx appium driver list --installed

# Python 패키지 확인
pip list | grep -i appium
```

---

## 유의 사항

### 경로 관련
- **프로젝트 코드는 상대 경로를 사용**하므로 어떤 폴더에 클론해도 동작합니다.
- 단, 아래 파일들은 사용자별로 다르게 설정해야 합니다:
  - `.appiumsession` 파일: Appium Inspector에서 직접 생성 (git에서 제외됨)

### Windows 사용자
- **Git Bash 사용 권장**: `run-app.sh` 스크립트는 Bash 스크립트이므로 PowerShell에서 직접 실행 불가
- Git Bash 실행 방법: 프로젝트 폴더에서 우클릭 → "Git Bash Here"

### APK 파일
- APK 파일은 Git LFS로 관리됩니다.
- 클론 후 APK가 제대로 받아지지 않으면:
  ```bash
  git lfs install
  git lfs pull
  ```

### 에뮬레이터 이름
- `run-app.sh` 스크립트는 기본적으로 `Pixel_6` 이름의 에뮬레이터를 찾습니다.
- 다른 이름을 사용하려면 Android Studio Device Manager에서 에뮬레이터 이름 확인 후 사용

---

## 테스트 실행

### 방법 1: Shell 스크립트 (Git Bash) - 권장
```bash
# 권장: 루트 래퍼 스크립트(= shell/run-app.sh 호출)
# 단일 파일 실행(단축 옵션): tests/<platform>/<file>.py 를 자동 실행
./run-app.sh --xml_test
./run-app.sh --gme1_test

# 단일 테스트만 실행 (-k 필터)
./run-app.sh --gme1_test --test test_Login

# 여러 파일을 지정한 순서대로 실행
./run-app.sh --files "tests/android/gme1_test.py tests/android/xml_test.py"

# 폴더(플랫폼 전체) 실행: tests/<platform> 폴더 전체
./run-app.sh --all

# 모든 테스트 실행 + Allure 리포트
./run-app.sh --all --report

# 도움말
./run-app.sh --help
```

참고:
- 기본 플랫폼은 android 입니다. iOS는 `--platform ios` 옵션을 사용하세요.
- 예전 단축 옵션 `--test_xml` / `--test_xml.py` 도 `xml_test.py`로 자동 매핑됩니다.

스크립트가 자동으로 처리하는 것:
- Appium 서버 실행 여부 확인 (없으면 자동 시작)
- 에뮬레이터 연결 여부 확인 (없으면 자동 시작)
- Python 가상환경 활성화
- 테스트 실행

### 방법 2: 수동 실행 (PowerShell/CMD)
```bash
# 터미널 1: Appium 서버 시작
npm run appium:start

# 터미널 2: 에뮬레이터 시작 (Android Studio에서 또는)
emulator -avd Pixel_6

# 터미널 3: 테스트 실행
.\venv\Scripts\activate
pytest tests/android/gme1_test.py -v --platform=android

# xml 기반 시나리오 테스트만 실행
pytest tests/android/xml_test.py -v --platform=android
```

### 방법 3: npm 스크립트
```bash
npm run test:android
npm run test:ios  # Mac only
```

---

## Allure 리포트

Allure 화면 구성/탭 의미/분석 루틴(상세)은 아래 문서를 참고하세요.

- [docs/ALLURE_REPORT_GUIDE.md](docs/ALLURE_REPORT_GUIDE.md)

### Allure CLI 설치 (최초 1회)
```bash
# Windows (Scoop 사용)
scoop install allure

# 또는 Chocolatey 사용
choco install allure
```

### 리포트 생성 및 확인
```bash
# 테스트 실행 (결과 생성)
pytest tests/android -v --alluredir=allure-results

# 리포트 서버 실행 (브라우저에서 확인)
allure serve allure-results

# HTML 리포트 생성
allure generate allure-results -o allure-report --clean
allure open allure-report
```

### UI 확인 방법(아주 간단 버전)

- **Overview**: 이번 실행의 전체 건강상태(FAILED/BROKEN/SKIPPED 비율)
- **Suites**: 실패한 테스트를 클릭해서 상세 진입(가장 자주 씀)
- **Attachments**: 스크린샷/비디오/log/page source로 원인 단서 확인

### (권장) 실행 이력 저장 + 대시보드

이 프로젝트는 실행 이력을 `allure-reports/YYYYMMDD_HHMMSS/` 형태로 보관하며,
전체 실행 목록을 한 화면에서 볼 수 있는 대시보드를 함께 제공합니다.

1) **타임스탬프 기반 실행 + 리포트 생성**
```bash
# 기본(권장): hybrid = FAIL/SKIP/BROKEN만 첨부
python tools/run_allure.py -- tests/android/gme1_test.py -v --platform=android --record-video

# 필요 시: all = 성공(PASS)까지 포함해 전부 첨부
python tools/run_allure.py -- tests/android/gme1_test.py -v --platform=android --record-video --allure-attach=all
```

2) **최신 리포트 바로 열기**
- `allure-reports/LATEST/index.html` (최신 실행으로 리다이렉트)

3) **전체 이력 대시보드 열기**
- `allure-reports/dashboard/index.html`

대시보드는 브라우저에서 `runs.json`을 읽기 때문에, 아래처럼 간단 서버로 여는 것을 권장합니다.
```bash
python -m http.server 8000
```
그 후 브라우저에서 아래로 접속:
- `http://127.0.0.1:8000/allure-reports/dashboard/`

---

## 프로젝트 구조

```
appium/
├── config/
│   └── capabilities.py     # 디바이스 설정 (상대 경로 사용)
├── pages/
│   ├── base_page.py        # 공통 기능
│   └── sample_page.py      # 페이지 객체
├── tests/
│   ├── android/            # Android 테스트
│   │   └── gme1_test.py    # 메인 테스트 파일
│   └── ios/                # iOS 테스트
├── shell/
│   └── run-app.sh          # 테스트 실행 스크립트
├── apk/                    # APK 파일 (Git LFS)
├── pdf/                    # 가이드 문서
├── conftest.py             # pytest 설정
├── requirements.txt        # Python 패키지
└── package.json            # Node.js 패키지
```

---

## Appium Inspector 설정

Appium Inspector는 앱 요소(버튼, 입력필드 등)를 탐색하는 도구입니다.

### 다운로드
https://github.com/appium/appium-inspector/releases

### 설정 방법

1. **Appium Inspector 실행**

2. **Remote 서버 설정** (상단 탭에서 선택)
   | 항목 | 값 |
   |------|-----|
   | Remote Host | `127.0.0.1` |
   | Remote Port | `4723` |
   | Remote Path | `/` (비워두거나 슬래시) |

3. **Desired Capabilities 입력** (JSON Representation 탭)
   ```json
   {
     "platformName": "Android",
     "appium:automationName": "UiAutomator2",
     "appium:deviceName": "Android Emulator",
     "appium:platformVersion": "14",
     "appium:app": "C:\\Users\\{사용자명}\\appium\\apk\\[Stg]GME_7.13.0.apk",
     "appium:noReset": false,
     "appium:autoGrantPermissions": true
   }
   ```

   > **중요:** `{사용자명}` 부분을 본인의 Windows 사용자명으로 변경하세요.
   > 예: `C:\\Users\\John\\appium\\apk\\[Stg]GME_7.13.0.apk`

4. **세션 저장** (선택사항)
   - `File` → `Save As...`
   - 파일명: 원하는 이름 (예: `my-session.appiumsession`)
   - 저장 위치: 프로젝트 폴더 또는 원하는 위치

5. **세션 시작**
   - Appium 서버가 실행 중인지 확인 (`npm run appium:start`)
   - 에뮬레이터가 실행 중인지 확인
   - "Start Session" 버튼 클릭

---

## 문제 해결

### Appium 서버 연결 실패
```
ConnectionRefusedError: [WinError 10061]
```
**원인:** Appium 서버가 실행되지 않음
**해결:**
```bash
npm run appium:start
```

### 디바이스를 찾을 수 없음
```
No device found / Could not find a connected Android device
```
**원인:** 에뮬레이터가 실행되지 않았거나 연결되지 않음
**해결:**
```bash
# 연결된 기기 확인
adb devices

# 에뮬레이터 시작
emulator -avd Pixel_6
```

### 앱을 찾을 수 없음
```
App not found at path / The application at ... does not exist
```
**원인:** APK 파일 경로가 잘못되었거나 파일이 없음
**해결:**
1. `apk/` 폴더에 APK 파일이 있는지 확인
2. Git LFS로 파일 다운로드: `git lfs pull`

### 요소를 찾을 수 없음
```
NoSuchElementException
```
**원인:** Locator가 잘못되었거나 요소가 화면에 없음
**해결:**
1. Appium Inspector로 정확한 locator 확인
2. 대기 시간(wait) 추가

### run-app.sh 실행 안됨 (Windows)
```
./shell/run-app.sh: command not found
```
**원인:** PowerShell/CMD에서 Bash 스크립트 실행 시도
**해결:** Git Bash에서 실행
- 프로젝트 폴더에서 우클릭 → "Git Bash Here"
- 또는 Git Bash 실행 후 `cd /c/Users/{사용자명}/appium`

### JAVA_HOME 설정 오류
```
JAVA_HOME is not set
```
**해결:**
1. 시스템 환경 변수에 `JAVA_HOME` 추가
2. 터미널 재시작 후 확인: `echo %JAVA_HOME%`

### adb 명령어 인식 안됨
```
'adb' is not recognized as an internal or external command
```
**해결:**
1. `ANDROID_HOME` 환경 변수 확인
2. PATH에 `%ANDROID_HOME%\platform-tools` 추가
3. 터미널 재시작

---

## 참고 링크

- [Appium 공식 문서](https://appium.io/docs/en/latest/)
- [Appium Inspector 다운로드](https://github.com/appium/appium-inspector/releases)
- [Android Studio 다운로드](https://developer.android.com/studio)
- [Node.js 다운로드](https://nodejs.org/)
- [Python 다운로드](https://www.python.org/downloads/)
