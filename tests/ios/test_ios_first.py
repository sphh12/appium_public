"""
iOS 시뮬레이터 첫 동작 확인 테스트
Safari 브라우저를 사용하여 Appium ↔ iOS 연결을 검증합니다.
"""
import pytest
from appium import webdriver
from appium.options.ios import XCUITestOptions
from config.capabilities import get_appium_server_url


class TestiOSFirstRun:
    """iOS 시뮬레이터 첫 실행 테스트"""

    @pytest.fixture(scope="function")
    def safari_driver(self):
        """Safari 브라우저로 연결하는 드라이버 (앱 없이 테스트 가능)"""
        caps = {
            "platformName": "iOS",
            "automationName": "XCUITest",
            "deviceName": "iPhone 17",
            "platformVersion": "26.2",
            "browserName": "Safari",
            "newCommandTimeout": 300,
            # Safari 연결 대기 시간 늘림 (기본 5초 → 30초)
            "webviewConnectTimeout": 30000,
            "safariInitialUrl": "https://www.google.com",
        }
        options = XCUITestOptions().load_capabilities(caps)

        print("[INFO] Appium 서버에 연결 중...")
        driver = webdriver.Remote(
            command_executor=get_appium_server_url(),
            options=options,
        )
        driver.implicitly_wait(10)
        print("[INFO] iOS 시뮬레이터 연결 성공!")

        yield driver

        driver.quit()
        print("[INFO] 드라이버 종료 완료")

    def test_simulator_connection(self, safari_driver):
        """1. 시뮬레이터 연결 확인"""
        assert safari_driver is not None
        print(f"[PASS] 시뮬레이터 연결 성공")

    def test_screen_size(self, safari_driver):
        """2. 화면 크기 확인"""
        size = safari_driver.get_window_size()
        print(f"[INFO] 화면 크기: {size['width']} x {size['height']}")
        assert size["width"] > 0
        assert size["height"] > 0

    def test_open_url(self, safari_driver):
        """3. Safari에서 URL 열기"""
        safari_driver.get("https://www.google.com")
        # 페이지 타이틀 또는 URL 확인
        current_url = safari_driver.current_url
        print(f"[INFO] 현재 URL: {current_url}")
        assert "google" in current_url.lower()

    def test_page_source(self, safari_driver):
        """4. 페이지 소스 가져오기"""
        safari_driver.get("https://www.google.com")
        page_source = safari_driver.page_source
        print(f"[INFO] 페이지 소스 길이: {len(page_source)}")
        assert len(page_source) > 0
