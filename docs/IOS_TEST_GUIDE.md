# iOS UI Dump 기반 테스트 작성 가이드

## 개요

iOS 시뮬레이터 내장 앱(연락처 등)을 대상으로 UI Dump → 분석 → 테스트 코드 작성까지의 전체 흐름을 정리한 가이드입니다. 연락처 앱 테스트(`ios_contacts_test.py`) 작성 과정에서 겪은 시행착오와 해결 방법을 포함합니다.

---

## 1. 전체 작업 흐름

```
[1] UI Dump 캡처  →  [2] XML 분석  →  [3] 테스트 코드 작성  →  [4] 실행 및 디버깅
```

| 단계 | 도구/명령어 | 산출물 |
|------|------------|--------|
| UI Dump 캡처 | `python tools/ui_dump_ios.py` | `ui_dumps/ios_{timestamp}/*.xml` |
| XML 분석 | VS Code에서 XML 열기 | 요소 정보 정리 (name, type, label) |
| 테스트 코드 작성 | - | `tests/ios/*_test.py` |
| 실행 | `pytest tests/ios/*_test.py -v -s` | 테스트 결과 |

---

## 2. Step 1: UI Dump 캡처

### 2.1 필요한 화면 캡처

테스트 시나리오에 포함되는 **모든 화면**을 캡처합니다.

```bash
# 가상환경 활성화
source venv/bin/activate

# 단일 캡처 (이름 지정)
python tools/ui_dump_ios.py contacts_list     # 연락처 목록 화면
python tools/ui_dump_ios.py contacts_add      # 연락처 추가 화면

# Watch 모드 (화면 변화 자동 캡처) - 여러 화면을 연속으로 캡처할 때
python tools/ui_dump_ios.py -w
```

### 2.2 저장 위치

```
ui_dumps/
├── ios_20260215_2348/                        # iOS 폴더 (ios_ 프리픽스)
│   ├── 20260215_2335_ios_contacts_list.xml
│   └── 20260215_2348_ios_contacts_add.xml
├── aos_260123_1254/                          # Android 폴더 (aos_ 프리픽스)
│   └── ...
```

---

## 3. Step 2: XML 분석

### 3.1 iOS XML 요소 구조

iOS는 Android와 속성명이 다릅니다.

| 용도 | iOS 속성 | Android 속성 |
|------|----------|-------------|
| 요소 식별 | `name` | `resource-id` |
| 접근성 ID | `name` / `label` | `content-desc` |
| 표시 텍스트 | `value` / `label` | `text` |
| 요소 타입 | `type` (XCUIElementType...) | `class` (android.widget...) |
| 클릭 가능 | `enabled` + `accessible` | `clickable` |

### 3.2 XML에서 추출할 정보

```xml
<!-- 예: 연락처 추가 화면의 TextField -->
<XCUIElementTypeTextField
    type="XCUIElementTypeTextField"
    name="성"              ← Locator로 사용
    label="성"
    value="성"             ← placeholder (입력 전)
    enabled="true"
    accessible="true"
/>

<!-- 예: 버튼 -->
<XCUIElementTypeButton
    type="XCUIElementTypeButton"
    name="완료"            ← Locator로 사용
    label="완료"
    enabled="true"
/>
```

### 3.3 분석 결과 정리 (권장 형식)

테스트 코드 작성 전, 분석 결과를 테스트 파일 docstring에 기록합니다.

```python
"""
UI 요소 정보 (ui_dumps/ios_20260215_2348 기반):
- 성: TextField name="성"
- 이름: TextField name="이름"
- 직장: TextField name="직장"
- 전화번호 추가: Cell → 클릭 후 TextField name="휴대전화" 생성
- 완료: Button name="완료"
- 추가: Button name="추가"
"""
```

---

## 4. Step 3: 테스트 코드 작성

### 4.1 기본 구조

```python
import time
import pytest
from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.capabilities import get_appium_server_url


class TestiOSExample:

    @pytest.fixture(scope="function")
    def app_driver(self):
        """앱 전용 드라이버"""
        caps = {
            "platformName": "iOS",
            "automationName": "XCUITest",
            "deviceName": "iPhone 17",
            "platformVersion": "26.2",
            "bundleId": "com.apple.MobileAddressBook",  # 대상 앱 bundleId
            "noReset": True,
            "newCommandTimeout": 300,
        }
        options = XCUITestOptions().load_capabilities(caps)
        driver = webdriver.Remote(
            command_executor=get_appium_server_url(),
            options=options,
        )
        driver.implicitly_wait(10)

        yield driver
        driver.quit()
```

### 4.2 iOS Locator 전략

```
1순위: ACCESSIBILITY_ID (name 속성)   → 대부분의 iOS 요소에서 사용 가능
2순위: XPath (type + name 조합)       → 동일 name이 여러 요소에 있을 때
```

```python
# 1순위: Accessibility ID
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "추가")

# 2순위: XPath (타입 지정이 필요할 때)
field = driver.find_element(
    AppiumBy.XPATH,
    "//XCUIElementTypeTextField[@name='성']"
)
```

### 4.3 내장 앱 bundleId

| 앱 | bundleId |
|----|----------|
| 연락처 | `com.apple.MobileAddressBook` |
| 설정 | `com.apple.Preferences` |
| 캘린더 | `com.apple.mobilecal` |
| Safari | `com.apple.mobilesafari` |
| 메모 | `com.apple.mobilenotes` |

---

## 5. 시행착오 & 해결 방법

### 5.1 iOS 한국어 이름 표시 형식

**문제**: 성="홍", 이름="길동"을 입력했는데 목록에서 찾을 수 없음

```python
# ❌ 잘못된 방식 - "이름 성" 형식
full_name = f"{first_name} {last_name}"  # "길동 홍"

# ✅ 올바른 방식 - iOS는 "성이름" (공백 없음) 형식으로 표시
full_name = f"{last_name}{first_name}"   # "홍길동"
```

**원인**: iOS 연락처 앱은 한국어 이름을 `"성이름"` (공백 없음)으로 표시합니다. 영어 이름은 `"First Last"` 형식입니다.

### 5.2 앱 상태 불일치 (가장 빈번한 문제)

**문제**: 이전 테스트 실패로 앱이 편집 화면/상세 화면/그룹 화면에 남아있어서 다음 테스트에서 "추가" 버튼을 찾지 못함

```python
# ✅ 해결: terminate_app + activate_app으로 앱 재시작
def _ensure_contacts_list(self, driver):
    """앱 재시작으로 항상 깨끗한 상태에서 시작"""
    bundle_id = "com.apple.MobileAddressBook"
    driver.terminate_app(bundle_id)
    time.sleep(1)
    driver.activate_app(bundle_id)
    time.sleep(2)

    # 기대하는 화면인지 확인
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "추가"))
    )
```

**핵심**: fixture에서 `yield` 전에 앱 상태를 초기화하면, 테스트 실패 후에도 다음 실행이 안정적입니다.

### 5.3 StaleElementReferenceException

**문제**: TextField를 찾아서 클릭했는데, `send_keys()` 시점에 요소 참조가 만료됨

```python
# ❌ 문제 코드 - 클릭 후 요소 갱신됨
field = driver.find_element(AppiumBy.XPATH, xpath)
field.click()
field.send_keys(text)  # StaleElementReferenceException!

# ✅ 해결 - 클릭 후 재탐색
field = driver.find_element(AppiumBy.XPATH, xpath)
field.click()
time.sleep(0.3)
field = driver.find_element(AppiumBy.XPATH, xpath)  # 재탐색
field.send_keys(text)
```

**원인**: iOS에서 TextField를 탭하면 키보드가 올라오면서 DOM이 갱신됩니다. 갱신 전에 찾은 요소 참조는 무효화됩니다.

### 5.4 동일 name의 Cell과 TextField 구분

**문제**: `"전화번호 추가"` Cell을 클릭하면 `"휴대전화"` TextField가 생성되는데, Accessibility ID로 찾으면 Cell이 먼저 잡힘

```python
# ❌ Cell과 TextField 모두 name="휴대전화"
field = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "휴대전화")  # Cell이 잡힐 수 있음

# ✅ XPath로 타입을 명시적으로 지정
field = driver.find_element(
    AppiumBy.XPATH,
    "//XCUIElementTypeTextField[@name='휴대전화']"
)
```

### 5.5 키보드가 버튼을 가림

**문제**: 전화번호 입력 후 키보드가 "완료" 버튼을 가려서 탭이 안 됨

```python
# ✅ NavigationBar 탭으로 키보드 닫기
def _dismiss_keyboard(self, driver):
    try:
        nav = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "새로운 연락처")
        nav.click()
    except Exception:
        pass
    time.sleep(0.5)
```

**참고**: `driver.hide_keyboard()`는 iOS에서 동작하지 않는 경우가 많습니다. NavigationBar나 빈 영역을 탭하는 방식이 안정적입니다.

### 5.6 전화번호 포맷팅 차이

**문제**: `"01012345678"` 입력 → iOS가 자동으로 `"010-1234-5678"`로 표시 → 문자열 비교 실패

```python
# ❌ 직접 비교 - 포맷이 다르면 실패
assert "01012345678" in page_source

# ✅ 숫자만 추출하여 비교
source_digits = "".join(c for c in page_source if c.isdigit())
assert "01012345678" in source_digits
```

### 5.7 동적으로 생성되는 요소

**문제**: "전화번호 추가" 셀을 클릭해야 "휴대전화" TextField가 생성됨 → 클릭 전에는 존재하지 않음

```python
# ✅ 셀 클릭 → 대기 → 생성된 요소 찾기
self._wait_and_tap(driver, "전화번호 추가")
time.sleep(0.5)

phone_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located(
        (AppiumBy.XPATH, "//XCUIElementTypeTextField[@name='휴대전화']")
    )
)
phone_field.send_keys("01012345678")
```

---

## 6. 헬퍼 메서드 모음

아래 헬퍼 메서드들은 iOS 테스트에서 반복적으로 사용됩니다.

```python
def _wait_and_tap(self, driver, accessibility_id, timeout=10):
    """요소 대기 후 탭"""
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
    )
    element.click()
    return element


def _input_text_field(self, driver, field_name, text):
    """TextField 입력 (StaleElement 방지)"""
    xpath = f"//XCUIElementTypeTextField[@name='{field_name}']"
    field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
    )
    field.click()
    time.sleep(0.3)
    field = driver.find_element(AppiumBy.XPATH, xpath)  # 재탐색
    field.send_keys(text)


def _is_element_present(self, driver, accessibility_id, timeout=5):
    """요소 존재 여부 확인"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
        )
        return True
    except Exception:
        return False
```

---

## 7. iOS vs Android 주요 차이 요약

| 항목 | iOS | Android |
|------|-----|---------|
| Locator 1순위 | `ACCESSIBILITY_ID` (name) | `ACCESSIBILITY_ID` (content-desc) |
| Locator 2순위 | `XPATH` (type + name) | `ID` (resource-id) |
| 요소 타입 접두사 | `XCUIElementType` | `android.widget.` |
| TextField 입력 | 클릭 → 재탐색 → send_keys | 바로 send_keys 가능 |
| 키보드 닫기 | NavigationBar 탭 | `driver.hide_keyboard()` |
| 앱 초기화 | `terminate_app` + `activate_app` | `driver.reset()` |
| 스크롤 | `mobile: scroll` | `UiScrollable` |
| 이름 표시 (한국어) | "홍길동" (성이름) | 앱마다 다름 |

---

## 8. 체크리스트

### 테스트 작성 전

- [ ] 대상 화면 UI Dump 캡처 완료
- [ ] XML에서 요소 정보(name, type) 추출
- [ ] 동일 name 요소 여부 확인 (Cell vs TextField 등)
- [ ] 동적 생성 요소 파악 (클릭 후 나타나는 요소)

### 테스트 작성 시

- [ ] fixture에 앱 상태 초기화 로직 포함
- [ ] TextField 입력은 **클릭 → 재탐색 → send_keys** 패턴
- [ ] XPath로 타입 명시 (동일 name 요소 구분)
- [ ] 키보드 닫기 로직 포함 (버튼 탭 전)
- [ ] 포맷팅되는 데이터는 숫자만 비교

### 테스트 작성 후

- [ ] 파일명 규칙 준수 (`*_test.py`)
- [ ] 연속 2회 실행해도 통과하는지 확인 (앱 상태 초기화 검증)
- [ ] 테스트 데이터 정리 로직 포함

---

## 관련 파일

| 파일 | 설명 |
|------|------|
| `tools/ui_dump_ios.py` | iOS UI Dump 도구 |
| `tests/ios/ios_contacts_test.py` | 연락처 앱 테스트 (실제 작동 예시) |
| `tests/ios/test_ios_first.py` | Safari 기반 연결 테스트 |
| `config/capabilities.py` | iOS/Android capabilities 설정 |
| `docs/UI_DUMP_GUIDE.md` | UI Dump 도구 사용 가이드 (Android 중심) |
| `docs/IOS_SETUP_GUIDE.md` | iOS 환경 설정 가이드 |
