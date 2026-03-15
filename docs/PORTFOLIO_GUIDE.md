# 포트폴리오용 Public 저장소 가이드

> 이 문서는 현재 private Appium 프로젝트를 포트폴리오용 public 저장소로 공개할 때의 기준과 절차를 정리합니다.

---

## 1. 기본 원칙

```
공개 기준: "내 역량을 보여주되, 민감정보는 절대 노출하지 않는다"
```

- 현재 private 저장소를 그대로 public으로 전환하지 않는다
- **별도 public 저장소를 생성**하여 민감정보를 제거한 버전만 공개한다
- git history에 민감정보가 남지 않도록 주의한다

---

## 2. 공개/비공개 파일 분류

### 2.1 공개 대상 (역량 증명용)

| 파일/폴더 | 공개 이유 | 공개 시 주의사항 |
|-----------|-----------|-----------------|
| `conftest.py` | fixture 설계, 드라이버 관리, 리포팅 Hook | 앱 패키지명 일반화 |
| `config/capabilities.py` | 환경별 설정 자동 전환 구조 | 실제 패키지명 → 예시로 변경 |
| `utils/auth.py` | 로그인 모듈, 보안 키보드 처리 | 계정 기본값 제거 확인 |
| `utils/initial_screens.py` | 초기 화면 자동 처리 로직 | 그대로 공개 가능 |
| `utils/language.py` | 다국어 언어 설정 모듈 | 그대로 공개 가능 |
| `utils/helpers.py` | 유틸리티 함수 모음 | 그대로 공개 가능 |
| `tests/android/` | 테스트 시나리오 작성 능력 | resource-id 접두사 일반화 |
| `tests/ios/` | iOS 테스트 코드 | 그대로 공개 가능 |
| `tools/ui_dump.py` | UI 덤프 도구 자체 개발 능력 | 그대로 공개 가능 |
| `tools/ui_dump_ios.py` | iOS UI 덤프 도구 | 그대로 공개 가능 |
| `tools/explore_app.py` | 앱 자동 탐색 스크립트 | 앱 패키지명 일반화 |
| `tools/run_allure.py` | Allure 리포트 자동화 | 대시보드 URL 제거 |
| `tools/export_summary.py` | 경량 HTML 요약 Export | 그대로 공개 가능 |
| `tools/upload_to_dashboard.py` | 대시보드 업로드 도구 | API URL/토큰 참조 제거 |
| `tools/serve.py` | 로컬 HTTP 서버 | 그대로 공개 가능 |
| `shell/run-app.sh` | 5단계 파이프라인 자동화 | 그대로 공개 가능 |
| `shell/run-aos.sh` | Android 래퍼 스크립트 | 그대로 공개 가능 |
| `shell/run-ios.sh` | iOS 래퍼 스크립트 | 그대로 공개 가능 |
| `pages/base_page.py` | Page Object Model 베이스 | 그대로 공개 가능 |
| `pages/sample_page.py` | POM 샘플 구현 | 그대로 공개 가능 |
| `docs/` | 문서화 능력 증명 | 내부 업무 관련 내용 제거 |
| `.env.example` | 설정 구조 안내 | 실제 값 없는지 재확인 |
| `README.md` | 프로젝트 소개 | 포트폴리오용으로 재작성 |
| `.gitignore` | 프로젝트 구성 | 그대로 공개 가능 |
| `.editorconfig` | 코드 스타일 설정 | 그대로 공개 가능 |
| `pytest.ini` | pytest 설정 | 그대로 공개 가능 |
| `pyproject.toml` | 프로젝트 메타데이터 | 그대로 공개 가능 |
| `requirements.txt` | 의존성 목록 | 그대로 공개 가능 |
| `package.json` | Node.js 의존성 | 그대로 공개 가능 |

### 2.2 절대 비공개 (민감정보 포함)

| 파일/폴더 | 비공개 이유 |
|-----------|------------|
| `.env` | 실제 계정, 비밀번호, API 토큰 |
| `apk/` | 회사 앱 바이너리 (저작권, 리버스 엔지니어링 위험) |
| `ui_dumps/` | 앱 내부 UI 구조 + 개인정보(전화번호, 이메일) 포함 가능 |
| `allure-results/` | 테스트 결과에 스크린샷, logcat 등 민감정보 포함 |
| `allure-reports/` | HTML 리포트에 앱 화면 캡처 포함 |
| (내부 문서들) | 내부 업무 히스토리, 워크플로우, Git 규칙 등 |
| `.claude/` | Claude Code 설정, 메모리 파일 |
| `.gitattributes` | LFS 설정 (APK 관련) |

### 2.3 선택적 공개 (판단 필요)

| 파일 | 공개 시 장점 | 공개 시 위험 | 권장 |
|------|-------------|-------------|------|
| `docs/APP_STRUCTURE_stg.md` | 앱 분석 능력 증명 | 앱 내부 구조 노출 | 일반화 후 공개 또는 비공개 |
| `docs/feature_list_live.md` | 테스트 커버리지 증명 | 앱 기능 목록 노출 | 비공개 |
| 스크린샷/동영상 | 시각적 데모 효과 | 앱 UI 노출 | 마스킹 후 선택적 공개 |

---

## 3. 일반화 작업 체크리스트

public 저장소에 올리기 전에 아래 항목을 모두 확인합니다.

### 3.1 앱 정보 일반화

- [ ] 패키지명 변경
  - `com.example.remittance.stag` → `com.example.app.stag`
  - `com.example.remittance` → `com.example.app`
  - `com.example.remittance.livetest` → `com.example.app.livetest`
- [ ] resource-id 접두사 변경
  - `com.example.remittance.stag:id` → `com.example.app.stag:id`
  - `com.example.remittance:id` → `com.example.app:id`
  - `com.example.remittance.livetest:id` → `com.example.app.livetest:id`
- [ ] 앱 이름 변경: `Sample Remit` → `Sample Remittance App` 등
- [ ] Activity 이름 변경: `.SplashActivity` → `.SplashActivity` 등

### 3.2 계정 정보 제거

- [ ] 코드 내 기본값에 실제 계정이 없는지 확인
- [ ] `.env.example`에 실제 값이 없는지 확인 (`your_username` 등 플레이스홀더 사용)
- [ ] 주석에 실제 계정 정보가 없는지 확인

### 3.3 URL/토큰 제거

- [ ] Vercel 대시보드 URL 제거 또는 일반화
- [ ] `BLOB_READ_WRITE_TOKEN` 참조는 유지하되 실제 값 없는지 확인
- [ ] GitHub/GitLab remote URL 제거

### 3.4 문서 정리

- [ ] `README.md`를 포트폴리오용으로 재작성 (섹션 4 참조)
- [ ] `docs/` 내 회사 앱 구조 관련 문서 제거 또는 일반화
- [ ] 문서 내 회사명, 앱명, 내부 URL 검색 후 제거

### 3.5 Git History 확인

- [ ] `git log --all --oneline`으로 커밋 메시지에 민감정보 없는지 확인
- [ ] 이전 커밋에 `.env` 파일이 포함된 적 없는지 확인
- [ ] 필요 시 새 저장소에 **초기 커밋**으로 클린 버전만 push

---

## 4. 포트폴리오용 README.md 작성 가이드

public 저장소의 README는 채용 담당자/면접관이 가장 먼저 보는 파일입니다.

### 4.1 권장 구조

```markdown
# Mobile Test Automation Framework

모바일 앱(Android/iOS) 자동화 테스트 프레임워크

## 기술 스택

| 카테고리 | 기술 |
|---------|------|
| 테스트 프레임워크 | Appium + Python + pytest |
| Android 드라이버 | UiAutomator2 |
| iOS 드라이버 | XCUITest |
| 리포팅 | Allure Report + Vercel 웹 대시보드 |
| 디자인 패턴 | Page Object Model (POM) |
| CI/CD | Shell Script 파이프라인 |

## 주요 구현 사항

### 멀티 환경 자동 전환
- `APP_ENV` 하나로 3개 환경(staging/live/livetest)의 APK, 인증 정보,
  UI 요소 접두사가 자동 전환
- 폴더 기반 APK 자동 탐색 (`apk/stage/`, `apk/live/`, `apk/livetest/`)

### 보안 키보드 자동 입력
- 앱 빌드 타입에 따라 숫자 키패드/QWERTY 키보드 자동 판별
- Accessibility ID, content-desc 기반 키 입력 구현

### 초기 화면 자동 처리
- 앱 첫 실행 시 나타나는 언어 선택, 약관 동의 화면 자동 처리
- 로그인 후 팝업(지문 인증, 보안 경고) 자동 처리

### UI Dump 분석 도구
- Android/iOS 화면 요소를 XML로 캡처하는 자체 도구
- Watch 모드: 화면 변화 자동 감지 (0.2초 간격)
- 민감정보(전화번호, 이메일, 생년월일) 자동 마스킹

### 테스트 실행 파이프라인
- 쉘 스크립트 5단계 자동화:
  서버 시작 → 에뮬레이터 부팅 → 테스트 실행 → 리포트 생성 → 대시보드 업로드
- Allure 웹 대시보드: 테스트 이력 추적, 첨부파일 관리

### Allure 리포트 자동화
- pytest 실행 결과 자동 수집 → HTML 리포트 생성
- 실패 시 자동 첨부: 스크린샷, page_source XML, logcat, 비디오

## 프로젝트 구조

(프로젝트 트리 구조)

## 설치 및 실행

(간단한 설치/실행 방법)

## 환경별 실행

(APP_ENV 기반 실행 방법)
```

### 4.2 README 작성 팁

- **첫 3줄**에 "무엇을 하는 프로젝트인지" 명확히 쓴다
- **기술 스택**을 테이블로 한눈에 보이게 정리한다
- **주요 구현 사항**에 기술적 깊이를 보여준다 (단순 나열이 아니라 왜/어떻게)
- **스크린샷/GIF**가 있으면 시각적 효과가 크다 (앱 화면은 마스킹)
- 회사명, 앱명은 쓰지 않는다 ("금융 송금 앱" 정도로 표현)

---

## 5. Public 저장소 생성 절차

### 5.1 방법 A: 새 저장소에 클린 커밋 (권장)

git history에 민감정보가 남지 않아 가장 안전합니다.

```bash
# 1. 포트폴리오용 폴더 생성
mkdir ~/code/appium-portfolio
cd ~/code/appium-portfolio
git init

# 2. private 저장소에서 공개할 파일만 복사
#    (복사 스크립트 또는 수동으로 선별)

# 3. 일반화 작업 수행 (패키지명, URL 등)

# 4. 초기 커밋
git add .
git commit -m "Initial commit: Mobile Test Automation Framework"

# 5. GitHub public 저장소 생성 후 push
gh repo create appium-portfolio --public
git remote add origin https://github.com/<username>/appium-portfolio.git
git push -u origin main
```

### 5.2 방법 B: 브랜치 분리 후 public remote push

기존 저장소에서 public 브랜치를 만들어 별도 remote에 push합니다.

```bash
# 1. public 브랜치 생성 (현재 브랜치 기반)
git checkout -b public

# 2. 비공개 파일 삭제
git rm --cached .env  # 내부 전용 문서들도 함께 제거
git rm -r --cached ui_dumps/ allure-results/ allure-reports/ apk/ .claude/

# 3. 일반화 작업 수행

# 4. 커밋
git commit -m "Prepare public portfolio version"

# 5. public remote에 push
git remote add public https://github.com/<username>/appium-portfolio.git
git push public public:main
```

> **주의**: 방법 B는 git history에 이전 커밋이 포함되므로, 과거 커밋에 민감정보가 있으면 방법 A를 사용해야 합니다.

---

## 6. 공개 후 유지 관리

### 6.1 동기화 전략

private 저장소에서 작업 후, 공개할 변경사항만 public에 반영합니다.

```
private (작업용)  →  일반화 작업  →  public (포트폴리오)
     ↓                                    ↓
  모든 변경사항              민감정보 제거된 변경사항만
```

- 매번 동기화할 필요 없음 — 의미 있는 기능 추가 시에만 반영
- 동기화 시 반드시 민감정보 검사 수행

### 6.2 민감정보 검사 자동화

public push 전 아래 패턴을 검사합니다:

```bash
# 검사 대상 패턴
git diff --cached | grep -iE \
  "password|secret|token|api_key|your_company_package|your_real_username|\.env"
```

검출 대상:
- 비밀번호, API 키, 토큰
- 회사 패키지명 (실제 앱 패키지명)
- 실제 계정 ID
- `.env` 파일 내용

---

## 7. 면접 대비: 예상 질문과 답변 포인트

### Q. 이 프로젝트에서 가장 어려웠던 점은?

**답변 포인트**:
- 보안 키보드 자동 입력 — 일반 `send_keys`가 동작하지 않아 Accessibility ID/content-desc 기반으로 키 하나하나를 탭하는 로직 구현
- 환경별 앱 차이 — staging/live/livetest 앱이 패키지명, resource-id, 키보드 타입이 모두 달라서 `APP_ENV` 기반 자동 전환 시스템 설계

### Q. 테스트 자동화 프레임워크 설계 시 고려한 점은?

**답변 포인트**:
- 모듈화: 로그인, 초기화면, 언어 설정을 독립 모듈로 분리하여 재사용성 확보
- 환경 독립성: 환경변수 하나로 3개 환경을 전환하여 코드 수정 없이 다른 환경 테스트 가능
- 진단 용이성: 실패 시 스크린샷, XML, logcat, 비디오를 자동 첨부하여 원인 분석 시간 단축

### Q. Appium의 한계와 해결 방법은?

**답변 포인트**:
- 보안 키보드에 `send_keys` 불가 → 커스텀 키보드 입력 모듈 개발
- 앱 초기 화면이 매번 다름 → 화면 상태 감지 + 조건부 처리 로직
- 에뮬레이터 불안정 → 자동 재시작, System UI 팝업 자동 처리

### Q. CI/CD와 어떻게 연동하나요?

**답변 포인트**:
- 쉘 스크립트로 5단계 파이프라인 구성 (서버→디바이스→테스트→리포트→대시보드)
- GitHub Actions에서 동일한 스크립트로 실행 가능하도록 설계
- Allure 웹 대시보드로 테스트 이력 추적 및 팀 공유

---

## 8. 체크리스트 요약

public 저장소 push 전 최종 확인:

- [ ] `.env` 파일이 포함되지 않았는가?
- [ ] APK 파일이 포함되지 않았는가?
- [ ] 코드 내 실제 패키지명이 일반화되었는가?
- [ ] 코드 내 실제 계정 정보가 없는가?
- [ ] 대시보드 URL, API 토큰이 제거되었는가?
- [ ] git history에 민감정보가 없는가? (방법 A 사용 시 자동 해결)
- [ ] `.gitignore`에 `.env`, `apk/`, `ui_dumps/` 등이 포함되어 있는가?
- [ ] README.md가 포트폴리오용으로 작성되었는가?
- [ ] 회사명이 문서 어디에도 노출되지 않는가?
