import time
import pytest
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class TestXmlScenario:
    """XML 파일 분석 기반 테스트 시나리오

    UI dump XML 파일에서 추출한 요소 정보를 활용하여
    1. 홈화면에서 GME 앱 실행
    2. 로그인 화면 진입
    3. 로그인 화면의 클릭 가능한 모든 요소 클릭

    Locator 전략:
    - 1순위: Accessibility ID (content-desc)
    - 2순위: Resource ID (resource-id)
    """

    # 앱 패키지 ID
    PACKAGE_ID = "com.gmeremit.online.gmeremittance_native.stag:id"

    # 로그인 화면의 클릭 가능한 요소들 (005.xml에서 추출)
    # accessibility_id: content-desc 값 (있는 경우)
    # id: resource-id 값 (fallback)
    LOGIN_SCREEN_CLICKABLE_ELEMENTS = [
        {
            "accessibility_id": None,
            "id": "usernameId",
            "name": "User ID 입력란",
            "type": "EditText"
        },
        {
            "accessibility_id": "********",  # 마스킹된 값이라 사용 불가
            "id": "securityKeyboardEditText",
            "name": "Password 입력란",
            "type": "EditText"
        },
        {
            "accessibility_id": None,
            "id": "btn_submit",
            "name": "Login 버튼",
            "type": "Button"
        },
        {
            "accessibility_id": None,
            "id": "tvFindUserId",
            "name": "Find my User ID 링크",
            "type": "TextView"
        },
        {
            "accessibility_id": None,
            "id": "tv_forgotpass",
            "name": "Forgot Password 링크",
            "type": "TextView"
        },
        {
            "accessibility_id": None,
            "id": "register",
            "name": "Register Here 링크",
            "type": "TextView"
        },
        {
            "accessibility_id": "Customer Support",  # 유일하게 유효한 content-desc
            "id": "ivChannelTalk",
            "name": "Customer Support 아이콘",
            "type": "ImageView"
        },
    ]

    def _handle_initial_screens(self, driver):
        """
        앱 초기 화면들(언어 선택, 약관 동의)을 자동으로 처리

        처리하는 화면:
        1. 언어 선택 화면 (003.xml) - English 선택
        2. 약관 동의 화면 (004.xml) - 전체 동의 후 스크롤하여 다음 진행
        """
        max_attempts = 3

        for attempt in range(max_attempts):
            # 이미 메인 화면인지 확인
            if self._is_main_screen(driver):
                return True

            # 이미 로그인 화면인지 확인
            if self._is_login_screen(driver):
                return True

            # 1. 언어 선택 화면 처리
            if self._handle_language_selection(driver):
                time.sleep(2)
                continue

            # 2. 약관 동의 화면 처리
            if self._handle_terms_and_conditions(driver):
                time.sleep(2)
                continue

            # 알 수 없는 화면이면 잠시 대기
            time.sleep(2)

        return self._is_main_screen(driver) or self._is_login_screen(driver)

    def _is_main_screen(self, driver):
        """메인 화면(Login 버튼이 있는 화면)인지 확인"""
        try:
            driver.find_element(
                by=AppiumBy.ID,
                value=f"{self.PACKAGE_ID}/btn_lgn"
            )
            return True
        except NoSuchElementException:
            return False

    def _is_login_screen(self, driver):
        """로그인 화면인지 확인"""
        try:
            driver.find_element(
                by=AppiumBy.ID,
                value=f"{self.PACKAGE_ID}/usernameId"
            )
            return True
        except NoSuchElementException:
            return False

    def _handle_language_selection(self, driver):
        """
        언어 선택 화면 처리 (003.xml 기반)
        - languageRv (RecyclerView)가 있으면 언어 선택 화면
        - English를 선택
        """
        try:
            # 언어 선택 화면 확인 (languageRv 또는 selectedLanguageText)
            driver.find_element(
                by=AppiumBy.ID,
                value=f"{self.PACKAGE_ID}/languageRv"
            )

            # English 선택 (첫 번째 언어 항목 또는 text="English")
            try:
                english_item = driver.find_element(
                    by=AppiumBy.ANDROID_UIAUTOMATOR,
                    value='new UiSelector().text("English")'
                )
                english_item.click()
                allure.attach(
                    "언어 선택 화면에서 English 선택",
                    name="language_selection",
                    attachment_type=allure.attachment_type.TEXT
                )
                return True
            except NoSuchElementException:
                # English를 못 찾으면 첫 번째 항목 클릭
                first_language = driver.find_element(
                    by=AppiumBy.ID,
                    value=f"{self.PACKAGE_ID}/countryLanguageText"
                )
                first_language.click()
                return True

        except NoSuchElementException:
            return False

    def _handle_terms_and_conditions(self, driver):
        """
        약관 동의 화면 처리 (004.xml 기반)
        - screenTitle이 "Terms And Condition"이면 약관 화면
        - agreeAllContainer 클릭하여 전체 동의
        - 스크롤 후 다음 버튼 클릭 (있으면)
        """
        try:
            # 약관 화면 확인 (screenTitle 또는 agreeAllContainer)
            screen_title = driver.find_element(
                by=AppiumBy.ID,
                value=f"{self.PACKAGE_ID}/screenTitle"
            )

            if "Terms" not in screen_title.text:
                return False

            # 전체 동의 클릭
            try:
                agree_all = driver.find_element(
                    by=AppiumBy.ID,
                    value=f"{self.PACKAGE_ID}/agreeAllContainer"
                )
                agree_all.click()
                time.sleep(1)
                allure.attach(
                    "약관 화면에서 전체 동의 클릭",
                    name="terms_agree_all",
                    attachment_type=allure.attachment_type.TEXT
                )
            except NoSuchElementException:
                pass

            # 화면 스크롤 (다음 버튼이 아래에 있을 수 있음)
            try:
                driver.swipe(540, 1800, 540, 800, 500)
                time.sleep(1)
            except Exception:
                pass

            # 다음/확인 버튼 찾기 (여러 가능한 ID 시도)
            next_button_ids = ["btnNext", "btn_next", "btnConfirm", "btn_confirm", "btnSubmit"]
            for btn_id in next_button_ids:
                try:
                    next_btn = driver.find_element(
                        by=AppiumBy.ID,
                        value=f"{self.PACKAGE_ID}/{btn_id}"
                    )
                    next_btn.click()
                    return True
                except NoSuchElementException:
                    continue

            # 버튼을 못 찾으면 텍스트로 시도
            try:
                next_btn = driver.find_element(
                    by=AppiumBy.ANDROID_UIAUTOMATOR,
                    value='new UiSelector().textContains("Next").clickable(true)'
                )
                next_btn.click()
                return True
            except NoSuchElementException:
                pass

            try:
                next_btn = driver.find_element(
                    by=AppiumBy.ANDROID_UIAUTOMATOR,
                    value='new UiSelector().textContains("Confirm").clickable(true)'
                )
                next_btn.click()
                return True
            except NoSuchElementException:
                pass

            return True  # 전체 동의는 클릭했으므로 True

        except NoSuchElementException:
            return False

    def find_element_with_fallback(self, driver, element_info, timeout=5):
        """
        Accessibility ID를 1순위로 시도하고, 실패 시 Resource ID로 fallback

        Args:
            driver: Appium WebDriver
            element_info: 요소 정보 dict (accessibility_id, id, name, type)
            timeout: 대기 시간 (초)

        Returns:
            찾은 요소 또는 None
        """
        accessibility_id = element_info.get("accessibility_id")
        resource_id = element_info.get("id")
        element_name = element_info.get("name", "Unknown")

        # 1순위: Accessibility ID 시도
        if accessibility_id and accessibility_id != "********":
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located(
                        (AppiumBy.ACCESSIBILITY_ID, accessibility_id)
                    )
                )
                allure.attach(
                    f"Accessibility ID로 찾음: {accessibility_id}",
                    name=f"locator_{element_name}",
                    attachment_type=allure.attachment_type.TEXT
                )
                return element
            except (NoSuchElementException, TimeoutException):
                pass  # fallback으로 진행

        # 2순위: Resource ID 시도
        if resource_id:
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located(
                        (AppiumBy.ID, f"{self.PACKAGE_ID}/{resource_id}")
                    )
                )
                allure.attach(
                    f"Resource ID로 찾음: {resource_id}",
                    name=f"locator_{element_name}",
                    attachment_type=allure.attachment_type.TEXT
                )
                return element
            except (NoSuchElementException, TimeoutException):
                pass

        # 둘 다 실패
        return None

    @allure.feature("UI 탐색")
    @allure.story("홈에서 앱 실행")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("홈화면에서 GME 앱 실행")
    @allure.description("안드로이드 홈화면에서 GME Remit 앱을 찾아 실행한다")
    def test_01_launch_app_from_home(self, android_driver):
        """홈화면에서 GME 앱 실행"""

        # 초기 화면 처리 (언어 선택, 약관 동의 등)
        with allure.step("초기 화면 처리 (언어 선택, 약관 동의)"):
            self._handle_initial_screens(android_driver)

        with allure.step("홈 버튼 눌러 홈화면으로 이동"):
            android_driver.press_keycode(3)  # KEYCODE_HOME
            time.sleep(1)

        with allure.step("GME Remit 앱 아이콘 찾기"):
            # 1순위: Accessibility ID (content-desc)
            try:
                gme_app = WebDriverWait(android_driver, 10).until(
                    EC.presence_of_element_located(
                        (AppiumBy.ACCESSIBILITY_ID, "GME Remit")
                    )
                )
                allure.attach(
                    "Accessibility ID로 찾음: GME Remit",
                    name="locator_gme_app",
                    attachment_type=allure.attachment_type.TEXT
                )
            except TimeoutException:
                # 2순위: UiAutomator로 descriptionContains 사용
                gme_app = android_driver.find_element(
                    by=AppiumBy.ANDROID_UIAUTOMATOR,
                    value='new UiSelector().descriptionContains("GME")'
                )
                allure.attach(
                    "UiAutomator descriptionContains로 찾음",
                    name="locator_gme_app",
                    attachment_type=allure.attachment_type.TEXT
                )

        with allure.step("GME 앱 실행"):
            gme_app.click()
            time.sleep(3)  # 앱 로딩 대기

        # 앱 실행 후 초기 화면 다시 처리
        with allure.step("앱 실행 후 초기 화면 처리"):
            self._handle_initial_screens(android_driver)

        with allure.step("앱 실행 확인"):
            # 메인 화면의 Login 버튼이 보이는지 확인 (002.xml)
            login_btn = WebDriverWait(android_driver, 15).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, f"{self.PACKAGE_ID}/btn_lgn")
                )
            )
            assert login_btn.is_displayed(), "앱이 정상적으로 실행되지 않았습니다"

    @allure.feature("UI 탐색")
    @allure.story("로그인 화면 진입")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("로그인 화면으로 이동")
    @allure.description("메인 화면에서 로그인 버튼을 클릭하여 로그인 화면으로 진입한다")
    def test_02_navigate_to_login(self, android_driver):
        """로그인 화면 진입"""

        # 초기 화면 처리
        with allure.step("초기 화면 처리"):
            self._handle_initial_screens(android_driver)

        with allure.step("Login 버튼 클릭"):
            login_btn = WebDriverWait(android_driver, 15).until(
                EC.element_to_be_clickable(
                    (AppiumBy.ID, f"{self.PACKAGE_ID}/btn_lgn")
                )
            )
            login_btn.click()
            time.sleep(2)

        with allure.step("로그인 화면 진입 확인"):
            # User ID 입력란이 보이는지 확인 (005.xml)
            username_field = WebDriverWait(android_driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, f"{self.PACKAGE_ID}/usernameId")
                )
            )
            assert username_field.is_displayed(), "로그인 화면으로 진입하지 못했습니다"

    @allure.feature("UI 탐색")
    @allure.story("로그인 화면 요소 클릭")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("로그인 화면 클릭 가능 요소 테스트")
    @allure.description("로그인 화면의 모든 클릭 가능한 요소를 순서대로 클릭하여 반응을 확인한다 (Accessibility ID 우선, Resource ID fallback)")
    def test_03_click_all_login_elements(self, android_driver):
        """로그인 화면의 클릭 가능한 모든 요소 클릭"""

        # 초기 화면 처리 및 로그인 화면으로 진입
        with allure.step("초기 화면 처리 및 로그인 화면으로 진입"):
            self._handle_initial_screens(android_driver)
            self._navigate_to_login_screen(android_driver)

        clicked_elements = []
        failed_elements = []

        for element_info in self.LOGIN_SCREEN_CLICKABLE_ELEMENTS:
            element_name = element_info["name"]
            element_type = element_info["type"]

            with allure.step(f"{element_name} ({element_type}) 클릭"):
                try:
                    # 먼저 로그인 화면으로 돌아가기 (다른 화면으로 이동한 경우)
                    self._ensure_login_screen(android_driver)

                    # Accessibility ID 우선, Resource ID fallback으로 요소 찾기
                    element = self.find_element_with_fallback(android_driver, element_info)

                    if element is None:
                        raise NoSuchElementException(f"요소를 찾을 수 없음: {element_name}")

                    # 클릭
                    element.click()
                    time.sleep(1)

                    # 스크린샷 첨부
                    allure.attach(
                        android_driver.get_screenshot_as_png(),
                        name=f"after_click_{element_info['id']}",
                        attachment_type=allure.attachment_type.PNG
                    )

                    clicked_elements.append(element_name)

                    # EditText의 경우 키보드 닫기
                    if element_type == "EditText":
                        try:
                            android_driver.hide_keyboard()
                        except Exception:
                            pass  # 키보드가 없으면 무시
                        time.sleep(0.5)

                except (NoSuchElementException, TimeoutException) as e:
                    failed_elements.append(f"{element_name}: {str(e)}")
                    allure.attach(
                        f"요소를 찾을 수 없음: {element_name}\n"
                        f"Accessibility ID: {element_info.get('accessibility_id')}\n"
                        f"Resource ID: {element_info.get('id')}\n"
                        f"에러: {str(e)}",
                        name=f"error_{element_info['id']}",
                        attachment_type=allure.attachment_type.TEXT
                    )

        # 결과 요약
        with allure.step("클릭 테스트 결과 요약"):
            summary = f"성공: {len(clicked_elements)}개, 실패: {len(failed_elements)}개\n"
            summary += f"\n성공한 요소:\n" + "\n".join(f"  - {e}" for e in clicked_elements)
            if failed_elements:
                summary += f"\n\n실패한 요소:\n" + "\n".join(f"  - {e}" for e in failed_elements)

            allure.attach(summary, name="click_test_summary", attachment_type=allure.attachment_type.TEXT)
            print(summary)

        # 모든 요소가 클릭 가능해야 테스트 통과
        assert len(failed_elements) == 0, f"클릭 실패한 요소: {failed_elements}"

    def _navigate_to_login_screen(self, driver):
        """로그인 화면으로 이동 (메인 화면에서 Login 버튼 클릭)"""
        # 이미 로그인 화면인지 확인
        if self._is_login_screen(driver):
            return

        # 메인 화면에서 Login 버튼 클릭
        try:
            login_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (AppiumBy.ID, f"{self.PACKAGE_ID}/btn_lgn")
                )
            )
            login_btn.click()
            time.sleep(2)

            # 로그인 화면 진입 확인
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, f"{self.PACKAGE_ID}/usernameId")
                )
            )
        except TimeoutException:
            raise Exception("로그인 화면으로 진입할 수 없습니다")

    def _ensure_login_screen(self, driver):
        """로그인 화면에 있는지 확인하고, 아니면 뒤로가기로 돌아가기"""
        if self._is_login_screen(driver):
            return

        # 로그인 화면이 아니면 뒤로가기
        driver.back()
        time.sleep(1)

        # 다시 확인
        if self._is_login_screen(driver):
            return

        # 그래도 없으면 로그인 화면으로 다시 진입 시도
        try:
            self._navigate_to_login_screen(driver)
        except Exception:
            pass