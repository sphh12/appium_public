import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestAndroidSample:


    def test_Languague_settings(self, android_driver):

        # 언어 변경
        el3 = android_driver.find_element(by=AppiumBy.ID, value="com.gmeremit.online.gmeremittance_native.stag:id/selectedLanguageText")
        el3.click()

        el4 = android_driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().className(\"android.view.ViewGroup\").instance(1)")
        el4.click()

        el5 = android_driver.find_element(by=AppiumBy.ID, value="android:id/content")
        el5.click()


    def test_Login(self, android_driver):

        # 로그인 화면 진입
        el6 = android_driver.find_element(by=AppiumBy.ID, value="com.gmeremit.online.gmeremittance_native.stag:id/btn_lgn")
        el6.click()

        el7 = android_driver.find_element(by=AppiumBy.ID, value="com.gmeremit.online.gmeremittance_native.stag:id/usernameId")
        el7.send_keys("gme_qualitytest44")
       
        el8 = android_driver.find_element(by=AppiumBy.ID, value="com.gmeremit.online.gmeremittance_native.stag:id/securityKeyboardEditText")
        # el8 = android_driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="********")
        el8.send_keys("123456")

        # 빈곳 클릭
        e20 = android_driver.find_element(by=AppiumBy.ID, value="com.gmeremit.online.gmeremittance_native.stag:id/toolbarLayout")
        e20.click()

        # 로그인 시도
        el9 = android_driver.find_element(by=AppiumBy.ID, value="com.gmeremit.online.gmeremittance_native.stag:id/btn_submit")
        el9.click()

    def test_password_empty_error(self, android_driver):
        """비밀번호 미입력 시 에러 메시지 확인"""

        # 로그인 화면 진입
        login_btn = android_driver.find_element(by=AppiumBy.ID, value="com.gmeremit.online.gmeremittance_native.stag:id/btn_lgn")
        login_btn.click()

        # 아이디만 입력 (비밀번호는 입력하지 않음)
        username = android_driver.find_element(by=AppiumBy.ID, value="com.gmeremit.online.gmeremittance_native.stag:id/usernameId")
        username.send_keys("gme_qualitytest44")

        # 로그인 시도
        submit_btn = android_driver.find_element(by=AppiumBy.ID, value="com.gmeremit.online.gmeremittance_native.stag:id/btn_submit")
        submit_btn.click()

        # 에러 메시지 확인
        error_text = WebDriverWait(android_driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, "com.gmeremit.online.gmeremittance_native.stag:id/passwordErrorTxt"))
        )

        assert error_text.text == "Password cannot be empty", f"Expected 'Password cannot be empty' but got '{error_text.text}'"
