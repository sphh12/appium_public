"""
Android 샘플 테스트
실제 앱에 맞게 수정하여 사용하세요
"""
import pytest
from appium.webdriver.common.appiumby import AppiumBy


class TestAndroidSample:
    """Android 샘플 테스트 클래스"""

    def test_app_launches(self, android_driver):
        """앱이 정상적으로 실행되는지 확인"""
        # 앱이 실행되면 드라이버가 생성됨
        assert android_driver is not None
        print("앱이 성공적으로 실행되었습니다.")

    def test_get_page_source(self, android_driver):
        """페이지 소스 가져오기 테스트"""
        page_source = android_driver.page_source
        assert page_source is not None
        assert len(page_source) > 0

    def test_screen_size(self, android_driver):
        """화면 크기 확인"""
        size = android_driver.get_window_size()
        assert size['width'] > 0
        assert size['height'] > 0
        print(f"화면 크기: {size['width']} x {size['height']}")

    @pytest.mark.skip(reason="앱에 맞게 locator 수정 필요")
    def test_find_element_by_id(self, android_driver):
        """ID로 요소 찾기 예제"""
        # 실제 앱의 resource-id로 수정하세요
        element = android_driver.find_element(
            AppiumBy.ID, "com.example.app:id/button"
        )
        assert element is not None

    @pytest.mark.skip(reason="앱에 맞게 locator 수정 필요")
    def test_find_element_by_xpath(self, android_driver):
        """XPath로 요소 찾기 예제"""
        element = android_driver.find_element(
            AppiumBy.XPATH, "//android.widget.Button[@text='확인']"
        )
        assert element is not None

    @pytest.mark.skip(reason="앱에 맞게 locator 수정 필요")
    def test_click_and_input(self, android_driver):
        """클릭 및 입력 테스트 예제"""
        # 입력 필드 찾아서 텍스트 입력
        input_field = android_driver.find_element(
            AppiumBy.ID, "com.example.app:id/input_field"
        )
        input_field.send_keys("테스트 입력")

        # 버튼 클릭
        button = android_driver.find_element(
            AppiumBy.ID, "com.example.app:id/submit_button"
        )
        button.click()

    def test_take_screenshot(self, android_driver):
        """스크린샷 테스트"""
        result = android_driver.save_screenshot("reports/android_screenshot.png")
        # 스크린샷 저장 성공 여부는 파일 생성으로 확인
        print("스크린샷이 저장되었습니다.")
