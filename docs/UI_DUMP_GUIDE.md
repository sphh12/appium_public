# UI Dump 도구 가이드

## 개요

`ui_dump.py`는 Appium을 통해 연결된 에뮬레이터/디바이스의 현재 화면 UI 요소를 XML 파일로 저장하는 도구입니다. 저장된 XML 파일을 분석하여 테스트 스크립트 작성에 필요한 요소 정보(resource-id, content-desc, text 등)를 추출할 수 있습니다.

## 설치 및 실행 환경

### 필수 조건

- Python 가상환경 활성화
- Appium 서버 실행 중
- 에뮬레이터 또는 실제 디바이스 연결

### 가상환경 활성화

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

## 사용 방법

### 1. 단일 캡처

현재 화면을 한 번 캡처합니다.

```bash
python tools/ui_dump.py
```

### 2. 이름 지정 캡처

파일명에 식별 가능한 이름을 추가합니다.

```bash
python tools/ui_dump.py login_screen
# 결과: ui_dumps/20260123_143022_login_screen.xml
```

### 3. 인터랙티브 모드

수동으로 화면을 탐색하며 원하는 시점에 캡처합니다.

```bash
python tools/ui_dump.py -i
```

**인터랙티브 모드 조작:**

- `Enter` : 현재 화면 캡처
- `q` + `Enter` : 종료

### 4. 자동 감지 모드 (Watch Mode) - 권장

화면 변화를 자동으로 감지하여 캡처합니다. 사용자 플로우를 따라가며 모든 화면을 자동으로 기록할 때 유용합니다.

```bash
# 기본 실행 (0.2초 간격으로 화면 체크)
python tools/ui_dump.py -w

# 체크 간격 지정 (1초)
python tools/ui_dump.py -w 1.0
```

**자동 감지 모드 특징:**

- 화면 변화 자동 감지 (MD5 해시 비교)
- 화면 이름 자동 추출 (screenTitle, activity명, 또는 첫 번째 텍스트)
- 파일명 형식: `001_ScreenName.xml`, `002_LoginScreen.xml` 등
- `Ctrl+C`로 종료

**화면 이름 추출 우선순위:**

1. `screenTitle` 또는 `toolbarTitle` 요소의 텍스트
2. 일반적인 title 패턴의 요소 텍스트
3. 현재 Activity 이름 (예: `MainActivity` → `Main`)
4. 첫 번째 의미있는 TextView 텍스트

**출력 예시:**

```
감시 시작! 앱에서 화면을 이동해보세요.
--------------------------------------------------

  [01] Main
       -> 001_Main.xml (요소: 45, 클릭: 12)
  [02] Terms_And_Condition
       -> 002_Terms_And_Condition.xml (요소: 38, 클릭: 8)
  [03] Login
       -> 003_Login.xml (요소: 52, 클릭: 15)

감시 종료.
==================================================
  총 3개 화면 자동 캡처 완료
  저장 위치: ui_dumps/260123_1505
==================================================
```

## 저장 위치

캡처된 XML 파일은 `ui_dumps/` 폴더에 저장됩니다.

### 단일/이름 지정 캡처

```
ui_dumps/
├── 20260122_132500.xml              # 단일 캡처
├── 20260122_143022_login_screen.xml # 이름 지정 캡처
└── 20260122_150530_home.xml         # 이름 지정 캡처
```

**파일명 형식:** `YYYYMMDD_HHMMSS_[이름].xml`

### 인터랙티브 모드 / 자동 감지 모드

세션 단위로 폴더가 생성됩니다. 폴더명은 종료 시점의 타임스탬프입니다.

```
ui_dumps/
├── 20260122_132608/                 # 인터랙티브 세션 (YYYYMMDD_HHMMSS)
│   ├── 20260122_132500_001.xml
│   ├── 20260122_132515_002.xml
│   └── 20260122_132540_003.xml
│
└── 260123_1505/                     # Watch 모드 세션 (yymmdd_HHMM)
    ├── 001_Main.xml                 # 화면 이름 자동 추출
    ├── 002_Terms_And_Condition.xml
    └── 003_Login.xml
```

**폴더명 형식:**

- 인터랙티브 모드: `YYYYMMDD_HHMMSS` (예: 20260123_150530)
- Watch 모드: `yymmdd_HHMM` (예: 260123_1505)

**Watch 모드 파일명 형식:** `순번_화면이름.xml`

---

## XML 파일 구조

### 주요 속성

| 속성           | 설명                               | Appium Locator                 |
| -------------- | ---------------------------------- | ------------------------------ |
| `resource-id`  | 요소의 고유 ID                     | `AppiumBy.ID`                  |
| `content-desc` | 접근성 설명 (Accessibility ID)     | `AppiumBy.ACCESSIBILITY_ID`    |
| `text`         | 표시되는 텍스트                    | `AppiumBy.ANDROID_UIAUTOMATOR` |
| `class`        | 요소 클래스명                      | `AppiumBy.CLASS_NAME`          |
| `clickable`    | 클릭 가능 여부                     | -                              |
| `bounds`       | 요소 위치 [left,top][right,bottom] | -                              |

### XML 예시

```xml
<android.widget.Button
    index="1"
    package="com.gmeremit.online.gmeremittance_native.stag"
    class="android.widget.Button"
    text="Login"
    resource-id="com.gmeremit.online.gmeremittance_native.stag:id/btn_submit"
    checkable="false"
    checked="false"
    clickable="true"
    enabled="true"
    focusable="true"
    bounds="[241,1043][838,1180]"
    displayed="true"
/>
```

---

## 캡처된 화면 분석 (GME Remit 앱)

### 001.xml - 안드로이드 홈 화면

| 요소          | content-desc                                | 용도    |
| ------------- | ------------------------------------------- | ------- |
| GME 앱 아이콘 | `GME Remit` 또는 `Predicted app: GME Remit` | 앱 실행 |

### 002.xml - 앱 메인 화면 (로그인 전)

| 요소          | resource-id    | 용도             |
| ------------- | -------------- | ---------------- |
| Login 버튼    | `btn_lgn`      | 로그인 화면 진입 |
| New User 버튼 | `btn_new_user` | 회원가입         |

### 003.xml - 언어 선택 화면

| 요소        | resource-id           | 용도                   |
| ----------- | --------------------- | ---------------------- |
| 언어 목록   | `languageRv`          | 언어 선택 RecyclerView |
| 언어 텍스트 | `countryLanguageText` | English, 한국어 등     |

### 004.xml - 약관 동의 화면

| 요소      | resource-id                                          | 용도                  |
| --------- | ---------------------------------------------------- | --------------------- |
| 화면 제목 | `screenTitle`                                        | "Terms And Condition" |
| 전체 동의 | `agreeAllContainer`                                  | 모든 약관 동의        |
| 개별 약관 | `term1Container`, `term2Container`, `term3Container` | 개별 동의             |

### 005.xml - 로그인 화면

| 요소             | resource-id                | content-desc       | 클릭 가능 |
| ---------------- | -------------------------- | ------------------ | --------- |
| User ID 입력     | `usernameId`               | -                  | O         |
| Password 입력    | `securityKeyboardEditText` | `********`         | O         |
| Login 버튼       | `btn_submit`               | -                  | O         |
| Find my User ID  | `tvFindUserId`             | -                  | O         |
| Forgot Password  | `tv_forgotpass`            | -                  | O         |
| Register Here    | `register`                 | -                  | O         |
| Customer Support | `ivChannelTalk`            | `Customer Support` | O         |

---

## Locator 전략

### 우선순위

1. **Accessibility ID (`content-desc`)** - 권장
    - 크로스 플랫폼 호환성
    - 언어/지역 독립적
    - 유지보수 용이

2. **Resource ID (`resource-id`)** - Fallback
    - Android 전용
    - 패키지명에 의존적

### 코드 예시

```python
from appium.webdriver.common.appiumby import AppiumBy

# 1순위: Accessibility ID
try:
    element = driver.find_element(
        AppiumBy.ACCESSIBILITY_ID,
        "Customer Support"
    )
except NoSuchElementException:
    # 2순위: Resource ID
    element = driver.find_element(
        AppiumBy.ID,
        "com.gmeremit.online.gmeremittance_native.stag:id/ivChannelTalk"
    )
```

### Fallback 헬퍼 함수

```python
def find_element_with_fallback(driver, accessibility_id, resource_id, timeout=5):
    """Accessibility ID 우선, Resource ID fallback"""

    # 1순위: Accessibility ID
    if accessibility_id:
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(
                    (AppiumBy.ACCESSIBILITY_ID, accessibility_id)
                )
            )
        except TimeoutException:
            pass

    # 2순위: Resource ID
    if resource_id:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, resource_id)
            )
        )

    return None
```

---

## 테스트 스크립트에서 활용

### xml_test.py 구조

```python
class TestXmlScenario:
    PACKAGE_ID = "com.gmeremit.online.gmeremittance_native.stag:id"

    # XML에서 추출한 요소 정보
    LOGIN_SCREEN_CLICKABLE_ELEMENTS = [
        {
            "accessibility_id": None,
            "id": "usernameId",
            "name": "User ID 입력란",
            "type": "EditText"
        },
        {
            "accessibility_id": "Customer Support",
            "id": "ivChannelTalk",
            "name": "Customer Support 아이콘",
            "type": "ImageView"
        },
        # ...
    ]
```

### 초기 화면 자동 처리

앱이 `noReset: False`로 초기화될 경우 나타나는 화면들을 자동 처리:

1. **언어 선택 화면** → English 자동 선택
2. **약관 동의 화면** → 전체 동의 자동 클릭

```python
def _handle_initial_screens(self, driver):
    """언어 선택, 약관 동의 등 초기 화면 자동 처리"""

    # 언어 선택 화면 처리
    if self._handle_language_selection(driver):
        time.sleep(2)

    # 약관 동의 화면 처리
    if self._handle_terms_and_conditions(driver):
        time.sleep(2)
```

---

## 민감정보 자동 마스킹

UI Dump 도구는 캡처 시 **개인정보를 자동으로 마스킹**하여 저장합니다. 이를 통해 덤프 파일을 Git 저장소에 안전하게 커밋할 수 있습니다.

### 마스킹 대상

| 데이터 유형 | 원본 예시 | 마스킹 결과 |
|------------|----------|------------|
| 전화번호 (하이픈) | `010-1234-5678` | `010-****-****` |
| 전화번호 (연속) | `01012345678` | `010********` |
| 이메일 | `user@gmail.com` | `u***@g***.com` |
| 생년월일 (하이픈) | `1990-05-15` | `****-**-**` |
| 생년월일 (연속) | `19900515` | `********` |

### 자동 마스킹 동작

모든 캡처 모드에서 자동으로 마스킹이 적용됩니다:

- **단일 캡처** (`python tools/ui_dump.py`)
- **이름 지정 캡처** (`python tools/ui_dump.py screen_name`)
- **인터랙티브 모드** (`python tools/ui_dump.py -i`)
- **자동 감지 모드** (`python tools/ui_dump.py -w`)

### 기존 덤프 파일 마스킹

이미 저장된 덤프 파일들을 일괄 마스킹할 수 있습니다:

```bash
python tools/ui_dump.py --mask-existing
```

**출력 예시:**

```
기존 ui_dumps 파일 마스킹 시작...
--------------------------------------------------
마스킹 완료: ui_dumps/260123_1254/024_Remittance.xml
마스킹 완료: ui_dumps/260123_1254/027_Edit_Info.xml
--------------------------------------------------
총 2개 파일 마스킹 완료
```

### 테스트 코드에 미치는 영향

마스킹은 테스트 코드 작성에 **영향을 주지 않습니다**:

- 테스트에서는 `resource-id`, `content-desc` 등 **속성 기반 locator**를 사용
- 개인정보가 포함된 `text` 속성은 테스트 assertion에 사용하지 않음
- 덤프 파일은 요소 구조 파악용 **참고 자료**로만 활용

---

## 팁 & 트러블슈팅

### 1. Appium 모듈 에러

```
ModuleNotFoundError: No module named 'appium'
```

**해결:** 가상환경 활성화 필요

```bash
venv\Scripts\activate
```

### 2. 요소를 찾을 수 없음

- `ui_dump.py`로 현재 화면 캡처하여 실제 요소 확인
- `resource-id`가 빌드 환경(stag/prod)에 따라 다를 수 있음

### 3. content-desc가 없는 경우

대부분의 앱에서 `content-desc`가 제대로 설정되어 있지 않음

- 개발팀에 접근성 속성 추가 요청
- `resource-id` 또는 `text` 기반 locator 사용

### 4. 동적 요소 처리

화면 로딩 후 요소가 나타나는 경우 `WebDriverWait` 사용:

```python
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((AppiumBy.ID, "element_id"))
)
```

---

## 관련 파일

| 파일                             | 설명                                      |
| -------------------------------- | ----------------------------------------- |
| `tools/ui_dump.py`               | UI 덤프 도구                              |
| `ui_dumps/*.xml`                 | 캡처된 XML 파일들                         |
| `tests/android/xml_test.py`      | XML 기반 테스트 스크립트                  |
| `tests/android/basic_01_test.py` | XML 덤프 기반 기본 테스트                 |
| `utils/initial_screens.py`       | 초기 화면 처리 유틸리티                   |
| `conftest.py`                    | pytest fixture (초기 화면 자동 처리 포함) |
| `docs/CODING_GUIDELINES.md`      | 테스트 스크립트 작성 가이드라인           |
