# 코딩 가이드라인

## 개요

이 문서는 테스트 스크립트 작성 시 따라야 할 규칙과 가이드라인을 정리합니다.

---

## 1. UI Dump 기반 테스트 스크립트 작성

### 1.1 XML 덤프 파일 참조

| 상황 | 규칙 |
|------|------|
| 별도 언급 없음 | **최신 dump 폴더/파일** 참조 |
| 특정 폴더/파일 지정 | 지정된 파일 참조 |

**최신 폴더 확인 방법:**
```
ui_dumps/
├── 20260122_132608/    # 이전 세션
└── 260123_1254/        # ← 최신 (이 폴더 사용)
```

### 1.2 XML 파일 분석 시 확인 항목

테스트 스크립트 생성 전 반드시 확인:

1. **화면 타이틀** - `screenTitle`, `toolbar_title`, `txvTitle` 등
2. **클릭 가능 요소** - `clickable="true"` 속성
3. **주요 UI 요소** - `resource-id`, `content-desc`, `text`
4. **입력 필드** - EditText 클래스의 요소들

---

## 2. Locator 전략

### 2.1 우선순위

```
1순위: Accessibility ID (content-desc)
2순위: Resource ID (resource-id)
```

### 2.2 구현 패턴

```python
def find_element_with_fallback(self, driver, accessibility_id=None, resource_id=None, timeout=5):
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
                (AppiumBy.ID, f"{self.PACKAGE_ID}/{resource_id}")
            )
        )
    return None
```

### 2.3 사용 예시

```python
# Accessibility ID가 있는 경우
element = self.find_element_with_fallback(
    driver,
    accessibility_id="Customer Support",
    resource_id="ivChannelTalk"
)

# Resource ID만 있는 경우
element = self.find_element_with_fallback(
    driver,
    resource_id="btn_submit"
)
```

---

## 3. 테스트 파일 명명 규칙

### 3.1 파일명

```
tests/android/
├── basic_01_test.py    # 기본 테스트
├── gme1_test.py        # GME 테스트 1
├── xml_test.py         # XML 기반 테스트
└── <기능>_test.py      # 기능별 테스트
```

### 3.2 클래스/메서드명

```python
class TestBasic01:
    """테스트 클래스 - Test로 시작"""

    def test_01_feature_name(self, android_driver):
        """테스트 메서드 - test_로 시작, 순번_기능명"""
        pass
```

---

## 4. Allure 리포트 어노테이션

### 4.1 필수 어노테이션

```python
@allure.feature("기능 영역")      # Home, History, Profile 등
@allure.story("세부 기능")        # Easy Wallet Account, 거래 내역 등
@allure.severity(allure.severity_level.CRITICAL)  # BLOCKER, CRITICAL, NORMAL, MINOR
@allure.title("테스트 제목")
@allure.description("테스트 설명")
def test_example(self, android_driver):
    pass
```

### 4.2 Step 사용

```python
with allure.step("단계 설명"):
    # 테스트 코드
    assert condition, "실패 메시지"
```

---

## 5. 초기 화면 처리

### 5.1 자동 처리 (기본)

`conftest.py`에서 자동으로 처리:
- 언어 선택 화면 → English 선택
- 약관 동의 화면 → 전체 동의

### 5.2 자동 처리 비활성화

```python
@pytest.mark.skip_initial_screens
def test_without_initial_handling(self, android_driver):
    """초기 화면 처리 없이 테스트"""
    pass
```

---

## 6. UI Dump 도구 사용

### 6.1 모드 선택

| 모드 | 명령어 | 용도 |
|------|--------|------|
| 단일 캡처 | `python tools/ui_dump.py` | 현재 화면 1회 캡처 |
| 이름 지정 | `python tools/ui_dump.py login` | 이름 붙여 캡처 |
| 인터랙티브 | `python tools/ui_dump.py -i` | 수동 캡처 |
| **Watch (권장)** | `python tools/ui_dump.py -w` | 자동 감지 캡처 |

### 6.2 Watch 모드 출력

```
ui_dumps/260123_1505/
├── 001_Main.xml
├── 002_History.xml
└── 003_Edit_Info.xml
```

---

## 7. 테스트 실행

### 7.1 단일 파일 실행

```bash
./run-app.sh --basic_01
./run-app.sh --xml_test
```

### 7.2 직접 실행

```bash
pytest tests/android/basic_01_test.py -v
```

---

## 8. 체크리스트

### 테스트 스크립트 작성 전

- [ ] 최신 UI dump 폴더 확인
- [ ] 대상 화면의 XML 파일 분석
- [ ] 주요 요소의 resource-id, content-desc 추출

### 테스트 스크립트 작성 시

- [ ] Accessibility ID 우선 사용
- [ ] `find_element_with_fallback` 헬퍼 함수 활용
- [ ] Allure 어노테이션 추가
- [ ] Step 단위로 구분

### 테스트 스크립트 작성 후

- [ ] 파일명 규칙 준수 확인 (`*_test.py`)
- [ ] 실행 테스트