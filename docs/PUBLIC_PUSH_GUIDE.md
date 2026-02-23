# Public 저장소 푸시 가이드

Private 저장소에서 개발한 코드를 Public 저장소에 안전하게 공개하기 위한 규칙과 워크플로우를 정리합니다.

---

## 1. 저장소 정보

| 항목 | Private | Public |
|------|---------|--------|
| remote 이름 | `github`, `gitlab` | `public` |
| 저장소 | `sphh12/appium` | `sphh12/appium_public` |
| 유형 | Private (개인/팀 전용) | **Public (누구나 접근 가능)** |
| 개발 환경 | **기본 작업 환경** | 공개용 (읽기 전용 배포) |

> **원칙**: 개발은 항상 Private 저장소에서 진행하고, Public에는 정제된 코드만 푸시합니다.

---

## 2. 민감 파일 처리 규칙

### 2.1 실제 파일 대신 .example 파일로 대체

민감정보가 포함된 파일은 실제 파일을 올리지 않고, 플레이스홀더가 포함된 `.example` 파일로 대체합니다.

| 원본 파일 | 대체 파일 | 처리 방법 |
|-----------|----------|-----------|
| `.env` | `.env.example` | `.gitignore`로 제외 (이미 적용됨) |

### 2.2 Public에서 반드시 제외할 파일/폴더

`.gitignore`에 아래 항목이 포함되어 있는지 확인합니다.

```gitignore
# 환경변수 (민감정보)
.env
.env.local
.env.*.local
!.env.example

# APK 파일
apk/
*.apk
*.apk+

# UI 덤프 (앱 구조 정보 포함)
ui_dumps/

# 디버그 산출물
debug_output/

# Claude Code (로컬 전용)
.claude/

# Allure 리포트/결과
allure-results/
allure-reports/
```

---

## 3. 코드 내 민감정보 처리

### 3.1 처리가 필요한 항목

| 유형 | 예시 | 처리 방법 |
|------|------|-----------|
| 테스트 계정 | `username`, `PIN` | 환경변수 (`os.getenv()`) |
| API 토큰 | `BLOB_READ_WRITE_TOKEN` | 환경변수 (기본값 빈 문자열) |
| 개인 경로 | `/Users/sph/appium/` | 상대경로 또는 `os.path.expanduser("~")` |
| 대시보드 URL | `https://xxx.vercel.app` | 환경변수 또는 플레이스홀더 |

### 3.2 허용되는 기본값 (Public에 포함 가능)

다음은 공개해도 문제없는 항목입니다:

- **Appium 기본 설정**: `host=127.0.0.1`, `port=4723` (로컬 개발용)
- **앱 패키지명**: 공개 앱의 패키지 ID는 앱 스토어에서 조회 가능한 공개 정보
- **예시 PIN**: `1212`, `1234` 등 (실제 계정 PIN이 아닌 예시값)
- **플레이스홀더**: `your_username`, `app.apk` 등

### 3.3 주의가 필요한 패턴

푸시 전 아래 패턴을 검색하여 민감정보가 없는지 확인합니다:

```bash
# 계정 정보 검색
git diff --cached | grep -iE "password|secret|token|api_key"

# 하드코딩된 사용자 경로 검색
git diff --cached | grep -E "/Users/[a-zA-Z]+/"

# .env 파일이 스테이징되었는지 확인
git status | grep "\.env"

# 추적되면 안 되는 파일 확인
git ls-files | grep -E "\.env$|\.apk$|ui_dumps/|debug_output/"
```

---

## 4. 푸시 전 검증 체크리스트

```
[ ] .env 파일이 Git에 포함되지 않았는가?
[ ] .env.example에 실제 값 대신 플레이스홀더가 있는가?
[ ] ui_dumps/ 폴더가 제외되었는가?
[ ] debug_output/ 폴더가 제외되었는가?
[ ] 코드에 하드코딩된 계정 정보가 없는가?
[ ] 코드에 개인 경로(/Users/xxx/)가 없는가?
[ ] API 토큰이 환경변수로 처리되었는가?
[ ] allure-results/, allure-reports/가 제외되었는가?
```

---

## 5. 푸시 후 원상복구 (핵심)

### 5.1 원칙

> Public 푸시를 위해 변경한 파일은 **푸시 완료 후 반드시 원래 상태로 복구**합니다.
> 개발하기 쉬운 세팅(Private 기준)을 항상 유지하기 위함입니다.

### 5.2 복구 방법

**방법 1: git stash 활용 (권장)**

```bash
# 1. 현재 개발 상태 저장
git stash push -m "dev settings backup"

# 2. Public용 수정 → 커밋 → 푸시
#    (수정 작업 진행)
git add .
git commit -m "chore: public 배포용 정리"
git push public home

# 3. 원래 개발 상태로 복구
git stash pop
```

**방법 2: 별도 브랜치 사용**

```bash
# 1. Public용 브랜치 생성
git checkout -b public-release

# 2. 민감정보 정리 → 커밋 → 푸시
#    (수정 작업 진행)
git add .
git commit -m "chore: public 배포용 정리"
git push public public-release:home

# 3. 원래 브랜치로 복귀
git checkout home
git branch -d public-release
```

### 5.3 복구 확인

```bash
# 복구 후 Private 저장소와 동일한 상태인지 확인
git diff github/home
```

---

## 6. 푸시 워크플로우 (전체 단계)

```
┌─────────────────────────────────────────────┐
│  1. 검증: 민감정보 체크리스트 확인            │
│  2. 백업: git stash (현재 개발 상태 저장)     │
│  3. 수정: Public용 민감정보 정리              │
│  4. 커밋: Public용 커밋 생성                  │
│  5. 푸시: git push public home               │
│  6. 복구: git stash pop (개발 상태 복원)      │
│  7. 확인: Private 저장소와 상태 동일 여부 확인 │
└─────────────────────────────────────────────┘
```

### 실행 예시

```bash
# 1~2. 백업
git stash push -m "dev settings backup"

# 3. Public용 수정 (필요한 경우)
# - 개인 경로 → 상대경로 변경
# - 하드코딩된 URL → 환경변수 변경

# 4. 커밋
git add .
git commit -m "chore: public 배포용 정리"

# 5. 푸시
git push public home

# 6. 복구
git stash pop

# 7. 확인
git status
git diff github/home
```

---

## 7. 참고

- 상세 보안 정책: [GIT_RULES.md](../GIT_RULES.md) (섹션 2~7)
- 환경변수 목록: [.env.example](../.env.example)
- UI 덤프 정책: [GIT_RULES.md](../GIT_RULES.md) (섹션 14)
