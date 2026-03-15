"""
샘플 페이지 클래스
실제 앱에 맞게 수정하여 사용하세요
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class SampleLoginPage(BasePage):
    """로그인 페이지 예제"""

    # Locators (앱에 맞게 수정 필요)
    USERNAME_FIELD = (AppiumBy.ID, "username")  # Android: resource-id
    PASSWORD_FIELD = (AppiumBy.ID, "password")
    LOGIN_BUTTON = (AppiumBy.ID, "login_button")
    ERROR_MESSAGE = (AppiumBy.ID, "error_text")

    # iOS용 Locators
    USERNAME_FIELD_IOS = (AppiumBy.ACCESSIBILITY_ID, "username_field")
    PASSWORD_FIELD_IOS = (AppiumBy.ACCESSIBILITY_ID, "password_field")
    LOGIN_BUTTON_IOS = (AppiumBy.ACCESSIBILITY_ID, "login_button")

    def enter_username(self, username: str):
        """사용자명 입력"""
        self.input_text(self.USERNAME_FIELD, username)

    def enter_password(self, password: str):
        """비밀번호 입력"""
        self.input_text(self.PASSWORD_FIELD, password)

    def click_login(self):
        """로그인 버튼 클릭"""
        self.click(self.LOGIN_BUTTON)

    def login(self, username: str, password: str):
        """로그인 수행"""
        self.enter_username(username)
        self.enter_password(password)
        self.hide_keyboard()
        self.click_login()

    def get_error_message(self) -> str:
        """에러 메시지 가져오기"""
        return self.get_text(self.ERROR_MESSAGE)

    def is_login_page_displayed(self) -> bool:
        """로그인 페이지가 표시되는지 확인"""
        return self.is_element_visible(self.LOGIN_BUTTON)
