# Todo - 해결 필요 항목

> 마지막 업데이트: 2026-02-24

---

## 진행 중

### 3rd Depth 미캡처 화면

- **Card Features 미해결** (4개):
  - c2 (`btn_gme_wallet_transfer`): Home 전용 ID, Card 화면에서 올바른 ID 확인 필요
  - c3 (`btn_gme_wallet_deposit`): Home 전용 ID, Card 화면에서 올바른 ID 확인 필요
  - c11 (`performance_card_layout`): DOM 미존재, 앱 상태 의존 (동적 로딩)
  - c12 (`rlGlobalQRScanView`): DOM 미존재, 앱 상태 의존 (동적 로딩)
- **Card Management** (4개): c13~c16 미착수
- **Settings** (4개): s1~s4 미착수
- **참고**: `python tools/explore_app.py card_3rd` 으로 Card 3rd Depth만 실행 가능

### APP_STRUCTURE.md 미확인 화면 업데이트

- **상태**: explore_app.py 실행 결과 기반 업데이트 필요
- **완료 기준**: 미확인 → 확인 전환, 각 화면별 resource-id/텍스트 매핑 완료

### 처음 보는 팝업 기록 및 케이스화

- **상태**: 팝업 캡처 기능 구현 완료, 실행 후 분석 필요
- **내용**: explore_app.py가 저장하는 `popup_*.xml` 분석 → APP_STRUCTURE.md에 팝업 케이스 추가

---

## 다음 단계 (사용자 가이드 수신 후)

### 송금 화면 탐색 (금액 입력까지만)

- **주의**: 실제 결제/송금 액션 절대 금지
- **범위**: Send Money 진입 → 수취인 선택 → 금액 입력 화면 캡처 → 중단

### APP_STRUCTURE.md 기반 자동화 코드 생성

- **조건**: APP_STRUCTURE.md 완성 + 사용자 리뷰 후
- **목표**: Page Object Model 기반 자동화 코드 생성

---

## 알려진 이슈

### 로그인 모듈 테스트 검증

- 지문 인증 화면 처리 코드 동작 확인 필요
- UI 덤프에서 정확한 요소 확인 필요 시 수집

### c10 ViewPager "+" 버튼 ID 미확인

- ViewPager 2페이지 캡처 성공했으나, 카드 추가 "+" 버튼 ID 미식별
- 캡처 XML에서 확인 필요

### UiAutomator2 드라이버 설치 경고 (낮은 우선순위)

- `run-app.sh`의 드라이버 체크 로직이 "이미 설치됨"을 "설치 안됨"으로 오인
- 실제 동작에는 문제 없음

### UnicodeDecodeError 경고 (낮은 우선순위, Windows 환경)

- Windows 환경에서 한글 UTF-8 처리 문제 (`cp949` 코덱)
- 환경변수 `PYTHONIOENCODING=utf-8` 설정으로 해결 가능

---

## 참고사항

### 앱 환경
| 항목 | 값 |
|------|-----|
| Live 앱 | `com.gmeremit.online.gmeremittance_native` (v7.14.0) |
| Staging 앱 | `com.gmeremit.online.gmeremittance_native.stag` (v7.13.0) |
| 현재 사용 | **Live** (Staging 팝업 과다로 전환) |
| 에뮬레이터 | emulator-5554 |

### 알려진 팝업
| 팝업 | 처리 방법 | 처리 위치 |
|------|-----------|-----------|
| Renew Auto Debit | btn_okay → iv_back | explore_app.py |
| In-App Banner | imgvCross (X) / btnTwo (Cancel) | explore_app.py |
| 보이스피싱 경고 | check_customer → 확인 버튼 | auth.py |
| 지문 인증 설정 | txt_pennytest_msg (나중에) | auth.py |

### explore_app.py 실행 방법
| 명령어 | 설명 |
|--------|------|
| `USE_LIVE=true python tools/explore_app.py` | 전체 탐색 |
| `python tools/explore_app.py card_3rd` | Card 3rd Depth만 |
| `python tools/explore_app.py home` | Home 탭만 |

---

## 완료 아카이브

### 2026-02-23
- [x] docs/PUBLIC_PUSH_GUIDE.md 신규 생성 (Public 저장소 푸시 규칙 및 워크플로우)
- [x] `public` remote 추가 (appium_public)

### 2026-02-22
- [x] Claude Code 상태줄 설정 (Windows 환경, jq 없이 동작)
- [x] 문서 업데이트 (README.md 전면 재작성, ALLURE_REPORT_GUIDE.md, CLAUDE.md)
- [x] run_allure.py 자동 패키지 설치 기능 추가
- [x] run-app.sh 대시보드 자동 업로드 (STEP 5) 추가
- [x] upload_to_dashboard.py .env 자동 로드 수정
- [x] upload_to_dashboard.py Blob 스토리지 자동 정리 기능 (80% 초과 시 자동 삭제)
- [x] 워크플로우 개선 (Git Push md 업데이트 규칙, 브리핑, 중간 기록 규칙)
- [x] .claude/ Git 추적 제외 설정
- [x] allure-dashboard CLAUDE.md 생성

### 2026-02-21
- [x] Vercel Blob 연동 (스크린샷/비디오/로그 첨부파일 저장)
- [x] 상세 페이지에서 첨부파일 뷰어 구현 (이미지 미리보기, 비디오 재생, 텍스트 뷰어)
- [x] allure-dashboard GitHub 연동 → push 시 자동 배포 활성화
- [x] `--upload` 옵션 기본 활성화 + 프로덕션 URL 기본값 설정
- [x] iOS 테스트 실행 + 대시보드 업로드 확인
- [x] 빈 실행 이력 삭제 (DELETE API 추가)

### 2026-02-19
- [x] explore_app.py Card 3rd Depth 자동 캡처 (8/12 성공)
- [x] explore_app.py 검증 기능 추가 (인터랙티브 요소 분류, ViewPager 자동 감지)
