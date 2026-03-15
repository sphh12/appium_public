# Mobile Test Automation Framework

모바일 앱(Android/iOS) 자동화 테스트 프레임워크

Appium + Python + pytest 기반으로 멀티 환경 자동 전환, 보안 키보드 처리, UI 덤프 도구, Allure 리포팅 파이프라인을 구현했습니다.

---

## 기술 스택

| 카테고리 | 기술 |
|---------|------|
| 테스트 프레임워크 | Appium + Python 3.12 + pytest |
| Android 드라이버 | UiAutomator2 |
| iOS 드라이버 | XCUITest |
| 리포팅 | Allure Report + Vercel 웹 대시보드 |
| 디자인 패턴 | Page Object Model (POM) |
| CI/CD | Shell Script 5단계 파이프라인 |

---

## 주요 구현 사항

### 1. 멀티 환경 자동 전환 (`APP_ENV`)

`APP_ENV` 환경변수 하나로 3개 환경의 APK, resource-id 접두사, 계정 정보, 키보드 타입이 자동 전환됩니다.

```bash
APP_ENV=stage    pytest tests/android/ -v --platform=android   # Staging
APP_ENV=live     pytest tests/android/ -v --platform=android   # Live
APP_ENV=livetest pytest tests/android/ -v --platform=android   # LiveTest
```

| APP_ENV | APK 폴더 | resource-id 접두사 | 키보드 타입 |
|---------|----------|-------------------|------------|
| `stage` | `apk/stage/` | `...stag:id` | 숫자 키패드 |
| `live` | `apk/live/` | `...:id` | QWERTY |
| `livetest` | `apk/livetest/` | `...livetest:id` | QWERTY |

### 2. 보안 키보드 자동 입력

일반 `send_keys`가 동작하지 않는 커스텀 보안 키보드를 자동으로 처리합니다.

- **숫자 키패드** (Staging): Accessibility ID로 각 숫자 버튼 직접 탭
- **QWERTY 키보드** (Live): content-desc 속성 기반 키 입력, Shift/특수문자 모드 자동 전환

### 3. 초기 화면 자동 처리

앱 첫 실행 시 나타나는 화면들을 자동으로 통과합니다.

- 언어 선택 (11개 언어 지원)
- 약관 동의 (전체 동의 + 스크롤 + 확인)
- 로그인 후 팝업 처리 (지문 인증, 보안 경고)

### 4. UI Dump 분석 도구

Android/iOS 화면 요소를 XML로 캡처하는 자체 개발 도구입니다.

```bash
python tools/ui_dump.py              # 단일 캡처
python tools/ui_dump.py -i           # 인터랙티브 모드
python tools/ui_dump.py -w           # Watch 모드 (화면 변화 자동 감지)
python tools/ui_dump.py --mask-existing  # 기존 파일 마스킹
```

- Watch 모드: 0.2초 간격으로 화면 변화 자동 감지
- 민감정보 자동 마스킹 (전화번호, 이메일, 생년월일)

### 5. 테스트 실행 파이프라인

쉘 스크립트 5단계 자동화 파이프라인:

```
STEP 1: 사전 체크 & 자동 시작
  ├─ Appium 서버 (미실행 시 자동 시작)
  ├─ 에뮬레이터/시뮬레이터 (미실행 시 자동 부팅)
  ├─ Python venv (없으면 생성)
  ├─ Appium 드라이버 (UiAutomator2 / XCUITest)
  └─ Allure CLI

STEP 2: pytest 테스트 실행

STEP 3: Allure HTML 리포트 생성

STEP 4: 웹 대시보드 업로드

STEP 5: 리포트 브라우저 열기 (선택)
```

```bash
./shell/run-aos.sh --sample1_test              # Staging
./shell/run-aos.sh --sample1_test --live       # Live
./shell/run-aos.sh --all --report              # 전체 + 리포트
./shell/run-ios.sh --ios_contacts_test         # iOS
```

### 6. Allure 리포트 자동화

실패 시 진단 파일을 자동 첨부하여 원인 분석 시간을 단축합니다.

| 첨부 파일 | 실패 시 | 성공 시 (all 모드) |
|-----------|---------|-------------------|
| 스크린샷 | O | O |
| page_source.xml | O | O |
| capabilities.json | O | - |
| logcat.txt | O | - |
| 비디오 (MP4) | O | - |

---

## 프로젝트 구조

```
├── config/
│   └── capabilities.py          # Desired Capabilities + 환경별 설정
├── utils/
│   ├── auth.py                  # 로그인 모듈 (보안 키보드 처리)
│   ├── initial_screens.py       # 초기 화면 자동 처리
│   ├── language.py              # 앱 언어 설정
│   └── helpers.py               # 유틸리티 (스크롤, 스크린샷 등)
├── tests/
│   ├── android/                 # Android 테스트
│   └── ios/                     # iOS 테스트
├── tools/
│   ├── ui_dump.py               # Android UI 덤프 도구
│   ├── ui_dump_ios.py           # iOS UI 덤프 도구
│   ├── explore_app.py           # 앱 화면 자동 탐색
│   ├── run_allure.py            # Allure 리포트 생성/관리
│   └── upload_to_dashboard.py   # 웹 대시보드 업로드
├── pages/
│   ├── base_page.py             # Page Object Model 베이스
│   └── sample_page.py           # POM 샘플 구현
├── shell/
│   ├── run-app.sh               # 메인 실행 스크립트 (5단계 파이프라인)
│   ├── run-aos.sh               # Android 래퍼
│   └── run-ios.sh               # iOS 래퍼
├── docs/                        # 가이드 문서
├── conftest.py                  # pytest fixture (드라이버, 리포팅)
├── apk/                         # APK 폴더 (stage/live/livetest)
└── .env.example                 # 환경변수 템플릿
```

---

## 설치 및 실행

### 사전 요구사항

- Python 3.10+
- Node.js 18+
- Android Studio (에뮬레이터)
- Xcode (iOS 시뮬레이터, macOS만)
- Appium (`npm install -g appium`)
- Allure CLI (`brew install allure`)

### 설치

```bash
git clone https://github.com/sphh12/appium_public.git
cd appium_public

# Python 가상환경
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Appium 드라이버
appium driver install uiautomator2
appium driver install xcuitest

# 환경변수 설정
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력
```

### 실행

```bash
# 쉘 스크립트 (자동 사전 체크 포함)
./shell/run-aos.sh --sample1_test

# 또는 pytest 직접 실행
source venv/bin/activate
npx appium &                      # Appium 서버
pytest tests/android/sample1_test.py -v --platform=android
```

상세한 pytest 실행 방법은 [docs/PYTEST_GUIDE.md](docs/PYTEST_GUIDE.md)를 참고하세요.

---

## 문서

| 문서 | 내용 |
|------|------|
| [PYTEST_GUIDE.md](docs/PYTEST_GUIDE.md) | pytest 직접 실행 가이드 |
| [UI_DUMP_GUIDE.md](docs/UI_DUMP_GUIDE.md) | UI Dump 도구 사용법 |
| [CODING_GUIDELINES.md](docs/CODING_GUIDELINES.md) | 테스트 코드 작성 규칙 |
| [ALLURE_REPORT_GUIDE.md](docs/ALLURE_REPORT_GUIDE.md) | Allure 리포트 가이드 |
| [MAC_SETUP_GUIDE.md](docs/MAC_SETUP_GUIDE.md) | macOS 환경 세팅 |
| [IOS_SETUP_GUIDE.md](docs/IOS_SETUP_GUIDE.md) | iOS 자동화 환경 세팅 |
| [IOS_TEST_GUIDE.md](docs/IOS_TEST_GUIDE.md) | iOS 테스트 작성 가이드 |
| [PORTFOLIO_GUIDE.md](docs/PORTFOLIO_GUIDE.md) | 포트폴리오 공개 가이드 |
