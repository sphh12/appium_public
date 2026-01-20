import pytest
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestAndroidSample:

    @allure.feature("설정")
    @allure.story("언어 변경")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("언어 설정 변경")
    @allure.description("앱 내 언어 선택 UI를 통해 언어를 변경한다")
    def test_Languague_settings(self, android_driver):

        with allure.step("언어 선택 메뉴 열기"):
            el3 = android_driver.find_element(
                by=AppiumBy.ID,
                value="com.gmeremit.online.gmeremittance_native.stag:id/selectedLanguageText",
            )
            el3.click()

        with allure.step("언어 항목 선택"):
            el4 = android_driver.find_element(
                by=AppiumBy.ANDROID_UIAUTOMATOR,
                value='new UiSelector().className("android.view.ViewGroup").instance(1)',
            )
            el4.click()

        with allure.step("화면 닫기"):
            el5 = android_driver.find_element(by=AppiumBy.ID, value="android:id/content")
            el5.click()

    @allure.feature("인증")
    @allure.story("정상 로그인")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("유효한 계정으로 로그인")
    @allure.description("아이디/비밀번호 입력 후 로그인 버튼을 눌러 로그인 시도를 수행한다")
    def test_Login(self, android_driver):

        with allure.step("로그인 화면 진입"):
            el6 = android_driver.find_element(
                by=AppiumBy.ID,
                value="com.gmeremit.online.gmeremittance_native.stag:id/btn_lgn",
            )
            el6.click()

        with allure.step("아이디 입력"):
            el7 = android_driver.find_element(
                by=AppiumBy.ID,
                value="com.gmeremit.online.gmeremittance_native.stag:id/usernameId",
            )
            el7.send_keys("gme_qualitytest44")

        with allure.step("비밀번호 입력"):
            el8 = android_driver.find_element(
                by=AppiumBy.ID,
                value="com.gmeremit.online.gmeremittance_native.stag:id/securityKeyboardEditText",
            )
            el8.click()  # 키보드 활성화

            # 보안 키보드에서 각 숫자 버튼 클릭 (content-desc로 찾기)
            for digit in "123456":
                btn = android_driver.find_element(
                    by=AppiumBy.ACCESSIBILITY_ID,
                    value=digit
                )
                btn.click()

            # COMPLETE 버튼 클릭
            complete_btn = android_driver.find_element(
                by=AppiumBy.ACCESSIBILITY_ID,
                value="입력완료"
            )
            complete_btn.click()

        with allure.step("키보드 닫기(빈곳 클릭)"):
            e20 = android_driver.find_element(
                by=AppiumBy.ID,
                value="com.gmeremit.online.gmeremittance_native.stag:id/toolbarLayout",
            )
            e20.click()

        with allure.step("로그인 시도"):
            el9 = android_driver.find_element(
                by=AppiumBy.ID,
                value="com.gmeremit.online.gmeremittance_native.stag:id/btn_submit",
            )
            el9.click()

    @allure.feature("인증")
    @allure.story("유효성 검증")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("비밀번호 미입력 시 에러 메시지")
    @allure.description("아이디만 입력하고 로그인 시도 시 비밀번호 에러 메시지가 노출되는지 확인")
    def test_password_empty_error(self, android_driver):
        """비밀번호 미입력 시 에러 메시지 확인"""

        with allure.step("로그인 화면 진입"):
            login_btn = android_driver.find_element(
                by=AppiumBy.ID,
                value="com.gmeremit.online.gmeremittance_native.stag:id/btn_lgn",
            )
            login_btn.click()

        with allure.step("아이디만 입력"):
            username = android_driver.find_element(
                by=AppiumBy.ID,
                value="com.gmeremit.online.gmeremittance_native.stag:id/usernameId",
            )
            username.send_keys("gme_qualitytest44")

        with allure.step("로그인 시도"):
            submit_btn = android_driver.find_element(
                by=AppiumBy.ID,
                value="com.gmeremit.online.gmeremittance_native.stag:id/btn_submit",
            )
            submit_btn.click()

        with allure.step("에러 메시지 확인"):
            error_text = WebDriverWait(android_driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, "com.gmeremit.online.gmeremittance_native.stag:id/passwordErrorTxt")
                )
            )

        assert error_text.text == "Password cannot be empty", (
            f"Expected 'Password cannot be empty' but got '{error_text.text}'"
        )
