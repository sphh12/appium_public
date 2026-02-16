"""
iOS 연락처 앱 테스트 시나리오
시뮬레이터 내장 연락처 앱을 활용한 iOS 자동화 연습

시나리오: 연락처 추가 → 정보 입력 → 저장 → 저장된 연락처 조회

UI 요소 정보 (ui_dumps/ios_20260215_2348 기반):
- 성: TextField name="성"
- 이름: TextField name="이름"
- 직장: TextField name="직장"
- 전화번호 추가: Cell → 클릭 후 TextField name="휴대전화" 생성
- 완료: Button name="완료"
- 추가: Button name="추가"
- 닫기: Button name="닫기"

참고: iOS 연락처 목록에서 한국어 이름은 "성이름" 형식으로 표시됨
      예) 성="홍", 이름="길동" → 목록에서 "홍길동"으로 표시
"""
import time

import allure
import pytest
from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from config.capabilities import get_appium_server_url


# 테스트용 연락처 정보
TEST_CONTACT = {
    "last_name": "홍",
    "first_name": "길동",
    "company": "QA팀",
    "phone": "01012345678",
}

# iOS 연락처 목록에서 표시되는 이름 형식 (성+이름, 공백 없음)
FULL_NAME = f"{TEST_CONTACT['last_name']}{TEST_CONTACT['first_name']}"


class TestiOSContacts:
    """iOS 연락처 앱 테스트"""

    @pytest.fixture(scope="function")
    def contacts_driver(self):
        """연락처 앱 전용 드라이버"""
        caps = {
            "platformName": "iOS",
            "automationName": "XCUITest",
            "deviceName": "iPhone 17",
            "platformVersion": "26.2",
            "bundleId": "com.apple.MobileAddressBook",
            "noReset": True,
            "newCommandTimeout": 300,
        }
        options = XCUITestOptions().load_capabilities(caps)

        print("[INFO] 연락처 앱 실행 중...")
        driver = webdriver.Remote(
            command_executor=get_appium_server_url(),
            options=options,
        )
        driver.implicitly_wait(10)
        print("[INFO] 연락처 앱 실행 성공!")

        # 연락처 목록 화면으로 이동 보장
        self._ensure_contacts_list(driver)

        yield driver

        driver.quit()
        print("[INFO] 드라이버 종료 완료")

    # =========================================================================
    # 헬퍼 메서드
    # =========================================================================

    def _ensure_contacts_list(self, driver):
        """연락처 목록 화면에 있는지 확인하고, 아니면 이동"""
        bundle_id = "com.apple.MobileAddressBook"

        # 앱 종료 후 재시작 → 항상 깨끗한 연락처 목록에서 시작
        print("  [NAV] 연락처 앱 재시작으로 초기화...")
        driver.terminate_app(bundle_id)
        time.sleep(1)
        driver.activate_app(bundle_id)
        time.sleep(2)

        # "추가" 버튼이 보이면 연락처 목록 화면
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "추가"))
            )
            print("  [NAV] 연락처 목록 화면 확인 완료")
        except Exception:
            print("  [NAV] ⚠️ 연락처 목록 화면 진입 실패")

    def _wait_and_tap(self, driver, accessibility_id, timeout=10):
        """요소가 나타날 때까지 대기 후 탭"""
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
        )
        element.click()
        print(f"  [TAP] '{accessibility_id}' 클릭")
        return element

    def _input_text_field(self, driver, field_name, text):
        """TextField에 텍스트 입력 (StaleElement 방지를 위해 재탐색)"""
        # XPath로 정확히 TextField 타입 지정 (Cell과 구분)
        xpath = f"//XCUIElementTypeTextField[@name='{field_name}']"
        field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
        )
        field.click()
        time.sleep(0.3)
        # 클릭 후 요소가 갱신될 수 있으므로 재탐색
        field = driver.find_element(AppiumBy.XPATH, xpath)
        field.send_keys(text)
        time.sleep(0.3)

        # 입력값 확인
        field = driver.find_element(AppiumBy.XPATH, xpath)
        actual = field.get_attribute("value")
        print(f"  [INPUT] '{field_name}' → '{text}' (실제값: '{actual}')")

    def _is_element_present(self, driver, accessibility_id, timeout=5):
        """요소 존재 여부 확인"""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, accessibility_id))
            )
            return True
        except Exception:
            return False

    def _dismiss_keyboard(self, driver):
        """키보드 닫기 (여러 방법 시도)"""
        try:
            nav = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "새로운 연락처")
            nav.click()
            print("  [KB] NavigationBar 탭으로 키보드 숨김")
        except Exception:
            print("  [KB] 키보드 숨기기 실패 (무시)")
        time.sleep(0.5)

    def _delete_contact_if_exists(self, driver, full_name):
        """테스트 데이터 정리: 연락처가 있으면 삭제"""
        try:
            driver.implicitly_wait(3)
            contact = driver.find_element(AppiumBy.ACCESSIBILITY_ID, full_name)
            contact.click()
            time.sleep(1)

            # 편집 버튼
            self._wait_and_tap(driver, "편집")
            time.sleep(1)

            # 스크롤 다운하여 삭제 버튼 찾기
            driver.execute_script("mobile: scroll", {"direction": "down"})
            time.sleep(0.5)
            driver.execute_script("mobile: scroll", {"direction": "down"})
            time.sleep(0.5)

            # 연락처 삭제 버튼
            self._wait_and_tap(driver, "연락처 삭제")
            time.sleep(0.5)

            # 확인 팝업에서 삭제 선택
            self._wait_and_tap(driver, "연락처 삭제")
            time.sleep(1)
            print(f"  [CLEANUP] '{full_name}' 연락처 삭제 완료")
        except Exception:
            print(f"  [CLEANUP] '{full_name}' 연락처 없음 (정리 불필요)")
        finally:
            driver.implicitly_wait(10)

    # =========================================================================
    # 테스트 시나리오
    # =========================================================================

    @allure.feature("iOS 연락처")
    @allure.story("연락처 추가 및 조회")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("연락처 추가 → 정보 입력 → 저장 → 조회 검증")
    @allure.description("iOS 연락처 앱에서 새 연락처를 추가하고 저장된 정보를 검증하는 시나리오")
    def test_add_and_verify_contact(self, contacts_driver):
        """
        시나리오: 연락처 추가 → 정보 입력 → 저장 → 조회 검증

        1. 연락처 앱 실행 확인
        2. 기존 테스트 데이터 정리
        3. 새 연락처 추가 화면 진입
        4. 이름/성/직장/전화번호 입력
        5. 저장 (완료 버튼)
        6. 저장된 연락처 조회 및 검증
        7. 테스트 데이터 정리
        """
        driver = contacts_driver

        # --- Step 1: 연락처 앱 실행 확인 ---
        with allure.step("연락처 앱 실행 확인"):
            print("\n[Step 1] 연락처 앱 실행 확인")
            assert driver is not None
            print("  [PASS] 연락처 앱 실행 중")

        # --- Step 2: 기존 테스트 데이터 정리 ---
        with allure.step("기존 테스트 데이터 정리"):
            print("\n[Step 2] 기존 테스트 데이터 정리")
            self._delete_contact_if_exists(driver, FULL_NAME)

        # --- Step 3: 새 연락처 추가 화면 진입 ---
        with allure.step("새 연락처 추가 화면 진입"):
            print("\n[Step 3] 새 연락처 추가 화면 진입")
            self._wait_and_tap(driver, "추가")
            time.sleep(2)

            # "새로운 연락처" 네비게이션 바 확인
            assert self._is_element_present(driver, "새로운 연락처"), "새로운 연락처 화면 미표시"
            print("  [PASS] '새로운 연락처' 화면 진입 완료")

        # --- Step 4: 연락처 정보 입력 ---
        with allure.step(f"성 입력: '{TEST_CONTACT['last_name']}'"):
            self._input_text_field(driver, "성", TEST_CONTACT["last_name"])

        with allure.step(f"이름 입력: '{TEST_CONTACT['first_name']}'"):
            self._input_text_field(driver, "이름", TEST_CONTACT["first_name"])

        with allure.step(f"직장 입력: '{TEST_CONTACT['company']}'"):
            self._input_text_field(driver, "직장", TEST_CONTACT["company"])

        with allure.step(f"전화번호 입력: '{TEST_CONTACT['phone']}'"):
            print("  [INFO] 전화번호 입력 중...")
            self._wait_and_tap(driver, "전화번호 추가")
            time.sleep(0.5)

            # "휴대전화" TextField에 입력
            phone_xpath = "//XCUIElementTypeTextField[@name='휴대전화']"
            phone_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, phone_xpath))
            )
            phone_field.send_keys(TEST_CONTACT["phone"])
            print(f"  [INPUT] '휴대전화' → '{TEST_CONTACT['phone']}'")
            time.sleep(0.3)

        with allure.step("키보드 닫기"):
            self._dismiss_keyboard(driver)

        # --- Step 5: 저장 ---
        with allure.step("완료 버튼 클릭 (저장)"):
            print("\n[Step 5] 연락처 저장")
            done_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "완료"))
            )
            print(f"  [INFO] 완료 버튼 - displayed={done_btn.is_displayed()}, enabled={done_btn.is_enabled()}")
            done_btn.click()
            time.sleep(3)

        with allure.step("저장 성공 확인"):
            source_after = driver.page_source
            assert "새로운 연락처" not in source_after, \
                "저장 실패: 아직 '새로운 연락처' 화면에 있습니다"
            print("  [PASS] 저장 완료 - 상세 화면으로 이동됨")

        # --- Step 6: 저장된 연락처 조회 ---
        with allure.step(f"직장 '{TEST_CONTACT['company']}' 확인"):
            page_source = driver.page_source
            assert TEST_CONTACT["company"] in page_source, \
                "직장이 상세 화면에 표시되지 않습니다"
            print(f"  [PASS] 직장 '{TEST_CONTACT['company']}' 확인")

        with allure.step(f"전화번호 '{TEST_CONTACT['phone']}' 확인"):
            source_digits = "".join(c for c in page_source if c.isdigit())
            assert TEST_CONTACT["phone"] in source_digits, \
                "전화번호가 상세 화면에 표시되지 않습니다"
            print(f"  [PASS] 전화번호 '{TEST_CONTACT['phone']}' 확인")

        with allure.step("목록에서 연락처 존재 확인"):
            # 뒤로가기하여 목록에서 확인
            try:
                back = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "BackButton")
                back.click()
                time.sleep(1)
            except Exception:
                pass

            assert self._is_element_present(driver, FULL_NAME, timeout=10), \
                f"'{FULL_NAME}' 연락처를 목록에서 찾을 수 없습니다"
            print(f"  [PASS] '{FULL_NAME}' 연락처가 목록에 존재합니다")

        print("\n" + "=" * 50)
        print("  전체 시나리오 성공!")
        print("=" * 50)

        # --- Step 7: 테스트 데이터 정리 ---
        with allure.step("테스트 데이터 삭제"):
            print("\n[Step 7] 테스트 데이터 삭제")
            self._delete_contact_if_exists(driver, FULL_NAME)
