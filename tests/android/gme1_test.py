import os
import time

import pytest
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

from utils.auth import login, navigate_to_login_screen

# 환경변수 로드
load_dotenv()

# 환경변수에서 설정 로드
TEST_USERNAME = os.getenv("STG_ID", "")
RESOURCE_ID_PREFIX = os.getenv("GME_RESOURCE_ID_PREFIX", "com.gmeremit.online.gmeremittance_native.stag:id")


class TestAndroidSample:

    @allure.feature("설정")             # 1 Depth
    @allure.story("언어 변경")          # 2 Depth
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("언어 설정 변경")     # 3 Depth
    @allure.description("앱 내 언어 선택 UI를 통해 언어를 변경한다")
    def test_Languague_settings(self, android_driver):

        with allure.step("언어 선택 메뉴 열기"):
            el3 = android_driver.find_element(
                by=AppiumBy.ID,
                value=f"{RESOURCE_ID_PREFIX}/selectedLanguageText",
            )
            el3.click()

        with allure.step("언어 항목 선택"):
            el4 = android_driver.find_element(
                by=AppiumBy.ANDROID_UIAUTOMATOR,
                value='new UiSelector().className("android.view.ViewGroup").instance(1)',
            )
            el4.click()

        with allure.step("화면 닫기"):
            # 언어 선택 후 화면 갱신 대기
            time.sleep(1)
            # 뒤로가기 버튼으로 화면 닫기 (더 안정적)
            android_driver.back()




    @allure.feature("인증")                    # 1 Depth
    @allure.story("정상 로그인")               # 2 Depth
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("유효한 계정으로 로그인")    # 3 Depth
    @allure.description("아이디/비밀번호 입력 후 로그인 버튼을 눌러 로그인 시도를 수행한다")
    def test_Login(self, android_driver):
        login(android_driver)

    @allure.feature("인증")
    @allure.story("유효성 검증")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("비밀번호 미입력 시 에러 메시지")
    @allure.description("아이디만 입력하고 로그인 시도 시 비밀번호 에러 메시지가 노출되는지 확인")
    def test_password_empty_error(self, android_driver):
        """비밀번호 미입력 시 에러 메시지 확인"""

        with allure.step("로그인 화면 진입"):
            navigate_to_login_screen(android_driver)

        with allure.step("아이디만 입력"):
            username = android_driver.find_element(
                by=AppiumBy.ID,
                value=f"{RESOURCE_ID_PREFIX}/usernameId",
            )
            username.send_keys(TEST_USERNAME)

        with allure.step("로그인 시도"):
            submit_btn = android_driver.find_element(
                by=AppiumBy.ID,
                value=f"{RESOURCE_ID_PREFIX}/btn_submit",
            )
            submit_btn.click()

        with allure.step("에러 메시지 확인"):
            error_text = WebDriverWait(android_driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, f"{RESOURCE_ID_PREFIX}/passwordErrorTxt")
                )
            )

        assert error_text.text == "Password cannot be empty", (
            f"Expected 'Password cannot be empty' but got '{error_text.text}'"
        )
