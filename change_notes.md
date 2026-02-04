# Change Notes

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
