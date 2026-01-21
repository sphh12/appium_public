"""
크로스 플랫폼 테스트
--platform 옵션으로 Android/iOS 선택 가능
"""
import pytest
from pages.sample_page import SampleLoginPage


class TestCrossPlatform:
    """크로스 플랫폼 테스트 클래스"""

    def test_app_launches(self, driver, platform):
        """앱 실행 테스트"""
        assert driver is not None
        print(f"{platform.upper()} 앱이 성공적으로 실행되었습니다.")

    def test_screen_orientation(self, driver):
        """화면 방향 테스트"""
        # 현재 방향 확인
        orientation = driver.orientation
        assert orientation in ["PORTRAIT", "LANDSCAPE"]
        print(f"현재 화면 방향: {orientation}")

    def test_context_check(self, driver):
        """현재 컨텍스트 확인"""
        context = driver.current_context
        print(f"현재 컨텍스트: {context}")
        # 네이티브 앱은 NATIVE_APP 컨텍스트
        assert context is not None

    @pytest.mark.skip(reason="앱에 맞게 수정 필요")
    def test_login_flow(self, driver):
        """로그인 플로우 테스트 예제"""
        login_page = SampleLoginPage(driver)

        # 로그인 페이지 확인
        assert login_page.is_login_page_displayed()

        # 로그인 수행
        login_page.login("testuser", "testpass")

        # 결과 확인 (앱에 맞게 수정)
        # assert some_condition

    @pytest.mark.skip(reason="앱에 맞게 수정 필요")
    def test_navigation(self, driver):
        """네비게이션 테스트 예제"""
        # 특정 화면으로 이동 후 뒤로가기
        driver.back()
