# Change Notes

## 2026-04-16

### .env.example 항목 추가
- `TEAMS_WEBHOOK_URL`: Teams 채널 Incoming Webhook URL (선택)
- `DASHBOARD_API_URL`: 대시보드 API URL (트리거 폴링용, 선택)

### tools/ 신규 스크립트
- `tools/teams_notify.py`: Teams Webhook 알림 스크립트
- `tools/trigger_listener.py`: 대시보드 트리거 폴링 리스너

---

## 2026-04-03

### Local Transfer 테스트 Livetest 환경 전체 통과
- Livetest APK (7.15.0) + Pixel_6 에뮬레이터(4GB RAM)에서 10/10 PASSED
- Staging APK는 로그인 후 팝업 문제로 실패 → Livetest로 전환하여 해결
- 대시보드 업로드 완료 (첨부파일 10개 포함)

### capabilities.py 에뮬레이터 타임아웃 추가
- `appWaitDuration`: 60초 (기본 20초, 에뮬레이터 느린 경우 대비)
- `uiautomator2ServerLaunchTimeout`: 60초

### stdout 첨부파일 이름에 테스트명 포함
- `upload_to_dashboard.py`의 `_collect_attachments()`에서 `stdout — 테스트케이스명`으로 변경
- 기존 9개 리포트 재업로드 완료

---

## 2026-03-31

### iOS 앱 정보 추출 기능 추가
- `conftest.py`에 `_safe_get_ios_app_info()` 함수 추가
- iOS `.app` 번들의 `Info.plist`에서 앱 이름(`CFBundleDisplayName`/`CFBundleName`), 버전(`CFBundleShortVersionString`) 추출
- `pytest_configure`에서 플랫폼별 분기: iOS / Android
- 대시보드 ENVIRONMENT 영역에 iOS 테스트 시에도 APP 항목 표시

### APK 실제 바이너리 반영 + GitLab LFS 해결
- `apk/stage/`, `apk/live/`, `apk/livetest/` 폴더 LFS 포인터 → 실제 APK로 교체
- 7.15.0 APK 3개 적용 (stg 170MB, livetest 170MB, live 130MB)
- GitLab LFS 푸시 이슈 해결

### 에뮬레이터 RAM 부족 이슈 해결
- 170MB APK 실행 시 메모리 부족 원인 파악
- 에뮬레이터 RAM 2GB → 4GB로 증설하여 해결

### Allure Dashboard UI 개선
- 상세 페이지 상태 카드 세로 중앙 정렬
- glass 패널 입체감 강화 (테두리 밝기 2배 + 바깥 그림자/내부 하이라이트)

---

## 2026-03-30

### AI 실패 분석 기능
- `upload_to_dashboard.py`에 AI 기반 실패 케이스 자동 분석 기능 추가
- 실패/broken 시 에러 메시지 + 스크린샷 + page_source를 외부 AI API에 전송 → 분석 결과를 description에 저장
- 대시보드 AllCaseList에서 AI Analysis 자동 표시
- AI Gateway / 직접 API / 로컬 분석 3가지 방식 지원

### 대시보드 메인 UI 개선
- StatsBar Pass Rate 2단 표시 (Overall 전체 이력 + Latest 최근 실행)
- Latest 바 클릭 시 최근 실행 상세 페이지로 이동
- OverviewCharts 데이터 없을 때 No Data 표시
- Filters Clear 버튼 빨간색

---

## 2026-03-29

### Local Transfer 자동화 테스트 작성
- `tests/android/local_transfer_test.py` 신규 생성 (10개 테스트 케이스)
- 시나리오: 언어 설정 → 로그인 → Local Transfer 진입 → 계좌/은행/금액 입력 → 확인 → PIN 입력 → 성공 확인 → Transaction Details → History 이력 검증
- 클래스 단위 드라이버 공유 (로그인 1회만 수행)
- History 검증: Transaction ID 매칭 + 입금 시간 10분 범위 검증
- 구버전 스크립트(`test_01.py`, `xml_test.py`) → `tests/android/archive/` 폴더로 격리

### Allure Dashboard 상세 페이지 UI 대폭 개선
- Test Cases: 펼치기/상세 기능 통합 (에러 메시지, 스택 트레이스, 스텝, 스크린샷, 비디오)
- Test Cases: fullName 기준 실행 순서 정렬, severity 아이콘(🔴🟡🟢) 적용
- Environment 정리: OS(platform+version), APP(name+version), ENV, TEST SCRIPT
- 섹션 순서: Environment → Test Cases → Suites/Actions → Artifacts → Git Info → Remark

### conftest.py 앱 정보 자동 추출
- `aapt dump badging`으로 APK에서 앱 이름/버전 자동 추출
- `appName`, `appVersion`, `appEnv`, `testScript` 필드 environment.properties에 추가

---

## 2026-03-08

### Allure Dashboard 차트 시각화
- recharts 기반 Overview 차트 추가 (Status 도넛, Trend Area, Platform 도넛, Pass Rate Bar)
- 차트 슬라이스 클릭 → URL 파라미터 필터 토글 (status/platform)
- 도넛 차트: 전체 비율 유지 + 선택 슬라이스 하이라이트 (비선택 opacity 0.15)
- 다크/라이트 모드 토글 (localStorage 저장, FOUC 방지)
- CSS 변수 전면 적용

---

## 2026-02-25

### Windows 호환성 개선 + 반응형 대시보드
- Windows cp949 UnicodeDecodeError 수정 (UTF-8 환경변수 + reconfigure)
- Vercel 대시보드 반응형 변환 (StatsBar, Filters, RunsTable, 헤더)
- Status 필터 추가 (StatsBar 카드 클릭 + Filters 버튼 그룹)
- BEHAVIORS → ACTIONS 이름 변경
- Environment 카드 라벨 SNAKE_CASE 변환
- 로컬 대시보드 반응형 변환

---

## 2026-02-21

### Vercel Blob 연동
- 첨부파일 (스크린샷/비디오/로그) Vercel Blob 저장
- 상세 페이지 첨부파일 뷰어 (이미지 미리보기, 비디오 재생, 텍스트 뷰어)
- GitHub 연동 자동 배포 활성화
- iOS 테스트 + 대시보드 업로드 검증

---

## 2026-02-19

### explore_app.py 자동 화면 탐색
- Card 3rd Depth 자동 캡처 (8/12 성공)
- 인터랙티브 요소 분류, ViewPager 자동 감지
- 팝업 자동 처리 (In-App Banner, Renew Auto Debit 등)

---

## 2026-02-17

### Allure Dashboard 초기 구축
- Next.js 15 + TypeScript + Tailwind CSS v4 + Prisma 6
- PostgreSQL (Vercel Postgres / Neon) 데이터베이스
- Vercel 배포
- 테스트 실행 이력 + 상세 보기
- 파일 기반 첨부파일 (스크린샷, 비디오, 로그)

---

## 2026-02-04

### 환경변수 구조 개선
- `STG_ID`/`STG_PW`, `LIVE_ID`/`LIVE_PW`로 계정 분리
- APK 파일명 환경 접두사 적용
- 관련 파일 일괄 업데이트

---

## 2026-01-28

### Mobile Test Automation Framework 초기 구축
- Appium + Python 프레임워크
- Android / iOS 동시 지원
- Page Object Model 구조
- Allure 리포트 연동
- 초기 테스트 스크립트 (로그인, 네비게이션)
