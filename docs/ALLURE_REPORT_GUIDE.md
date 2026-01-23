# Allure Report 사용 가이드 (로컬/CI 공통)

이 문서는 Allure Report 웹 UI(예: `http://127.0.0.1:60703/#`)에서 **각 탭이 의미하는 바**와 **실무에서 빠르게 원인 분석하는 사용 루틴**을 정리합니다.

---

## 1) Allure 리포트가 만들어지는 흐름(How it works 요약)

Allure는 크게 아래 3단계로 동작합니다.

1. **테스트 실행 중 데이터 수집**
   - 프레임워크 어댑터(allure-pytest 등)가 테스트 생명주기(Setup/Call/Teardown)에 걸쳐
     step, 실행 시간, 상태, 첨부(스크린샷/비디오/로그) 등을 결과 폴더에 기록합니다.
   - 기본 결과 폴더는 보통 `allure-results`입니다.

2. **메타데이터 보강(Optional)**
   - `environment.properties`, `executor.json`, `categories.json`, `history/` 같은 추가 파일로
     “환경 정보/실행자/분류 규칙/트렌드”를 리포트에 반영할 수 있습니다.

3. **리포트 생성/열람**
   - `allure generate`로 정적 HTML 리포트를 생성(아카이빙/공유에 적합)
   - `allure open` 또는 `allure serve`로 로컬에서 빠르게 열람

공식 문서 참고: https://allurereport.org/docs/how-it-works/

---

## 1.1) 이 프로젝트에서의 저장 구조(중요)

이 레포는 실행 이력을 남기기 위해 결과/리포트를 타임스탬프 폴더로 보관합니다.

- 결과(raw): `allure-results/YYYYMMDD_HHMMSS/`
- 리포트(html): `allure-reports/YYYYMMDD_HHMMSS/`
- 최신 고정 엔트리: `allure-reports/LATEST/index.html`
- 전체 이력 대시보드: `allure-reports/dashboard/index.html`

`tools/run_allure.py` 또는 `shell/run-app.sh`로 실행하면 위 구조가 자동으로 갱신됩니다.

---

## 2) 상태(Status) 빠른 이해

Allure UI에서 가장 자주 보는 상태 의미는 아래와 같습니다.

- **PASSED**: 테스트가 기대대로 성공
- **FAILED**: 검증(assert) 실패 등 “테스트 로직상 실패”
- **BROKEN**: 주로 예외/환경 문제로 테스트가 정상 수행되지 못함(Setup/Teardown 실패, 세션 끊김, 타임아웃 등)
- **SKIPPED**: 조건에 의해 실행이 건너뜀(pytest skip/marker 등)

실무 팁:
- 실패가 많을 때는 `FAILED`/`BROKEN` 비율이 높아졌는지부터 확인하고,
  `BROKEN`이 많다면 환경/인프라(Appium/디바이스/네트워크) 이슈 가능성을 먼저 봅니다.

---

## 3) 좌측 탭별 기능 요약

### 3.1 Overview (전체 요약)

**목적**: “이번 실행이 전체적으로 건강한가?”를 30초~1분 안에 판단.

주로 확인하는 내용
- Passed/Failed/Broken/Skipped 카운트와 비율
- 트렌드(History가 연결되어 있을 때): 최근 실행 대비 실패 증가/감소
- Environment/Executor 정보: 어떤 OS/디바이스/브랜치/커밋에서 돌렸는지

추천 사용 흐름
- Overview에서 **이상 징후**를 보고 → `Categories` 또는 `Suites`로 내려가 원인 분석.

---

### 3.2 Suites (테스트 구조 탐색)

**목적**: 테스트를 파일/클래스/스위트 구조로 탐색하면서 **개별 테스트를 깊게 분석**.

주로 하는 일
- 실패/깨짐/스킵 케이스 선택
- Steps(Execution)에서 어느 단계에서 멈췄는지 확인
- Attachments(스크린샷/비디오/log/page source 등)로 재현 없이 원인 단서 확보
- History / Retries로 flaky 여부(재시도에서만 통과하는지) 확인

실무에서 가장 자주 클릭하는 화면입니다.

---

### 3.3 Categories (실패 유형별 분류)

**목적**: 실패를 “유형별”로 묶어서 원인 파악 시간을 단축.

동작 방식
- 스택트레이스/메시지에 정규식 룰을 적용해 카테고리로 자동 분류합니다.
  (예: UI 동기화 타임아웃, 요소 탐색 실패, 서버 연결 실패 등)

추천 사용 흐름
- 실패가 많을 때 **가장 큰 카테고리부터** 해결하면 효율이 좋습니다.

---

### 3.4 Graphs (차트/분포)

**목적**: 결과를 차트로 요약하여 품질 패턴을 빠르게 확인.

자주 보는 포인트(구성은 리포트 버전에 따라 일부 다를 수 있음)
- Status 분포: 실패/스킵 비율 변화
- Duration 분포: 느린 테스트가 늘었는지
- Severity 분포: 중요도 라벨 기반(팀이 라벨을 잘 쓰고 있을 때 유용)

추천 사용 흐름
- “느려진 구간”이나 “특정 중요도에서 실패가 몰림” 같은 운영 관점 분석에 좋습니다.

---

### 3.5 Timeline (시간축)

**목적**: 테스트가 시간축에서 어떻게 실행됐는지 시각화.

유용한 상황
- 병렬 실행 시 특정 시간대에 실패가 몰리는지
- 특정 구간에서 대기/응답 지연이 집중되는지

---

### 3.6 Behaviors (기능 라벨 기반)

**목적**: `feature`/`story`(또는 epic 등) 라벨 기준으로 기능 단위 품질을 확인.

추천 사용 흐름
- “기능별 품질 현황”을 보고할 때 Suites보다 직관적인 경우가 많습니다.

---

### 3.7 Packages (코드 단위 그룹)

**목적**: 테스트를 패키지/모듈/클래스 단위로 묶어 코드 소유권 관점에서 확인.

추천 사용 흐름
- “어느 모듈이 가장 많이 깨지나?” 같은 담당 범위 중심 분석에 적합.

---

## 4) 개별 테스트 상세 화면: 꼭 알아야 할 것

### 4.1 Execution / Steps
- 테스트가 어떤 순서로 수행됐는지, 어느 Step에서 실패/스킵됐는지 확인합니다.
- 모바일 테스트는 UI 동기화 문제로 “실패 지점”이 중요하므로 Step 단위 기록이 특히 유용합니다.

### 4.2 Attachments
주로 첨부되는 자료 예시
- 스크린샷(PNG)
- 비디오(mp4)
- page source(XML/TEXT)
- logcat(TEXT)
- capabilities(JSON)

이 프로젝트에서 첨부가 붙는 대표 케이스
- **기본(hybrid)**: FAIL/SKIP/BROKEN에만 첨부(성공은 첨부하지 않음)
- **다 붙이기(all)**: 성공(PASS)까지 포함해 최대한 첨부

옵션
- `--allure-attach=hybrid` (기본)
- `--allure-attach=all`

실무 팁
- 실패 직후 화면(스크린샷/비디오) + page source + 로그 조합이면 재현 없이도 원인 추정이 가능한 경우가 많습니다.

### 4.3 History / Retries
- History: 이전 실행들에서 같은 테스트가 어땠는지
- Retries: 재시도 내역이 있으면 “처음 실패 → 재시도 성공” 같은 flaky 패턴을 확인 가능

---

## 5) 실무용 ‘30초 분석 루틴’ 추천

1. **Overview**: Failed/Broken이 급증했는지 확인
2. **Categories**: 가장 큰 실패 카테고리부터 확인(환경/동기화/요소 탐색)
3. **Suites → 실패 테스트 선택**
4. **Steps**에서 실패 위치 확인
5. **Attachments**에서 스크린샷/비디오/log/page source를 순서대로 확인
6. flaky 의심이면 **Retries/History**로 “재시도 성공 패턴” 확인

---

## 6) 팁: 로컬에서 최신 리포트 빠르게 열기

이 프로젝트는 최신 리포트 접근성을 위해 아래 파일을 사용합니다.

- `allure-reports/LATEST.txt`: 최신 실행 timestamp 기록
- `allure-reports/LATEST/index.html`: 최신 리포트로 리다이렉트(정렬과 무관)

추가 팁
- 특정 실행 리포트는 `allure-reports/<timestamp>/index.html`을 열면 됩니다.
- 브라우저 보안 정책 때문에, 대시보드는 `file://`로 열면 `runs.json` 로딩이 막힐 수 있어 **간단 서버로 여는 것을 권장**합니다.

추가로, 전체 실행 이력을 한 화면에서 보고 싶은 경우 아래 대시보드를 사용합니다.

- `allure-reports/dashboard/index.html`: 전체 실행 이력 목록(클릭 시 해당 리포트로 이동)

대시보드는 `runs.json`을 읽어 렌더링하므로, 로컬에서 아래처럼 간단 서버로 여는 것을 권장합니다.

```bash
python -m http.server 8000
```

브라우저 접속:
- `http://127.0.0.1:8000/allure-reports/dashboard/`

---

## 7) 자주 겪는 질문(FAQ)

### Q1. 스크린샷/비디오가 너무 커서 텍스트까지 줄여야 해요.
- 권장: 브라우저 줌을 낮추지 말고, 첨부 미디어 미리보기 크기만 제한하는 CSS 후처리를 적용합니다.

참고(이 레포 적용 내용)
- 생성된 리포트의 `index.html`에 `custom.css`가 주입되어 첨부 미리보기만 줄어듭니다.

### Q2. SKIPPED인데도 스크린샷/비디오가 없어요.
- 테스트가 드라이버/녹화 시작 전에 skip되면(예: collection/fixture 진입 전) 캡처할 대상이 없어 첨부가 불가능합니다.

### Q4. BROKEN인데 비디오가 안 붙어요.
- BROKEN은 주로 setup/teardown 실패로 발생하며, 드라이버가 정상 생성되기 전에 실패하면 녹화/첨부 자체가 불가능합니다.
- 드라이버가 생성되고 `--record-video`가 켜진 상태에서 실패했다면, teardown 시점에 저장된 녹화 파일이 Allure에 첨부됩니다.

### Q3. “다 붙이기” / “하이브리드”가 뭐예요?
- `--allure-attach=hybrid`(기본): FAIL/SKIP/BROKEN만 첨부(성공은 첨부하지 않음)
- `--allure-attach=all`: 성공(PASS)까지 포함해 최대한 첨부

---

## 부록) 어노테이션/라벨(권장)

팀에서 아래 라벨을 꾸준히 쓰면 Behaviors/Graphs가 훨씬 유용해집니다.
- `@allure.feature("..." )`
- `@allure.story("..." )`
- `@allure.severity(...)`
- `@allure.title("..." )`
- `@allure.description("..." )`
- `with allure.step("..." ):`
