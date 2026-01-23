# 진행 상황 (2026-01-22)

## 완료된 작업

- `noReset=False` 환경에서도 테스트가 항상 메인/로그인 화면으로 진입하도록 초기 화면 자동 처리 로직을 추가
  - 공통 처리: `utils/initial_screens.py`
  - 적용 위치: `conftest.py`의 Android 드라이버 생성 fixture에서 자동 실행
  - 옵트아웃: `@pytest.mark.skip_initial_screens`

- 테스트 실행 편의성 개선
  - 루트 래퍼 스크립트 추가: `run-app.sh` (내부적으로 `shell/run-app.sh` 호출)
  - `shell/run-app.sh` 기능 확장
    - `--files "<paths...>"`: 지정한 파일을 순서대로 실행
    - `--<file>`: `tests/<platform>/<file>.py` 단축 실행(예: `--xml_test`, `--gme1_test`)
    - 이전 옵션 호환: `--test_xml` → `xml_test`로 자동 매핑

- 파일 리네임 및 참조 정리
  - `tests/android/test_01.py` → `tests/android/gme1_test.py`
  - `tests/android/test_xml.py` → `tests/android/xml_test.py`
  - 예시/스크립트/도구/패키지 스크립트 내 경로 참조 업데이트

- `ui_dump` 산출물 정리 개선
  - 인터랙티브 덤프(`python tools/ui_dump.py -i`) 시
    - 실행 시작~종료까지를 한 세션 폴더로 묶음
    - 종료 시점에 폴더명을 `YYYYMMDD_HHMMSS`(종료시간)로 확정

- pytest 설정 보강
  - `pytest.ini`: `*_test.py` 파일도 수집하도록 확장
  - `skip_initial_screens` 마커 등록

## 남은 작업(TODO)

- (선택) `ui_dump.py`의 단발 캡처(`python tools/ui_dump.py <name>`)도 세션 폴더 방식으로 정리할지 결정
- Allure 리포트/가이드 문서(생성 PDF 포함) 최신 실행 예시 검수

## 빠른 실행 예시

- 단일 파일 실행
  - `./run-app.sh --gme1_test`
  - `./run-app.sh --xml_test`

- 여러 파일을 지정한 순서대로 실행
  - `./run-app.sh --files "tests/android/gme1_test.py tests/android/xml_test.py"`

- 플랫폼 폴더 전체 실행
  - `./run-app.sh --all`
