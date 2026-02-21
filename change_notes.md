# Change Notes

## 2026-02-21

### Allure Dashboard - Next.js 웹 대시보드 구축 + Vercel 배포

기존 로컬 전용(`tools/serve.py`) 대시보드를 Next.js 기반 웹 대시보드로 전환하여 Vercel에 배포 완료.
팀원 누구나 웹에서 테스트 결과를 확인할 수 있게 됨.

**프로덕션 URL**: https://allure-dashboard-three.vercel.app

#### 신규 프로젝트: `~/allure-dashboard/`
- **기술 스택**: Next.js 15 (App Router) + TypeScript + Tailwind CSS + Prisma 6 + Vercel Postgres (Neon)
- **API 엔드포인트**:
  - `GET /api/runs` - 실행 목록 조회 (필터: platform, status, q)
  - `POST /api/runs` - 실행 결과 등록
  - `GET /api/runs/[timestamp]` - 실행 상세 조회
- **대시보드 UI**:
  - 메인 페이지: 통계 카드, 패스율 바, 필터/검색, 테이블 (스택 바 차트 포함)
  - 상세 페이지: 원형 패스율, Git 정보, Suites/Behaviors, Environment
  - 다크 테마: 뉴트럴 블랙 + 흰색 포인트 배색
- **DB 스키마**: Run (테스트 실행 메타데이터), Artifact (첨부파일, Phase 2 대비)

#### appium 프로젝트 변경
- **`tools/upload_to_dashboard.py`** (신규): 대시보드 API로 데이터 업로드 스크립트
  - `--all`: 기존 리포트 일괄 업로드 (마이그레이션용)
  - `--dashboard-url`: 대시보드 API URL 지정
  - `update_dashboard.py`의 데이터 읽기 로직 재사용
- **`tools/run_allure.py`** (수정): `--upload`, `--dashboard-url` 옵션 추가
  - 테스트 완료 후 자동으로 대시보드에 업로드 가능

#### 배포 및 마이그레이션
- Vercel CLI로 프로젝트 배포, Neon Postgres 연결
- 기존 19개 리포트 일괄 업로드 완료

---

## 2026-02-19

### explore_app.py 인터랙티브 요소 검증 시스템 추가

- **`_log_interactive_elements(sources, base_name)`**: XML page_source를 ElementTree로 파싱하여 인터랙티브 요소를 5가지 타입(버튼/아이콘버튼/토글/ViewPager/스크롤영역)으로 자동 분류·리포트
- **`_capture_viewpager_pages(driver, folder, base_name)`**: ViewPager 자동 감지 → dotsIndicator로 페이지 수 파악 → 가로 스와이프 캡처 → 원위치 복귀
- **`scroll_and_capture` 통합**: 스크롤 중 `captured_sources` 수집 → 완료 후 검증 리포트 + ViewPager 자동 캡처

### explore_app.py Card 3rd depth 자동 캡처 (explore_card_3rd_depth)

- **Card Features 서브화면 12개 대상** 자동 탐색 구현
  - c1~c8: 클릭 → 화면 변화 감지 → 캡처 → 복귀
  - c9 (upArrow): UI 확장 → 캡처 → 접기
  - c10 (ViewPager): 스와이프 → 2페이지 캡처 → + 버튼 탐색
  - c11~c12: UiScrollable + 수동 스크롤 + 텍스트 검색 3단계 탐색
- **화면 변화 감지 로직**: `_has_screen_changed()` 추가 - 클릭 전/후 텍스트 비교로 실제 화면 이동 여부 판별
- **팝업/바텀시트 분리 캡처**: `is_popup` 플래그로 `verify=False` 적용 → 팝업이 닫히지 않고 그대로 캡처
- **캡처 결과**: 8개 서브화면 캡처 성공 (c1, c4~c10)
  - c2/c3: Card 화면에 해당 ID 없음 (Home 전용)
  - c11/c12: 현재 앱 상태에서 DOM에 요소 없음

### explore_app.py 실행 옵션 추가

- 커맨드라인 인자로 특정 섹션만 실행 가능
  - `python tools/explore_app.py card_3rd` → Card 3rd depth만 실행
  - `python tools/explore_app.py` → 전체 탐색 (기존과 동일)
  - 사용 가능: `home`, `hamburger`, `history`, `card`, `card_3rd`, `event`, `profile`

변경 파일:
- [tools/explore_app.py](tools/explore_app.py)

---

## 2026-02-17

### Live 앱 로그인 자동화 완성 (QWERTY 보안 키보드 대응)

- **Live 앱 전용 QWERTY 커스텀 보안 키보드 완전 대응**
  - `_type_on_live_security_keyboard()`: 영문(소/대문자) + 숫자 + 특수문자 입력 지원
  - 대문자 키: Shift 후 `"Capital S 니은"` 형식 content-desc 매핑
  - 특수문자: 한국어 설명 매핑 (`"!" → "느낌표"`, `"@" → "골뱅이"` 등 33개)
  - 모드 전환: 소문자↔대문자(Shift), 영문↔특수문자 자동 전환
  - Shift 1회용 동작 지원 (대문자 1글자 입력 후 자동 해제)

- **간편비밀번호(Simple Password) 설정 자동화**
  - 4자리 PIN 생성 입력 → 재확인 입력 → 성공 팝업 OK 클릭
  - 랜덤 배치 숫자 키패드 대응 (content-desc 기반)
  - 연속 숫자 제한 대응: `1234` → `1212`로 변경 ("sequence characters" 에러 방지)

- **잠금화면 자동 처리 (2가지 유형)**
  - Full Password Lock: `"Enter password to unlock"` + QWERTY 키보드 → 비밀번호 입력으로 해제
  - Simple Password Lock: `"Login with ID/Password"` 클릭 → YES → 로그인 화면 이동
  - 권한 동의 화면: `"Agree"` 클릭 (pm clear 후 첫 실행 대응)

- **보안 키보드 진단 스크립트 추가**
  - `tools/debug_keyboard.py`: 키보드 상태별 UI 덤프 캡처 (소문자/대문자/특수문자)
  - 키보드 content-desc 형식 확인용 도구

- **로그인 후 팝업 처리 강화**
  - 간편비밀번호 설정 후에도 보이스피싱 경고 팝업 처리 추가
  - `_dismiss_success_popup()`: btnOk → "OK" 텍스트 → 아무 Button 순서로 fallback

테스트 흐름 (전체 자동화 성공):
```
앱 실행 → 잠금화면 해제 → 간편비밀번호 설정 → Success OK → 보이스피싱 처리 → 홈 화면 도달
```

변경 파일:
- [utils/auth.py](utils/auth.py) - QWERTY 키보드, 잠금화면, 간편비밀번호 처리
- [tools/test_login_live.py](tools/test_login_live.py) - Live 앱 로그인 테스트 스크립트
- [tools/debug_keyboard.py](tools/debug_keyboard.py) (신규) - 키보드 진단 도구
- .env / .env.example - SIMPLE_PIN 추가 (1212)

---

## 2026-02-16 (2차)

### 앱 화면 자동 탐색 스크립트 (explore_app.py) 신규 생성

- **`tools/explore_app.py` 신규 생성**: 앱의 전체 화면/메뉴 구조를 자동 탐색하고 UI Dump를 캡처하는 스크립트
  - 하단 탭 5개 (Home, History, Card, Event, Profile) 자동 탐색
  - 햄버거 메뉴(Side Drawer) 8개 항목 자동 진입 및 캡처
  - 서브 탭 (HorizontalScrollView, TabLayout) 자동 감지 및 캡처
  - Profile 내 메뉴 항목 자동 탐색 (비밀번호/로그아웃 등 위험 항목 제외)

- **Live / Staging 앱 전환 기능**
  - `USE_LIVE` 환경변수로 전환 (기본: `true`)
  - Live: `com.gmeremit.online.gmeremittance_native` / LIVE_ID, LIVE_PW 사용
  - Staging: `com.gmeremit.online.gmeremittance_native.stag` / STG_ID, STG_PW 사용
  - 앱 액티비티도 자동 전환 (Live: SplashScreen, Staging: ActivityMain)

- **팝업 자동 처리 시스템**
  - Renew Auto Debit: `btn_okay` 클릭 → `iv_back` 복귀 (테스트 환경 팝업)
  - In-App Banner: `imgvCross` (X), `btnTwo` (Cancel) 우선 처리
  - 공통 닫기: `btn_close`, `btnCancel`, `content-desc=close`
  - 바텀시트: `touch_outside`, `design_bottom_sheet` → 백키
  - 앱 종료 방지 안전장치: `current_package` 확인 후 백키, 종료 시 `activate_app` 재활성화
  - **팝업 캡처 기능**: 팝업 닫기 전 UI Dump 자동 저장 (모듈 레벨 `_popup_capture_folder`)

- **안정성 기능**
  - `ensure_app_running()`: 앱 포그라운드 확인 + `activate_app` 재활성화
  - `verify_app_screen()`: 앱/팝업/시스템UI/unknown 상태 분류
  - `ensure_clean_screen()`: 팝업 완전 제거 후 앱 화면 보장
  - `go_back_to_home()`: 어떤 화면에서든 홈으로 안정 복귀 (5단계 전략)
  - UiAutomator2 크래시 자동 복구 (드라이버 재생성)
  - `noReset=True` + `appPackage/appActivity` 방식 (APK 재설치 방지)

- **실행 방법**
  ```bash
  USE_LIVE=true /Users/sph/appium/venv/bin/python3 tools/explore_app.py
  ```

### APP_STRUCTURE.md 신규 생성

- 앱 전체 화면 구조 문서화 (자동화 코드 생성용 기반 자료)
- UI Dump XML 분석 기반으로 10개 화면 구조 확인 완료
  - Home, Hamburger Menu, Notification, Link Bank Account, Settings 등
- 10개 미확인 화면 목록 기록 (팝업 오버레이로 인한 캡처 실패분)
- 각 화면별 resource-id, content-desc, 텍스트 등 UI 요소 상세 기록

### Live APK 설치

- Live Release APK (`GME_v7.14.0_03_02_2026 09_35-live-release.apk`) adb install 완료
- Staging 앱의 불필요한 팝업 과다 발생으로 Live 앱으로 전환 결정

추가 파일:
- [tools/explore_app.py](tools/explore_app.py) (신규)
- [docs/APP_STRUCTURE.md](docs/APP_STRUCTURE.md) (신규)

---

## 2026-02-16

### Allure 대시보드 플랫폼 필터 추가

- **Platform 드롭다운 필터 추가**: `Platform: 전체` / `Android` / `iOS` 선택 가능
  - 기존에는 검색창에 "ios"를 직접 입력해야만 iOS 결과를 찾을 수 있었음
  - 디버깅 과정에서 생성된 다수의 Android 로그로 인해 iOS 결과가 뒤로 밀리는 문제 해결
- Result 필터 옆에 배치, Clear 버튼 클릭 시 함께 초기화

변경 파일:
- [allure-reports/dashboard/index.html](allure-reports/dashboard/index.html)
- [tools/update_dashboard.py](tools/update_dashboard.py)

### 쉘 스크립트 구조 개편 (플랫폼별 래퍼)

- **`run-aos.sh` 신규 생성**: Android 전용 래퍼 (`run-app.sh --platform android`)
- **`run-stg.sh` / `run-live.sh` 삭제**: `run-aos.sh --stg` / `run-aos.sh --live`로 대체
- 최종 구조: `run-app.sh`(메인 엔진) + `run-aos.sh`(Android) + `run-ios.sh`(iOS)

### run-app.sh 환경 호환성 수정 (macOS/Windows 크로스 플랫폼)

- **`~/.zshrc` 자동 로드 추가**: bash 스크립트에서 `ANDROID_HOME`, `npx`, `allure` 등 PATH 누락 방지
  - `if [[ -f "$HOME/.zshrc" ]]` 조건이라 Windows에서는 실행 안 됨 (안전)
- **ANDROID_HOME 자동 탐색**: `adb` 미발견 시 macOS 기본 SDK 경로(`~/Library/Android/sdk`) 자동 탐색
- **Appium 드라이버 감지 수정**: `appium driver list`가 stderr로 출력 → `2>/dev/null`을 `2>&1`로 변경
  - UiAutomator2, XCUITest 모두 동일 수정
  - grep 패턴에서 불필요한 `@` 제거
- **PROJECT_ROOT 경로 정규화**: `$SCRIPT_DIR/..` → `$(cd "$SCRIPT_DIR/.." && pwd)` 로 절대 경로 변환
- **.env CRLF 방지**: `tr -d '\r'` 추가하여 APK 파일명 뒤 `\r` 제거
- **CMD 실행 방식 변경**: `$CMD` → `eval $CMD` (대괄호/공백 등 특수문자 포함 경로 처리)

### APK 파일명 변경

- Appium(Node.js)이 대괄호 `[]`를 glob 패턴으로 해석하여 파일 접근 실패
- `[Stg]GME_7.13.0.apk` → `Stg_GME_7.13.0.apk` 로 변경
- `[LiveTest]GME_7.14.0.apk` → `LiveTest_GME_7.14.0.apk` 로 변경
- `.env` 파일 및 `run-app.sh` 기본값도 함께 업데이트

### CLAUDE.md 업데이트

- 쉘 스크립트 CRLF 방지 규칙 추가: `.sh` 파일 생성 후 반드시 LF 변환 수행

### Windows 환경 호환 참고사항

- macOS 전용 수정사항(`~/.zshrc` 로드, SDK 경로 탐색)은 조건부 실행이라 Windows에 영향 없음
- Windows에서 git pull 후 필요한 조치:
  1. APK 파일명 변경 (`[Stg]` → `Stg_`, `[LiveTest]` → `LiveTest_`)
  2. `.env`의 `STG_APK` 값 맞추기
  3. `run-stg.sh`/`run-live.sh` 대신 `run-aos.sh --stg`/`run-aos.sh --live` 사용

변경 파일:
- [shell/run-aos.sh](shell/run-aos.sh) (신규)
- [shell/run-app.sh](shell/run-app.sh)
- [.claude/CLAUDE.md](.claude/CLAUDE.md)
- .env (APK 파일명 변경)

삭제 파일:
- shell/run-stg.sh
- shell/run-live.sh

---

### iOS 연락처 앱 테스트 완성

- **핵심 버그 수정**: iOS 한국어 이름 표시 형식 차이 해결
  - iOS 연락처는 `"홍길동"` (성+이름, 공백 없음) 형식으로 표시
  - 기존 코드의 `"길동 홍"` (이름 + 공백 + 성) → 목록에서 검색 실패
- **앱 상태 초기화 안정화**: `terminate_app()` + `activate_app()`으로 fixture 개선
  - 이전 테스트 실패로 앱이 비정상 화면에 남아있는 문제 해결
- 최종 테스트 **1 passed in 75.63s** 달성

변경 파일:
- [tests/ios/ios_contacts_test.py](tests/ios/ios_contacts_test.py)

### UI Dump 폴더 플랫폼 프리픽스 도입

- **Android**: `aos_` 프리픽스 추가 (`tools/ui_dump.py`)
- **iOS**: `ios_` 프리픽스 추가 (`tools/ui_dump_ios.py`)
- 모든 캡처 모드(단일/Interactive/Watch)에서 플랫폼별 폴더 생성

| 모드 | Android | iOS |
|------|---------|-----|
| 단일 캡처 | `aos_20260216_1430/` | `ios_20260216_1430/` |
| Interactive | `aos_20260216_1430/` | `ios_20260216_1430/` |
| Watch | `aos_260216_1430/` | `ios_260216_1430/` |

- 기존 폴더명도 변경:
  - `260123_1254/` → `aos_260123_1254/`
  - `261022_132638/` → `aos_261022_132638/`
  - iOS 단일 파일 → `ios_20260215_0009/`, `ios_20260215_2348/` 폴더로 이동

변경 파일:
- [tools/ui_dump.py](tools/ui_dump.py)
- [tools/ui_dump_ios.py](tools/ui_dump_ios.py)

### 문서 업데이트 (프리픽스 반영)

- 폴더 구조 예시, Watch 출력 경로 등 `aos_`/`ios_` 프리픽스 반영

변경 파일:
- [docs/UI_DUMP_GUIDE.md](docs/UI_DUMP_GUIDE.md)
- [docs/CODING_GUIDELINES.md](docs/CODING_GUIDELINES.md)
- [docs/IOS_TEST_GUIDE.md](docs/IOS_TEST_GUIDE.md)
- [tests/android/basic_01_test.py](tests/android/basic_01_test.py) - docstring 경로 수정

### iOS 테스트 작성 가이드 생성

- UI Dump 기반 iOS 테스트 작성 전체 흐름 정리
- 시행착오 7가지 및 해결 방법 문서화
  - 한국어 이름 형식, StaleElement 방지, Cell/TextField 구분, 키보드 닫기 등
- 헬퍼 메서드 모음, iOS vs Android 차이표, 체크리스트 포함

추가 파일:
- [docs/IOS_TEST_GUIDE.md](docs/IOS_TEST_GUIDE.md) (신규)

### CLAUDE.md 워크플로우 추가

- **Git Push 워크플로우**: 트리거 키워드 → change_notes 작성 → 푸시
- **자동화 코드 작성 워크플로우**: OS 확인 → UI Dump → 코드 구현 → Allure 결과 → 가이드 업데이트
- **작업 완료 후 규칙**: change_notes.md 작성 의무화

변경 파일:
- [.claude/CLAUDE.md](.claude/CLAUDE.md)

---

## 2026-02-15

### iOS UI Dump 도구 생성

- Android 버전(`ui_dump.py`)과 별도로 iOS 전용 UI Dump 도구 생성
- 단일 캡처, Interactive(-i), Watch(-w), `--mask-existing` 모드 지원
- iOS 전용 요소 분석: `XCUIElementType` 기반 통계, NavigationBar에서 화면 이름 추출
- `XCUITestOptions` + `IOS_CAPS` 사용

추가 파일:
- [tools/ui_dump_ios.py](tools/ui_dump_ios.py) (신규)

### iOS 연락처 앱 테스트 시나리오 작성

- 시뮬레이터 내장 연락처 앱 대상 (`bundleId: com.apple.MobileAddressBook`)
- 시나리오: 연락처 추가 → 정보 입력(성/이름/직장/전화번호) → 저장 → 조회 검증 → 테스트 데이터 정리
- 연락처 목록/추가 화면 UI Dump 캡처 (`ios_20260215_2348/`)

주요 구현 패턴:
- TextField 입력: 클릭 → 재탐색 → `send_keys` (StaleElement 방지)
- 동적 요소: "전화번호 추가" Cell 클릭 → "휴대전화" TextField 생성 후 XPath로 탐색
- 키보드 닫기: NavigationBar 탭
- 전화번호 검증: `page_source`에서 숫자만 추출하여 비교

추가 파일:
- [tests/ios/ios_contacts_test.py](tests/ios/ios_contacts_test.py) (신규)

---

## 2026-02-14

### iOS 자동화 환경 구축

- **Xcode 설치 및 iOS 시뮬레이터 설정**
  - Xcode 설치 → Settings > Platforms에서 iOS 26.2 추가
  - iPhone 17 시뮬레이터 부팅 확인
- **Appium XCUITest 드라이버 설치**
  - `appium driver install xcuitest`
  - `appium-doctor --ios` 환경 검증 통과 (필수 항목 all passed)
- **PATH 설정 확인**: Homebrew/Node.js는 이미 설치되어 있었으나 세션에서 PATH 미로드 → `~/.zprofile`에 기존 설정 확인

### iOS 시뮬레이터 첫 연결 테스트

- Safari 브라우저 기반 iOS 테스트 4건 작성 및 전체 통과
  - 시뮬레이터 연결, 화면 크기 확인, URL 열기, 페이지 소스 확인
- Safari Web Inspector 활성화 및 `webviewConnectTimeout` 설정으로 타임아웃 해결

추가 파일:
- [tests/ios/test_ios_first.py](tests/ios/test_ios_first.py) (신규)

### iOS Capabilities 설정 업데이트

- `IOS_CAPS`의 `platformVersion`을 `"17.0"` → `"26.2"`로 수정
- 환경변수 대응: `IOS_DEVICE_NAME`, `IOS_PLATFORM_VERSION`

변경 파일:
- [config/capabilities.py](config/capabilities.py)

### iOS 환경 설정 가이드 생성

- macOS + Xcode + 시뮬레이터 + Appium 설정 전체 절차 문서화
- 시뮬레이터 관리, Safari 설정, 에러 트러블슈팅 포함

추가 파일:
- [docs/IOS_SETUP_GUIDE.md](docs/IOS_SETUP_GUIDE.md) (신규)

### 기타

- 컴퓨터 이름 변경: `hanseungpil-ui-MacBookPro` → `sph-mbp`

---

## 2026-02-04

### 앱 언어 설정 모듈 추가 (language.py)

- **언어 변경 모듈 신규 생성**: 로그인 전 앱 언어를 영어로 설정하는 기능
  - `is_main_screen_with_language_button()`: 메인 화면의 언어 버튼 존재 확인
  - `open_language_list()`: 언어 선택 목록 열기
  - `set_language_to_english()`: 영어로 언어 설정
  - `ensure_english_language()`: 로그인 전 호출되는 통합 함수
- **UiSelector 기반 요소 찾기**: XPath보다 안정적인 UiSelector 방식 적용
  - 1순위: UiSelector (resourceId + text 조합)
  - 2순위: XPath 폴백
  - 3순위: 스크롤 후 재시도
- **auth.py 통합**: `login()` 함수에 `set_english` 파라미터 추가
  - 기본값 `True`로 로그인 전 자동 영어 설정

주요 Resource-ID:
| Resource-ID | 용도 |
|-------------|------|
| `selectedLanguageText` | 메인 화면의 언어 선택 버튼 |
| `languageRv` | 언어 목록 RecyclerView |
| `countryLanguageText` | 각 언어 항목의 텍스트 |

변경/추가 파일:
- [utils/language.py](utils/language.py) (신규)
- [utils/auth.py](utils/auth.py)
- [tests/test_language_module.py](tests/test_language_module.py) (신규, 디버그용)

---

## 2026-02-03

### 민감정보 환경변수화 (.env 파일 분리)

- **환경변수 기반 설정 관리 도입**: 하드코딩된 민감정보를 환경변수로 분리
  - 테스트 계정 (username, PIN) 환경변수화
  - APK 파일명, 패키지 ID (resource-id prefix) 환경변수화
  - Appium 서버 설정 (host, port) 환경변수화
- **`.env` 파일 기반 설정**: `python-dotenv` 패키지 활용
- **`.env.example` 템플릿 파일 추가**: 새 환경 설정 시 참고용
- **`.gitignore` 업데이트**: `.env` 파일 제외 규칙 추가 (민감정보 보호)

환경변수 목록:
| 변수명 | 설명 | 필수 |
|--------|------|------|
| `STG_ID` / `STG_PW` | Staging 테스트 계정 | O |
| `LIVE_ID` / `LIVE_PW` | Live 테스트 계정 | O |
| `GME_RESOURCE_ID_PREFIX` | 앱 패키지의 resource-id 접두사 | O |
| `STG_APK` / `LIVE_APK` | APK 파일명 (Staging/Live) | O |
| `APPIUM_HOST` | Appium 서버 호스트 | X |
| `APPIUM_PORT` | Appium 서버 포트 | X |
| `ANDROID_UDID` | 실물 디바이스 시리얼 | X |

사용법:
```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env

# .env 파일 편집 후 테스트 실행
./shell/run-app.sh --gme1_test
```

변경 파일:
- [.env.example](.env.example) (신규)
- [.gitignore](.gitignore)
- [requirements.txt](requirements.txt) - `python-dotenv` 추가
- [config/capabilities.py](config/capabilities.py)
- [tests/android/gme1_test.py](tests/android/gme1_test.py)
- [tests/android/test_01.py](tests/android/test_01.py)
- [tests/android/basic_01_test.py](tests/android/basic_01_test.py)
- [tests/android/xml_test.py](tests/android/xml_test.py)
- [utils/auth.py](utils/auth.py)
- [utils/initial_screens.py](utils/initial_screens.py)

---

## 2026-01-28

### README 문서 구조 개선

- **Overview 섹션 추가**: 프로젝트 목적 및 개요 설명
- **Tech Stack 섹션 추가**: 사용 기술 스택 정리
- **Quick Start 가이드 추가**: 빠른 시작을 위한 단계별 안내
- **문제 해결 섹션 개선**: 테이블 형태로 정리하여 가독성 향상
- **전체 문서 구조 재배치**: 논리적 흐름에 맞게 섹션 순서 변경

변경 파일:
- [README.md](README.md)

---

### UI Dump 민감정보 자동 마스킹 기능 추가

- **자동 마스킹 기능 구현**: XML 캡처 시 개인정보 자동 마스킹
  - 전화번호: `010-1234-5678` → `010-****-****`, `01012345678` → `010********`
  - 이메일: `user@gmail.com` → `u***@g***.com`
  - 생년월일: `1990-05-15` → `****-**-**`, `19900515` → `********`
- **모든 캡처 모드에 적용**: 단일/이름 지정/인터랙티브/Watch 모드
- **기존 덤프 일괄 마스킹 옵션**: `--mask-existing` 플래그 추가
- **기존 XML 파일 5개 마스킹 처리**

사용법:
```bash
# 새 캡처 (자동 마스킹)
python tools/ui_dump.py -w

# 기존 파일 마스킹
python tools/ui_dump.py --mask-existing
```

변경 파일:
- [tools/ui_dump.py](tools/ui_dump.py)
- [docs/UI_DUMP_GUIDE.md](docs/UI_DUMP_GUIDE.md)
- ui_dumps/260123_1254/*.xml (5개 파일 마스킹)
- ui_dumps/261022_132638/20260122_132631_006.xml

---

## 2026-01-27

### APK별 실행 스크립트 추가

- **run-stg.sh / run-live.sh 생성**: Staging/Live APK 전용 실행 스크립트
  - 경로: `shell/run-stg.sh`, `shell/run-live.sh`
  - 기존 `run-app.sh`를 `--app` 옵션과 함께 호출하는 래퍼 스크립트
- **run-app.sh에 `--app` 옵션 추가**: APK/IPA 파일 경로 지정 가능
- **MINGW 경로 변환 로직 추가**: `cygpath -w`로 Windows 경로 자동 변환

사용법:
```bash
./shell/run-stg.sh --basic_01_test      # Staging APK로 테스트
./shell/run-live.sh --basic_01_test     # Live APK로 테스트
./shell/run-app.sh --app apk/custom.apk # 직접 APK 지정
```

변경 파일:
- [shell/run-stg.sh](shell/run-stg.sh) (신규)
- [shell/run-live.sh](shell/run-live.sh) (신규)
- [shell/run-app.sh](shell/run-app.sh)

---

### Allure 대시보드 UI 개선

- **Timestamp 형식 개선**: 날짜/시간 분리 표시
  - 기존: `20260127_153847` (단일 행)
  - 변경: `2026-01-27` + `15:38:47` (2행, 시간은 작은 글씨)
  - `formatTimestamp()` JavaScript 함수 추가
- **테이블 정렬 개선**:
  - 기본: 모든 컬럼 가운데 정렬
  - 예외: Timestamp, Device/Tests, Branch/Commit 컬럼은 좌측 정렬 (가독성 향상)

변경 파일:

- [tools/update_dashboard.py](tools/update_dashboard.py)

---

## 2026-01-26

### Allure 리포트 서버 간편 실행 (`tools/serve.py` 신규)

- 프로젝트 루트에서 `python tools/serve.py` 한 줄로 대시보드 서버 실행
- 브라우저 자동 오픈, Enter 키로 서버 종료 (Windows Ctrl+C 문제 해결)
- 옵션: `--port`, `--latest`, `--no-open`

### Allure 대시보드 레이아웃 개선

- **컬럼 구조 변경**: 역할 분리로 정보 중복 제거
  - `Device / Tests`: 디바이스명 + Behaviors 목록 (테스트 내용 중심)
  - `Branch / Commit`: 브랜치 @ 커밋해시 + 커밋 메시지 (Git 정보 중심)
- commit 메시지 35자 truncate 처리
- 컬럼 너비 최적화, 헤더 이름 변경
- 커밋 메시지 없을 시 `(no message)` 표시
- **Clear 버튼 추가**: Result/Date 필터 한번에 초기화

### Allure 대시보드 데이터 파싱 수정

- environment.json 파싱: `value` → `values[0]` (Allure 형식 대응)
- Suites 이름에서 deviceName 표시: `tests.android` → `Android Emulator`
- 불필요 문구 삭제 ("runs.json 기반..." 안내문)

### Result 판단 로직 개선

- 우선순위 기반 판단: **Failed > Passed > Broken > Skip**
- 필터 옵션 추가: BROKEN, SKIP
- 각 상태별 색상 표시

| 조건 | Result | 색상 |
|------|--------|------|
| Failed > 0 | FAIL | 빨강 |
| Passed > 0 | PASS | 초록 |
| Broken > 0 | BROKEN | 노랑 |
| Skipped > 0 | SKIP | 회색 |

### 플랫폼/앱 버전 표시 보강

- Android `platformVersion`이 비어있으면 adb에서 자동 수집하여 환경 정보에 기록
- OS 버전에 플랫폼명 접두사 자동 추가: `14` → `Android 14`, `17.0` → `iOS 17.0`
- 대시보드 `Device / Tests`에 OS 버전과 App 버전 표시(앱 파일명에서 버전 추출)
- App 경로 처리/정규식 오류 수정으로 렌더링 안정화

### 디바이스 모델명 자동 감지

- adb를 통해 디바이스 모델명 자동 조회
- 조회 우선순위:
  1. **환경변수** (`ANDROID_DEVICE_NAME`)
  2. **AVD 이름** (`ro.boot.qemu.avd_name`) - 에뮬레이터용
  3. **모델명** (`ro.product.model`) - 실물 디바이스용
  4. **기본값** ("Android Emulator")
- 에뮬레이터: `Pixel_6 (Emulator)` 형식으로 표시
- 실물 디바이스: `Pixel 6 (Device)` 형식으로 표시
- adb 연결 불안정 시 재시도 로직 추가 (최대 3회, 1초 간격)

### 실물 디바이스 지원 (환경변수 방식)

- 환경변수로 에뮬레이터/실물 디바이스 선택 가능
- 기본값: 에뮬레이터 (환경변수 없이 실행)
- 실물 디바이스: `ANDROID_UDID` 환경변수 설정

```powershell
# 실물 디바이스
$env:ANDROID_UDID = "XXXXXXXX"
$env:ANDROID_DEVICE_NAME = "Pixel 6"

# 에뮬레이터로 복귀
Remove-Item Env:ANDROID_UDID
```

### 대시보드 버그 수정

- JavaScript 정규식 백슬래시 escape 문제 수정 (`/[\/\\]/`)
- Python 문자열에서 `\\` → `\\\\`로 변경하여 올바른 JavaScript 출력

### 코드 품질 설정 추가

회사/집 환경에서 pull 후 바로 실행되도록 코드 스타일 통일 설정:

- **EditorConfig**: 에디터 설정 통일 (들여쓰기 4칸, LF 줄바꿈)
- **pyproject.toml**: Ruff 린터/포매터 설정
- **Pre-commit hooks**: 커밋 전 자동 검사/수정

```bash
# Pre-commit 설치 및 활성화
pip install pre-commit
pre-commit install

# 전체 파일 검사 (최초 1회)
pre-commit run --all-files
```

### 기타 개선

- `tools/update_dashboard.py` 인덴테이션 수정 (탭/스페이스 혼용 → 4스페이스 통일)

변경 파일:

- [tools/serve.py](tools/serve.py) (신규)
- [tools/update_dashboard.py](tools/update_dashboard.py)
- [config/capabilities.py](config/capabilities.py)
- [conftest.py](conftest.py)
- [.editorconfig](.editorconfig) (신규)
- [pyproject.toml](pyproject.toml) (신규)
- [.pre-commit-config.yaml](.pre-commit-config.yaml) (신규)

## 2026-01-25

### Allure 대시보드 링크/서빙 개선

- 대시보드 링크를 현재 URL 기준으로 동적 계산하여 서버 루트가 달라도 404가 나지 않도록 개선
- 사용 방법: 레포 루트에서 정적 서버 실행 후 `/allure-reports/dashboard/`로 접속

변경 파일:

- [allure-reports/dashboard/index.html](allure-reports/dashboard/index.html)
- [tools/update_dashboard.py](tools/update_dashboard.py)

## 2026-01-22

### 초기 화면 자동 처리(온보딩)

- `noReset=False` 환경에서도 메인/로그인 화면까지 진입하도록 최초 화면(언어/약관 등) 처리 로직 추가
- Android 드라이버 생성 시 자동 실행되며, `@pytest.mark.skip_initial_screens`로 비활성화 가능

변경 파일(주요):

- utils/initial_screens.py
- conftest.py
- pytest.ini

### 테스트 실행/리포트 운영 개선

- 루트 `run-app.sh` 래퍼 추가 및 `shell/run-app.sh` 확장(파일/플랫폼 단축 옵션 등)
- 로컬 Allure 지원 및 실행 편의성 개선(`tools/run_allure.py`, npm scripts)

변경 파일(주요):

- run-app.sh
- shell/run-app.sh
- tools/run_allure.py
- package.json

### ui_dump / xml 테스트 정리

- `ui_dump` 산출물 관리 개선(인터랙티브 모드 세션 폴더화 및 종료 시점 폴더명 확정)
- XML 기반 시나리오 테스트 파일/네이밍 정리(예: `xml_test.py`)
- 테스트 파일 리네임 및 참조 업데이트(예: `test_01.py` → `gme1_test.py`)

변경 파일(주요):

- tools/dump_ui.py
- tests/android/gme1_test.py
- tests/android/xml_test.py
- README.md
- readme_status.md

### 환경/안정성

- Android capability에 `adbExecTimeout` 추가
- 로그인 플로우 관련 수정

변경 파일(주요):

- config/capabilities.py
- tests/android/test_01.py (이후 gme1_test.py로 리네임됨)

### 문서

- 새 PC clone/원샷 설정 가이드 보강(Quick Start/트러블슈팅 포함)

변경 파일:

- docs/README_CLONE.md

## 2026-01-21

### 실행 스크립트/폴더 구조 정리

- 폴더/파일 정리 및 `run-app.sh` 동작 개선(서버/에뮬레이터 실행 포함)

변경 파일(주요):

- shell/run-app.sh
- conftest.py
- README.md

## 2026-01-20

### 경로/문서 생성

- 여러 파일에서 상대 경로 적용(환경 의존성 감소)
- PDF 생성 관련 파일/폴더 정리 및 실행 스크립트 추가

변경 파일(주요):

- config/capabilities.py
- generate_pdf.py
- generate_allure_guide_pdf.py
- shell/run-app.sh

## 2026-01-05

### 프로젝트 초기 구성

- Appium 모바일 테스트 자동화 프로젝트 기본 구조/의존성/샘플 테스트 추가
- APK 파일 Git LFS 적용

변경 파일(주요):

- requirements.txt
- conftest.py
- tests/
- apk/

## 2026-01-23

### UI Dump Watch 모드 추가

- 자동 감지 모드 (`-w`, `--watch`) 구현
  - 화면 변화 자동 감지 (MD5 해시 비교)
  - 화면 이름 자동 추출 (screenTitle, activity명, 첫 번째 텍스트)
  - 파일명 형식: `001_ScreenName.xml`
- Watch 모드 기본 간격을 0.5s → 0.2s로 변경
- 폴더명 형식: `yymmdd_HHMM` (예: 260123_1505)
- 도움말/가이드 문서의 기본값 설명도 0.2s로 일치

변경 파일:

- tools/ui_dump.py
- docs/UI_DUMP_GUIDE.md

### 로그인 모듈화

- 로그인 플로우를 재사용 가능한 모듈로 분리 (`login`, `navigate_to_login_screen`)
- `gme1_test.py`의 로그인 테스트가 모듈을 호출하도록 리팩터링
- 신규 테스트가 로그인 상태에서 시작할 수 있도록 `android_driver_logged_in` 픽스처 추가

추가 적용:

- `basic_01_test.py`에 로그인 모듈/픽스처 혼합 적용
  - 1~2번: `login()` 함수 호출
  - 3~4번: `android_driver_logged_in` 픽스처 사용

변경/추가 파일:

- utils/auth.py (신규)
- tests/android/gme1_test.py
- conftest.py
- tests/android/basic_01_test.py

### Allure 리포트(운영)

- `allure-results` 루트에 남아있던 결과 파일들을 별도 폴더로 묶어 리포트 생성
  - results: allure-results/LEGACY_ROOT_20260123_151056
  - report : allure-reports/LEGACY_ROOT_20260123_151056

참고:

- 위 Allure 관련 내용은 코드 변경이라기보다, 누락 리포트 생성을 위한 운영 작업 기록입니다.

### Allure 리포트(메타데이터/첨부/UX)

- Allure 결과 폴더에 실행 환경/빌드 메타데이터 자동 생성
  - `environment.properties`에 OS/Python/git 정보 포함
  - `executor.json` 생성(buildName에 timestamp|platform|branch@commit 포함)
- 실패(fail) 시 분석용 첨부 강화
  - 스크린샷(PNG), page source(XML/TEXT), capabilities(JSON), Android logcat(TEXT)
- 스킵(skip)/broken(주로 setup/teardown 실패) 케이스에서도(가능한 경우) 스크린샷/비디오(mp4) 첨부
  - 단, 드라이버/녹화 시작 이전에 skip되면 첨부 불가
- 첨부 정책 옵션 추가
  - `--allure-attach=hybrid`(기본): FAIL/SKIP/BROKEN만 첨부
  - `--allure-attach=all`: 성공(PASS)까지 포함해 스크린샷/진단/비디오를 “전부” 첨부
  - `--allure-attach=fail-skip`는 이전 값 호환용
- 비디오 처리 개선
  - 녹화 종료(stop)는 fixture teardown(quit 직전)에서 수행하고, 결과(mp4)를 저장해 두었다가 리포트 단계에서 상태에 따라 첨부
  - 목적: setup/call 단계 실패로 인한 “짧게 끊긴 영상” 최소화 및 첨부 안정성 향상
- 리포트 내 첨부 미디어(스크린샷/비디오) 미리보기만 작게 보이도록 커스텀 CSS 주입
  - 텍스트 크기는 유지하고 첨부 영역만 최대 높이 제한

변경 파일(주요):

- conftest.py
- tools/run_allure.py
- shell/run-app.sh
- docs/README_CLONE.md
- README.md

### Allure 실행 이력 대시보드

- `allure-reports/dashboard/index.html`: 저장된 전체 실행 이력 목록(클릭 시 해당 리포트로 이동)
- `tools/run_allure.py`, `shell/run-app.sh` 실행 시 대시보드(runs.json) 자동 갱신

변경/추가 파일:

- tools/update_dashboard.py (신규)
- tools/run_allure.py
- shell/run-app.sh
- README.md
- docs/ALLURE_REPORT_GUIDE.md

### 리포트 접근성: LATEST 고정 엔트리

- `allure-reports/LATEST/index.html`을 생성하여 최신 리포트로 자동 리다이렉트(정렬/탐색기 설정과 무관)
- `allure-reports/LATEST.txt`는 기존대로 최신 timestamp 기록 유지

변경 파일:

- tools/run_allure.py

### basic_01_test 로그인 방식 통일

- `basic_01_test.py`의 3~4번 테스트도 1~2번과 동일하게 `login()` 모듈 호출 방식으로 통일
  - 3~4번에서 사용하던 `android_driver_logged_in` 픽스처 의존 제거

변경 파일:

- tests/android/basic_01_test.py

### basic_01_test XML 덤프 기반 테스트 추가

- 최신 XML 덤프(260123_1254) 기반 테스트 케이스 추가
  - `test_01_easy_wallet_account_elements` (022_Easy_Wallet_Account.xml)
  - `test_02_history_screen_elements` (023_History.xml)
  - `test_03_edit_info_screen_elements` (027_Edit_Info.xml)
  - `test_04_gmepay_wallet_guide_elements` (030_GMEPay_wallet_guide.xml)
- `find_element_with_fallback` 헬퍼 함수 적용 (Accessibility ID 1순위, Resource ID 2순위)

변경 파일:

- tests/android/basic_01_test.py

### 코딩 가이드라인 문서 생성

- XML 덤프 기반 테스트 작성 규칙 정리
  - 별도 언급 없으면 **최신 dump 폴더** 참조
  - Locator 우선순위: Accessibility ID → Resource ID
  - `find_element_with_fallback` 헬퍼 함수 패턴
- Allure 어노테이션, 파일 명명 규칙, 체크리스트 포함

추가 파일:

- docs/CODING_GUIDELINES.md (신규)

### Allure 리포트/대시보드 공유·열람 방식 논의(보류)

- 로컬/팀 공유 관점에서 “어떻게 열람할지(서빙/호스팅 방식)”를 정리
- 공유 방식 후보: 결과 폴더 공유(로컬에서 열람) 또는 정적 호스팅(GitLab Pages 등)로 배포
- Pages 배포 파이프라인(CI) 구성은 추후 논의

### 보류 항목

- `test_01_app_launch` 테스트 실패 원인 조사 (홀드)
  - 앱 런치 검증 테스트가 실패하였으나, 우선순위에 따라 조사 보류
