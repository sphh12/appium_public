# Git 푸시 규칙 (Git Push Rules)

이 문서는 코드를 Git 저장소에 푸시할 때 준수해야 할 규칙을 정리합니다.

---

## 1. 기본 푸시 정책

별도의 언급이 없으면 **GitLab과 GitHub 모두에 푸시**를 진행한다.

```bash
# 두 저장소에 동시 푸시
git push github <branch>
git push gitlab <branch>
```

---

## 2. 저장소 유형별 보안 정책

### Private 저장소 (개인/팀 전용)

| 항목 | 필수 여부 | 설명 |
|------|-----------|------|
| 민감정보 제거 | **선택** | 접근 권한이 제한되므로 민감정보 포함 가능 |
| 환경변수 분리 | 권장 | 관리 편의성을 위해 권장하나 필수 아님 |
| .gitignore 설정 | 권장 | APK, 빌드 산출물 등 제외 권장 |

### Public 저장소 (공개)

| 항목 | 필수 여부 | 설명 |
|------|-----------|------|
| 민감정보 제거 | **필수** | 누구나 접근 가능하므로 반드시 제거 |
| 환경변수 분리 | **필수** | 모든 민감정보는 환경변수로 처리 |
| .gitignore 설정 | **필수** | `.env`, APK, UI 덤프 등 반드시 제외 |
| .env.example 제공 | **필수** | 설정 방법 안내를 위한 템플릿 필수 |

> **중요**: Public 저장소에 민감정보가 한 번이라도 커밋되면, 히스토리에 영구 기록됩니다.
> 삭제 후에도 복구 가능하므로 **푸시 전 반드시 확인**하세요.

---

## 3. 민감정보 분류

### Public 저장소에서 반드시 제거해야 할 항목

| 항목 | 예시 | 처리 방법 |
|------|------|-----------|
| 테스트 계정 ID | `gme_qualitytest44` | 환경변수 `GME_TEST_USERNAME` |
| 테스트 PIN/비밀번호 | `123456` | 환경변수 `GME_TEST_PIN` |
| API 키/토큰 | `sk-xxxx`, `token_xxxx` | 환경변수 사용 |
| 실제 `.env` 파일 | `.env`, `.env.local` | `.gitignore`에 추가 |

### 주의가 필요한 항목

| 항목 | 설명 | 권장 조치 |
|------|------|-----------|
| 앱 패키지 ID | `com.company.app:id` | 환경변수 기본값으로만 사용 |
| APK 파일명 | `App_v1.0.0.apk` | 환경변수 `GME_APK_FILENAME` |
| 디바이스 UDID | 실물 기기 시리얼 | 환경변수 `ANDROID_UDID` |
| UI 덤프 파일 | `ui_dumps/*.xml` | `.gitignore`에 추가 |

---

## 4. Public 저장소용 .gitignore 필수 항목

```gitignore
# 환경변수 (민감정보)
.env
.env.local
.env.*.local
!.env.example

# APK 파일
apk/
*.apk

# UI 덤프 (앱 구조 정보 포함)
ui_dumps/

# Appium 세션 파일
*.appiumsession
```

---

## 5. 환경변수 체크리스트 (Public 저장소 필수)

푸시 전 아래 항목들이 코드에 하드코딩되어 있지 않은지 확인:

- [ ] `GME_TEST_USERNAME` - 테스트 계정 ID
- [ ] `GME_TEST_PIN` - 테스트 계정 PIN
- [ ] `GME_RESOURCE_ID_PREFIX` - 앱 패키지 resource-id 접두사
- [ ] `GME_APK_FILENAME` - APK 파일명
- [ ] `APPIUM_HOST` - Appium 서버 호스트
- [ ] `APPIUM_PORT` - Appium 서버 포트
- [ ] `ANDROID_UDID` - 디바이스 시리얼

---

## 6. Public 저장소 푸시 전 검증 명령어

```bash
# 민감정보 검색 (계정명, PIN 등)
git diff --cached | grep -iE "password|secret|token|api_key|123456|qualitytest"

# 하드코딩된 패키지 ID 검색
git diff --cached | grep -E "com\.[a-z]+\.[a-z]+.*:id"

# .env 파일이 스테이징되었는지 확인
git status | grep "\.env"

# 추적되면 안 되는 파일 확인
git ls-files | grep -E "\.env$|\.apk$|ui_dumps/"
```

---

## 7. 코드 작성 규칙 (Public 저장소용)

### 올바른 환경변수 사용 패턴

```python
import os
from dotenv import load_dotenv

load_dotenv()

# 민감정보: 기본값 없이 환경변수 필수
USERNAME = os.getenv("GME_TEST_USERNAME", "")
PIN = os.getenv("GME_TEST_PIN", "")

# 설정값: 기본값 허용 (단, 실제 값 대신 플레이스홀더 권장)
RESOURCE_ID_PREFIX = os.getenv("GME_RESOURCE_ID_PREFIX", "")
```

### 잘못된 예시 (Public 저장소 금지)

```python
# BAD: 하드코딩된 민감정보
USERNAME = "gme_qualitytest44"
PIN = "123456"
PACKAGE_ID = "com.gmeremit.online.gmeremittance_native.stag:id"
```

---

## 8. 커밋 메시지 규칙

### 기본 형식

```
<type>: <파일/기능1> - <변경내용> / <파일/기능2> - <변경내용>

<한글 상세 설명>
- 변경사항 1
- 변경사항 2
```

### Type 종류

| Type | 설명 |
|------|------|
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 변경 |
| `refactor` | 코드 리팩토링 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드, 설정 변경 |
| `style` | 코드 포맷팅 |

### 예시

```
feat: auth.py - 환경변수 지원 추가 / .env.example - 템플릿 생성 / .gitignore - 민감정보 제외

민감정보 환경변수 분리
- 테스트 계정 (username, PIN) 환경변수화
- APK 파일명, 패키지 ID 환경변수화
- .env.example 템플릿 파일 추가
- .gitignore 업데이트 (민감정보 보호)
```

```
fix: test_01.py - 타임아웃 증가 / conftest.py - 딜레이 추가

로그인 테스트 간헐적 실패 수정
- WebDriverWait 타임아웃 10초 → 15초 증가
- 보안 키보드 입력 후 딜레이 추가
```

```
docs: GIT_RULES.md - 푸시 규칙 문서 추가

Git 푸시 규칙 문서 추가
- Private/Public 저장소별 보안 정책 정리
- 민감정보 처리 가이드라인 작성
- 커밋 메시지 작성 규칙 추가
```

```
refactor: Allure report - 대시보드 앱 버전 추가, export 기능 추가 / test_01.py - 불필요한 로직 제거
```

### 규칙

1. **제목**: `<파일/기능(영문)> - <변경내용(한글)>` 형식, 여러 파일은 `/`로 구분
2. **본문**: 한글 상세 설명, 변경 이유와 내용 포함
3. **빈 줄**: 제목과 본문 사이에 빈 줄 필수

---

## 9. 긴급 조치 (Public 저장소에 민감정보 노출 시)

만약 민감정보가 실수로 커밋된 경우:

```bash
# 1. 즉시 해당 파일 삭제 후 새 커밋
git rm --cached <파일명>
git commit -m "fix: 민감정보 포함 파일 제거"

# 2. 히스토리에서 완전 삭제 (주의: 협업 시 팀원 동기화 필요)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <파일명>" \
  --prune-empty --tag-name-filter cat -- --all

# 3. 원격 강제 푸시
git push origin --force --all

# 4. 민감정보 즉시 변경 (비밀번호, API 키 등)
# - 노출된 계정 비밀번호 변경
# - 노출된 API 키 재발급
```

> **경고**: Public 저장소에 노출된 민감정보는 이미 복제되었을 수 있습니다.
> 히스토리 삭제와 함께 **반드시 해당 민감정보를 변경**하세요.

---

## 10. 원격 브랜치 상태 확인

원격 저장소의 브랜치 상태를 확인할 때는 **반드시 fetch 후 확인**해야 합니다.

### 주의사항

`git branch -a` 명령어는 로컬에 캐시된 원격 브랜치 정보만 표시합니다.
실제 원격 저장소의 최신 상태와 다를 수 있습니다.

### 올바른 확인 방법

```bash
# 1. 모든 원격 저장소에서 최신 정보 가져오기
git fetch --all

# 2. 원격 브랜치 목록 확인
git branch -a

# 3. 특정 원격 저장소만 fetch
git fetch github
git fetch gitlab
```

### 잘못된 예시

```bash
# BAD: fetch 없이 바로 확인 (오래된 정보일 수 있음)
git branch -a
```

> **주의**: fetch 없이 `git branch -a`를 실행하면 원격에 새로 생성된 브랜치가
> 보이지 않거나, 이미 삭제된 브랜치가 여전히 표시될 수 있습니다.

---

## 요약

| 저장소 유형 | 민감정보 처리 | 환경변수 분리 | .gitignore |
|-------------|---------------|---------------|------------|
| **Private** | 선택 | 권장 | 권장 |
| **Public** | **필수** | **필수** | **필수** |

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-03 | 최초 작성 |
| 2026-02-03 | 원격 브랜치 상태 확인 규칙 추가 (섹션 10) |
