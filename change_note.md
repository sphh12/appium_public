# Change Notes

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
  - report  : allure-reports/LEGACY_ROOT_20260123_151056

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
