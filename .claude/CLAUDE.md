# Claude 응답 가이드

## 내 배경
- IT팀 QA 엔지니어
- 웹/모바일 자동화에 관심이 많고 공부 중
- 코딩 비전공자, 이론보다 실무 중심으로 접근

## 기술 스택
- 웹 자동화: Cypress (JavaScript / TypeScript)
- 모바일 자동화: Appium (Python)
- IDE: VS Code
- OS: (사용하시는 OS로 수정해주세요)

## 주요 질문 영역
- Appium 관련 질문과 코딩 요청이 많을 예정

## 응답 스타일

### 코드 작성 시
- 구현 방식 설명
- 해당 방식을 선택한 이유 설명
- 필요한 경우 코딩 구조 지식도 함께 설명

### 새로운 개념 설명 시
- 비유와 예시를 함께 사용
- 이해하기 쉽게 풀어서 설명

### 일반 규칙
- 기본 응답 언어: 한국어
- 긴 작업은 단계별로 나눠서 진행 및 설명
- 여러 요청이 동시에 들어오면 각각 분리하여 단계별로 설명
- 선택 옵션이 여러 개일 경우 추천 순서로 나열하고 사유 설명

## 코드 스타일 선호
- 변수명/함수명: 영어 사용
- 주석: 한국어로 작성
- 코드 내 디버깅용 print/console.log 포함
- **쉘 스크립트(.sh) 작성 시**: 파일 생성 후 반드시 CRLF → LF 변환 (`sed -i '' 's/\r$//'`)을 수행할 것. VS Code에서 CRLF로 저장되어 `bad interpreter: /bin/bash^M` 에러가 반복 발생함

## 에러/문제 해결 시
- 원인 분석을 먼저 설명
- 해결 방법을 단계별로 제시
- 비슷한 에러 예방법도 함께 안내

## 학습 목표
- Appium 기본기 탄탄히 익히기
- Page Object Model 패턴 적용
- CI/CD 연동 자동화 구축

---

## 프로젝트 사전 지식

### 프로젝트 구조

```
appium/
├── config/
│   └── capabilities.py          # ANDROID_CAPS, IOS_CAPS, get_appium_server_url()
├── utils/
│   ├── auth.py                  # 로그인 모듈 (login, enter_pin_via_security_keyboard)
│   ├── initial_screens.py       # 초기 화면 처리 (언어 선택, 약관 동의)
│   ├── language.py              # 앱 언어 설정 (ensure_english_language)
│   └── helpers.py               # 유틸리티 (scroll_to_element, save_screenshot 등)
├── tools/
│   ├── ui_dump.py               # Android UI 덤프 도구 (단일/인터랙티브/Watch 모드)
│   ├── ui_dump_ios.py           # iOS UI 덤프 도구 (동일 옵션 지원)
│   ├── explore_app.py           # 앱 화면 자동 탐색 스크립트
│   ├── run_allure.py            # Allure 리포트 생성/관리
│   ├── export_summary.py        # Allure 경량 HTML 요약 Export
│   ├── update_dashboard.py      # Allure 대시보드 업데이트
│   └── serve.py                 # 로컬 HTTP 서버 (대시보드 열람용)
├── tests/
│   ├── android/                 # Android 테스트 (gme1_test.py, test_01.py, xml_test.py 등)
│   └── ios/                     # iOS 테스트 (ios_contacts_test.py, test_ios_first.py 등)
├── conftest.py                  # pytest fixture (android_driver, ios_driver, android_driver_logged_in)
├── apk/                         # APK 파일 보관 (Staging, Live)
├── ui_dumps/                    # UI 덤프 XML 저장소
├── allure-results/              # Allure 테스트 결과 (타임스탬프 폴더)
├── allure-reports/              # Allure HTML 리포트 (LATEST/, dashboard/)
├── shell/                       # 실행 스크립트 (run-stg.sh, bootstrap.ps1 등)
├── .env                         # 환경변수 (Git 미추적)
└── .env.example                 # 환경변수 템플릿
```

### 대상 앱 정보

| 항목 | Staging | Live |
|------|---------|------|
| 패키지 | `com.gmeremit.online.gmeremittance_native.stag` | `com.gmeremit.online.gmeremittance_native` |
| Resource ID 접두사 | `com.gmeremit.online.gmeremittance_native.stag:id` | `com.gmeremit.online.gmeremittance_native:id` |
| APK | `apk/Stg_GME_7.13.0.apk` | `apk/GME_v7.14.0_03_02_2026 09_35-live-release.apk` |
| 계정 환경변수 | `STG_ID` / `STG_PW` | `LIVE_ID` / `LIVE_PW` |
| Activity | `.splash_screen.view.SplashScreen` | `.splash_screen.view.SplashScreen` |
| 보안 키보드 | ACCESSIBILITY_ID로 숫자 개별 클릭 | send_keys 방식 (에뮬레이터 제한 있음) |

### 이미 구현된 주요 도구

#### 1. UI Dump 도구 (`tools/ui_dump.py`, `tools/ui_dump_ios.py`)
- **사용법**: `python tools/ui_dump.py [옵션]`
- **모드**:
  - 단일 캡처: `python tools/ui_dump.py [이름]`
  - 인터랙티브: `python tools/ui_dump.py -i` (Enter로 캡처, q로 종료)
  - **Watch 모드 (권장)**: `python tools/ui_dump.py -w` (화면 변화 자동 감지, 0.2초 간격)
  - 기존 파일 마스킹: `python tools/ui_dump.py --mask-existing`
- **저장 위치**: `ui_dumps/` (플랫폼별 aos_/ios_ 프리픽스)
- **민감정보 자동 마스킹**: 전화번호, 이메일, 생년월일 자동 마스킹 적용
- **가이드 문서**: `docs/UI_DUMP_GUIDE.md`

#### 2. 로그인 모듈 (`utils/auth.py`)
- `login(driver, username, pin, resource_id_prefix, set_english, ...)` - 전체 로그인 플로우
- `navigate_to_login_screen()` - 메인 화면에서 로그인 화면 진입
- `enter_pin_via_security_keyboard()` - 보안 키보드 PIN 입력 (Staging/Live 자동 감지)
- `_handle_post_login_popups()` - 로그인 후 팝업 처리 (지문 인증, 보이스피싱)

#### 3. 초기 화면 처리 (`utils/initial_screens.py`)
- `handle_initial_screens(driver)` - 언어 선택 + 약관 동의 자동 처리
- `is_main_screen()` - btn_lgn 존재 여부로 메인 화면 판별
- `handle_language_selection()` - English 자동 선택
- `handle_terms_and_conditions()` - 전체 동의 + 스크롤 + Next 버튼

#### 4. 언어 설정 모듈 (`utils/language.py`)
- `ensure_english_language(driver)` - 메인 화면에서 English 설정
- `set_language(driver, "한국어")` - 지정 언어로 변경
- 메인 화면의 `selectedLanguageText` 버튼 → `languageRv` 목록에서 선택

#### 5. 앱 탐색 스크립트 (`tools/explore_app.py`)
- 앱 전체 화면을 자동 탐색하여 UI 덤프 수집
- 로그인 → 홈 → 탭/메뉴/서브화면 순차 탐색
- 팝업 자동 처리 (In-App Banner, Renew Auto Debit 등)
- 결과: `ui_dumps/explore_*` 폴더에 XML + 스크린샷

#### 6. pytest Fixture (`conftest.py`)
- `android_driver` - Android 드라이버 (초기 화면 자동 처리 포함)
- `ios_driver` - iOS 드라이버
- `android_driver_logged_in` - 로그인 완료 상태 드라이버
- `@pytest.mark.skip_initial_screens` - 초기 화면 처리 건너뛰기
- `--record-video` - 테스트 화면 녹화 (실패 시 Allure 첨부)
- `--allure-attach=hybrid|all` - Allure 첨부 정책

#### 7. Allure 리포트 (`tools/run_allure.py`)
- 테스트 결과 자동 수집 → HTML 리포트 생성 → 대시보드 업로드
- 필수 패키지 자동 감지/설치 (`_ensure_dependencies`)
- `allure-results/YYYYMMDD_HHMMSS/` - 타임스탬프별 결과 보관
- `allure-reports/LATEST/` - 최신 리포트 고정 경로
- `allure-reports/dashboard/` - 로컬 실행 이력 대시보드
- `--upload` (기본 켜짐): Vercel 웹 대시보드에 결과 업로드
- `--no-upload`: 업로드 끄기
- `--open`: 리포트 생성 후 브라우저에서 열기
- 실패 시 자동 첨부: 스크린샷, page_source.xml, capabilities.json, logcat.txt
- **가이드 문서**: `docs/ALLURE_REPORT_GUIDE.md`

#### 8. 대시보드 업로드 (`tools/upload_to_dashboard.py`)
- Allure 리포트를 Vercel 웹 대시보드(https://allure-dashboard-three.vercel.app)에 업로드
- 테스트 통계 (passed/failed/broken/skipped) + 첨부파일 (Vercel Blob)
- 첨부파일: 스크린샷(PNG), 비디오(MP4), logcat, page_source, capabilities
- `BLOB_READ_WRITE_TOKEN` 필요 (없으면 첨부파일 건너뜀, 메타데이터만 업로드)
- **사용법**: `python tools/upload_to_dashboard.py <timestamp>` 또는 `--all`

### 기존 가이드 문서 목록 (`docs/`)

| 문서 | 내용 |
|------|------|
| `UI_DUMP_GUIDE.md` | UI Dump 도구 전체 사용법, XML 분석법, Locator 전략 |
| `CODING_GUIDELINES.md` | 테스트 스크립트 작성 규칙 (파일명, Locator 우선순위, Allure 어노테이션) |
| `APP_STRUCTURE.md` | GME 앱 기능 구조 리스트 (화면별 요소 정보, resource-id 정리) |
| `ALLURE_REPORT_GUIDE.md` | Allure 리포트 탭별 설명, 30초 분석 루틴, 진단 파일 활용법 |
| `IOS_SETUP_GUIDE.md` | iOS 자동화 환경 세팅 (Xcode, XCUITest 드라이버, 시뮬레이터) |
| `IOS_TEST_GUIDE.md` | iOS UI Dump 기반 테스트 작성 가이드 (시행착오 & 해결 방법 포함) |
| `MAC_SETUP_GUIDE.md` | macOS Appium 환경 세팅 (Homebrew, Node.js, Android Studio) |
| `README_CLONE.md` | 클론 후 초기 환경 구성 (bootstrap 스크립트, 필수 체크리스트) |

### 환경변수 (.env)

| 변수 | 설명 | 필수 여부 |
|------|------|-----------|
| `STG_ID` / `STG_PW` | Staging 테스트 계정 | Staging 테스트 시 필수 |
| `LIVE_ID` / `LIVE_PW` | Live 테스트 계정 | Live 테스트 시 필수 |
| `STG_APK` / `LIVE_APK` | APK 파일명 | 앱 설치 시 필수 |
| `GME_RESOURCE_ID_PREFIX` | resource-id 접두사 | 선택 (기본: Staging 패키지) |
| `APPIUM_HOST` / `APPIUM_PORT` | Appium 서버 주소 | 선택 (기본: 127.0.0.1:4723) |
| `ANDROID_UDID` | 실물 디바이스 시리얼 | 실기기 테스트 시 필수 |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob 토큰 (첨부파일 업로드용) | 선택 (미설정 시 첨부파일 건너뜀) |

### 코드 작성 전 반드시 확인

1. **기존 도구가 있는지 확인** - 새로 만들기 전에 `tools/`, `utils/` 폴더의 기존 코드를 먼저 확인
2. **최신 UI Dump 참조** - `ui_dumps/` 폴더에서 최신 XML 파일 분석 후 코드 작성
3. **Locator 우선순위** - ACCESSIBILITY_ID > Resource ID > XPath
4. **앱 빌드 구분** - Staging과 Live의 패키지명/resource-id가 다름, `resource_id_prefix` 파라미터로 구분
5. **가이드 문서 참조** - `docs/` 폴더의 해당 가이드를 먼저 읽고 기존 패턴을 따름

---

## 작업 완료 후 규칙

**큰 단위의 작업이 완료될 때마다** 자동으로 아래 파일들을 업데이트한다:

1. **`change_notes.md`**: 해당 작업의 변경 내용을 날짜별로 정리해서 기록 (기존 형식 참고)
2. **`Todo.md`**: 다음 진행할 작업, 미완료 항목, 알려진 이슈를 정리해서 기록
3. **Claude CLI 메모리 파일** (`~/.claude/projects/-Users-sph/memory/MEMORY.md`): 새로운 프로젝트 정보, 주요 경로, 패턴 등 세션 간 기억해야 할 정보 반영

> "큰 단위 작업"의 기준: 새로운 기능 구현, 프로젝트 생성/배포, 시스템 구조 변경, 도구 추가 등 여러 파일에 걸친 의미 있는 작업 단위

---

## 워크플로우

### Git Push

**트리거**: "깃에 업로드 해줘" / "git 푸시" / "깃에 푸시해줘" / "깃에 올려줘"

**참고 문서**: Git 작업 시 반드시 `GIT_RULES.md` 파일을 참고하여 규칙을 준수할 것 (커밋 메시지 형식, 보안 정책, Gist 동기화 등)

**동작:**
1. 지금까지의 변동 사항을 `change_notes.md` 파일에 정리해서 작성
2. 해당 작업이 재사용 시 문서 참고 혹은 내용 파악에 문서가 필요하면 `docs/` 폴더에 설명 문서를 추가
3. 현재 바라보는 브랜치에 변경사항을 **GitHub과 GitLab 모두** 푸시 (`GIT_RULES.md` 규칙 준수)
   - 커밋 메시지는 `GIT_RULES.md` 섹션 8 형식에 맞게 정돈하여 작성
   - `change_notes.md` 수정 시 Gist 동기화도 함께 진행

### 인사 (세션 시작)

**트리거**: "하이" / "안녕" / "컴백"

**동작:**
1. `change_notes.md` 파일을 확인하여 최근 작업 내용을 파악
2. `Todo.md` 파일을 확인하여 미완료 작업 및 다음 진행 사항을 파악
3. 현재 진행 상황을 간결하게 브리핑:
   - 최근 완료된 작업 요약
   - 미완료/진행 중인 작업 목록
   - 다음 우선 진행 작업 제안

### 퇴근 (세션 종료)

**트리거**: "바이" / "갈게" / "퇴근"

**동작:**
1. 당일 작업한 내용을 `change_notes.md` 파일에 정리해서 추가
2. 미완료 작업 및 다음 진행할 작업을 `Todo.md` 파일에 정리해서 기록
3. git 저장소의 최신 코드와 로컬 코드를 비교하여 최신이 아닌 경우 push 진행
   - **커밋 메시지**: `GIT_RULES.md` 섹션 8의 형식을 준수하여 정돈된 메시지 작성
     - `<type>: <파일/기능> - <변경내용>` 형식
     - 본문에 한글 상세 설명 포함
   - **push 대상**: GitHub과 GitLab **모두** push (`GIT_RULES.md` 섹션 1 참고)
     ```bash
     git push github <branch>
     git push gitlab <branch>
     ```
   - `change_notes.md` 수정 시 **Gist 동기화**도 함께 진행 (`GIT_RULES.md` 섹션 11)

### 자동화 코드 작성

**트리거**: "자동화 코드를 만들어줘" (OS를 언급하지 않으면, 현재 작업 중인 흐름을 보고 판단해서 사용자에게 물어볼 것)

**동작:**
1. 각 OS에 맞는 설정 확인 (capabilities, 드라이버, 시뮬레이터/에뮬레이터 상태)
2. UI Dump를 사용하여 대상 화면 요소 분석 → 테스트 코드 구현
3. 구현된 코드를 실행하면서 테스트 및 디버깅 진행
4. Allure Report를 통해 결과 확인:
   - 성공: 완료 결과를 보여줌
   - 실패: 실패 사유를 정리해서 알려줌
5. 실패 사유는 정리해서 재발하지 않도록 관련 가이드 문서를 업데이트
6. **반복적인 실패가 발생하여 진행이 불가한 경우**: 사용자에게 알리고 중지
