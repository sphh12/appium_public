"""
iOS 샘플 테스트
실제 앱에 맞게 수정하여 사용하세요
Mac에서만 실행 가능합니다.
"""
import pytest
from appium.webdriver.common.appiumby import AppiumBy


class TestiOSSample:
    """iOS 샘플 테스트 클래스"""

    def test_app_launches(self, ios_driver):
        """앱이 정상적으로 실행되는지 확인"""
        assert ios_driver is not None
        print("iOS 앱이 성공적으로 실행되었습니다.")

    def test_get_page_source(self, ios_driver):
        """페이지 소스 가져오기 테스트"""
        page_source = ios_driver.page_source
        assert page_source is not None
        assert len(page_source) > 0

    def test_screen_size(self, ios_driver):
        """화면 크기 확인"""
        size = ios_driver.get_window_size()
        assert size['width'] > 0
        assert size['height'] > 0
        print(f"화면 크기: {size['width']} x {size['height']}")

    @pytest.mark.skip(reason="앱에 맞게 locator 수정 필요")
    def test_find_element_by_accessibility_id(self, ios_driver):
        """Accessibility ID로 요소 찾기 예제"""
        element = ios_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "loginButton"
        )
        assert element is not None

    @pytest.mark.skip(reason="앱에 맞게 locator 수정 필요")
    def test_find_element_by_xpath(self, ios_driver):
        """XPath로 요소 찾기 예제"""
        element = ios_driver.find_element(
            AppiumBy.XPATH, "//XCUIElementTypeButton[@name='확인']"
        )
        assert element is not None

    @pytest.mark.skip(reason="앱에 맞게 locator 수정 필요")
    def test_click_and_input(self, ios_driver):
        """클릭 및 입력 테스트 예제"""
        # 입력 필드 찾아서 텍스트 입력
        input_field = ios_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "usernameField"
        )
        input_field.send_keys("테스트 입력")

        # 버튼 클릭
        button = ios_driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "submitButton"
        )
        button.click()

    def test_take_screenshot(self, ios_driver):
        """스크린샷 테스트"""
        ios_driver.save_screenshot("reports/ios_screenshot.png")
        print("iOS 스크린샷이 저장되었습니다.")
