# Todo - 해결 필요 항목

> 마지막 업데이트: 2026-02-16

## 진행 중

### explore_app.py Live 앱 실행 및 화면 구조 파악

- **상태**: 스크립트 수정 완료, 실행 미완
- **목표**: Live 앱의 전체 화면/메뉴 구조를 자동 탐색 후 APP_STRUCTURE.md 업데이트
- **실행 명령어**: `USE_LIVE=true /Users/sph/appium/venv/bin/python3 tools/explore_app.py`
- **사전 조건**:
  - Appium 서버 실행 (`appium`)
  - 에뮬레이터에 Live 앱 설치 완료 (v7.14.0)
- **확인 포인트**:
  - `ui_dumps/explore_YYYYMMDD_HHMM/` 폴더에 XML 파일 생성
  - 하단 탭 5개 (Home, History, Card, Event, Profile) 캡처
  - 햄버거 메뉴 8개 항목 캡처
  - 팝업 캡처 파일 (`popup_*.xml`) 확인

### APP_STRUCTURE.md 미확인 화면 업데이트

- **상태**: explore_app.py 실행 결과 대기 중
- **미확인 화면 목록** (10개):
  1. History 탭 메인 + 서브탭 (Overseas, Schedule History, Domestic, Inbound)
  2. Card 탭 메인
  3. Event 탭 메인
  4. Profile 탭 메인 + 각 메뉴 항목
- **완료 기준**: 미확인 → 확인 전환, 각 화면별 resource-id/텍스트 매핑 완료

### 처음 보는 팝업 기록 및 케이스화

- **상태**: 팝업 캡처 기능 구현 완료, 실행 후 분석 필요
- **내용**: explore_app.py가 저장하는 `popup_*.xml` 분석 → APP_STRUCTURE.md에 팝업 케이스 추가
- **참고**: "처음보는 팝업이 있으면 다 기록하고, 해당화면도 케이스로 만들어줘" (사용자 지시)

---

## 다음 단계 (사용자 가이드 수신 후)

### 송금 화면 탐색 (금액 입력까지만)

- **주의**: 실제 결제/송금 액션 절대 금지
- **범위**: Send Money 진입 → 수취인 선택 → 금액 입력 화면 캡처 → 중단
- **참고**: "실제 송금이나 돈을 보내는 액션은 금액 입력하는 액션 정도만 진행해줘" (사용자 지시)

### APP_STRUCTURE.md 기반 자동화 코드 생성

- **조건**: APP_STRUCTURE.md 완성 + 사용자 리뷰 후
- **참고**: "파악된 기록을 보고 수정을 거친후에 가이드를 줄게" (사용자 지시)
- **목표**: Page Object Model 기반 자동화 코드 생성

---

## 알려진 이슈

### 로그인 모듈 테스트 검증

- 지문 인증 화면 처리 코드 동작 확인 필요
- UI 덤프에서 정확한 요소 확인 필요 시 수집

### UiAutomator2 드라이버 설치 경고 (낮은 우선순위)

- `run-app.sh`의 드라이버 체크 로직이 "이미 설치됨"을 "설치 안됨"으로 오인
- 실제 동작에는 문제 없음, 로그에 불필요한 에러 메시지 출력

### UnicodeDecodeError 경고 (낮은 우선순위, Windows 환경)

- Windows 환경에서 한글 UTF-8 처리 문제 (`cp949` 코덱)
- 환경변수 `PYTHONIOENCODING=utf-8` 설정 또는 subprocess `encoding='utf-8'` 명시로 해결 가능

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
