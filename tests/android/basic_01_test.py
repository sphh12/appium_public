"""
Basic Test 01 - GME Remit 앱 기본 테스트
XML 덤프 기반 화면 검증 (260123_1254)

테스트 대상 화면:
- Easy Wallet Account (022)
- History (023)
- Edit Info (027)
- GMEPay Wallet Guide (030)
"""
import os
import time

import pytest
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

from utils.auth import login

# 환경변수 로드
load_dotenv()

# 환경변수에서 설정 로드
RESOURCE_ID_PREFIX = os.getenv(
    "GME_RESOURCE_ID_PREFIX",
    "com.gmeremit.online.gmeremittance_native.stag:id"
)


class TestBasic01:
    """GME Remit 앱 기본 테스트 - XML 덤프 기반"""

    PACKAGE_ID = RESOURCE_ID_PREFIX

    def find_element_with_fallback(self, driver, accessibility_id=None, resource_id=None, timeout=5):
        """Accessibility ID 우선, Resource ID fallback"""
        if accessibility_id:
            try:
                return WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located(
                        (AppiumBy.ACCESSIBILITY_ID, accessibility_id)
                    )
                )
            except TimeoutException:
                pass

        if resource_id:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, f"{self.PACKAGE_ID}/{resource_id}")
                )
            )
        return None

    # ========== Easy Wallet Account (022) ==========
    @allure.feature("Home")
    @allure.story("Easy Wallet Account")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Easy Wallet Account 화면 요소 검증")
    @allure.description("홈 화면의 Easy Wallet Account 섹션 UI 요소 확인")
    def test_01_easy_wallet_account_elements(self, android_driver):
        """Easy Wallet Account 화면 요소 검증"""

        # (1) 로그인은 모듈(함수)로 수행
        login(android_driver)

        with allure.step("네비게이션 메뉴 버튼 확인"):
            nav_btn = self.find_element_with_fallback(
                android_driver, resource_id="iv_nav"
            )
            assert nav_btn is not None, "네비게이션 버튼이 없음"
            assert nav_btn.is_displayed(), "네비게이션 버튼이 표시되지 않음"

        with allure.step("알림 아이콘 확인"):
            notice_view = self.find_element_with_fallback(
                android_driver, resource_id="noticeView"
            )
            assert notice_view is not None, "알림 아이콘이 없음"

        with allure.step("Easy Wallet Account 섹션 확인"):
            wallet_section = self.find_element_with_fallback(
                android_driver, resource_id="ll_easywallet_account"
            )
            assert wallet_section is not None, "Easy Wallet Account 섹션이 없음"

        with allure.step("Easy Wallet Account 타이틀 확인"):
            wallet_title = self.find_element_with_fallback(
                android_driver, resource_id="tv_easywallet_account_title"
            )
            assert wallet_title is not None, "Easy Wallet 타이틀이 없음"
            assert "Easy Wallet" in wallet_title.text, f"타이틀 불일치: {wallet_title.text}"

    # ========== History (023) ==========
    @allure.feature("History")
    @allure.story("거래 내역")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("History 화면 요소 검증")
    @allure.description("History 탭의 UI 요소 확인")
    def test_02_history_screen_elements(self, android_driver):
        """History 화면 요소 검증"""

        # (2) 로그인은 모듈(함수)로 수행
        login(android_driver)

        with allure.step("하단 네비게이션에서 History 탭 클릭"):
            try:
                history_tab = android_driver.find_element(
                    AppiumBy.XPATH, "//android.widget.TextView[@text='History']"
                )
                history_tab.click()
                time.sleep(2)
            except NoSuchElementException:
                pytest.skip("History 탭을 찾을 수 없음")

        with allure.step("History 타이틀 확인"):
            title = self.find_element_with_fallback(
                android_driver, resource_id="txvTitle", timeout=10
            )
            assert title is not None, "History 타이틀이 없음"
            assert title.text == "History", f"타이틀 불일치: {title.text}"

        with allure.step("MY USAGE 버튼 확인"):
            usages_btn = self.find_element_with_fallback(
                android_driver, resource_id="usages"
            )
            assert usages_btn is not None, "MY USAGE 버튼이 없음"

        with allure.step("History RecyclerView 확인"):
            history_rv = self.find_element_with_fallback(
                android_driver, resource_id="rvMainHistory"
            )
            assert history_rv is not None, "History 목록이 없음"

    # ========== Edit Info (027) ==========
    @allure.feature("Profile")
    @allure.story("정보 수정")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Edit Info 화면 요소 검증")
    @allure.description("Edit Info 화면의 UI 요소 확인")
    def test_03_edit_info_screen_elements(self, android_driver):
        """Edit Info 화면 요소 검증"""

        # (3) 로그인은 모듈(함수)로 수행
        login(android_driver)

        with allure.step("Profile 탭으로 이동"):
            try:
                profile_tab = android_driver.find_element(
                    AppiumBy.XPATH, "//android.widget.TextView[@text='Profile']"
                )
                profile_tab.click()
                time.sleep(2)
            except NoSuchElementException:
                pytest.skip("Profile 탭을 찾을 수 없음")

        with allure.step("Edit Info 메뉴 클릭"):
            try:
                edit_info = android_driver.find_element(
                    AppiumBy.XPATH, "//android.widget.TextView[@text='Edit Info']"
                )
                edit_info.click()
                time.sleep(2)
            except NoSuchElementException:
                pytest.skip("Edit Info 메뉴를 찾을 수 없음")

        with allure.step("Edit Info 타이틀 확인"):
            title = self.find_element_with_fallback(
                android_driver, resource_id="toolbar_title", timeout=10
            )
            assert title is not None, "Edit Info 타이틀이 없음"
            assert title.text == "Edit Info", f"타이틀 불일치: {title.text}"

        with allure.step("뒤로가기 버튼 확인"):
            back_btn = self.find_element_with_fallback(
                android_driver, resource_id="iv_back"
            )
            assert back_btn is not None, "뒤로가기 버튼이 없음"

        with allure.step("프로필 이미지 영역 확인"):
            profile_view = self.find_element_with_fallback(
                android_driver, resource_id="editProfileView"
            )
            assert profile_view is not None, "프로필 이미지 영역이 없음"

        with allure.step("프로필 편집 버튼 확인"):
            edit_image = self.find_element_with_fallback(
                android_driver, resource_id="editimage"
            )
            assert edit_image is not None, "프로필 편집 버튼이 없음"

        with allure.step("사용자 이름 확인"):
            fullname = self.find_element_with_fallback(
                android_driver, resource_id="fullname"
            )
            assert fullname is not None, "사용자 이름이 없음"
            assert len(fullname.text) > 0, "사용자 이름이 비어있음"

        with allure.step("Phone Number 섹션 확인"):
            phone_layout = self.find_element_with_fallback(
                android_driver, resource_id="phoneLayout"
            )
            assert phone_layout is not None, "Phone Number 섹션이 없음"

        with allure.step("Email 섹션 확인"):
            email_layout = self.find_element_with_fallback(
                android_driver, resource_id="emailLayout"
            )
            assert email_layout is not None, "Email 섹션이 없음"

        with allure.step("Address 섹션 확인"):
            address_layout = self.find_element_with_fallback(
                android_driver, resource_id="addressLayout"
            )
            assert address_layout is not None, "Address 섹션이 없음"

        with allure.step("Occupation 섹션 확인"):
            occupation_layout = self.find_element_with_fallback(
                android_driver, resource_id="occupationLayout"
            )
            assert occupation_layout is not None, "Occupation 섹션이 없음"

        with allure.step("Passport 섹션 확인"):
            passport_layout = self.find_element_with_fallback(
                android_driver, resource_id="passportLayout"
            )
            assert passport_layout is not None, "Passport 섹션이 없음"

        with allure.step("ARC 섹션 확인"):
            arc_layout = self.find_element_with_fallback(
                android_driver, resource_id="arcLayout"
            )
            assert arc_layout is not None, "ARC 섹션이 없음"

        with allure.step("Change Login Password 섹션 확인"):
            login_pw_layout = self.find_element_with_fallback(
                android_driver, resource_id="loginPasswordLayout"
            )
            assert login_pw_layout is not None, "Change Login Password 섹션이 없음"

        with allure.step("Change Simple Password 섹션 확인"):
            simple_pw_layout = self.find_element_with_fallback(
                android_driver, resource_id="simplePasswordLayout"
            )
            assert simple_pw_layout is not None, "Change Simple Password 섹션이 없음"

    # ========== GMEPay Wallet Guide (030) ==========
    @allure.feature("GMEPay")
    @allure.story("월렛 가이드")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GMEPay Wallet Guide 화면 요소 검증")
    @allure.description("GMEPay Wallet Guide 화면의 UI 요소 확인")
    def test_04_gmepay_wallet_guide_elements(self, android_driver):
        """GMEPay Wallet Guide 화면 요소 검증"""

        # (4) 로그인은 모듈(함수)로 수행
        login(android_driver)

        with allure.step("홈으로 이동"):
            try:
                home_tab = android_driver.find_element(
                    AppiumBy.XPATH, "//android.widget.TextView[@text='Home']"
                )
                home_tab.click()
                time.sleep(2)
            except NoSuchElementException:
                pass

        with allure.step("Easy Wallet Account 클릭하여 가이드 진입"):
            wallet_section = self.find_element_with_fallback(
                android_driver, resource_id="ll_easywallet_account", timeout=10
            )
            if wallet_section:
                wallet_section.click()
                time.sleep(2)
            else:
                pytest.skip("Easy Wallet Account 섹션을 찾을 수 없음")

        with allure.step("GMEPay wallet guide 타이틀 확인"):
            title = self.find_element_with_fallback(
                android_driver, resource_id="screenTitle", timeout=10
            )
            if title is None:
                pytest.skip("GMEPay wallet guide 화면이 아님")
            assert "GMEPay" in title.text or "wallet" in title.text.lower(), f"타이틀 불일치: {title.text}"

        with allure.step("뒤로가기 버튼 확인"):
            back_btn = self.find_element_with_fallback(
                android_driver, resource_id="btnBack"
            )
            assert back_btn is not None, "뒤로가기 버튼이 없음"

        with allure.step("How to deposit 섹션 확인"):
            how_to_deposit = self.find_element_with_fallback(
                android_driver, resource_id="llHowToDeposit"
            )
            assert how_to_deposit is not None, "How to deposit 섹션이 없음"

        with allure.step("Wallet Deposit Guide 섹션 확인"):
            deposit_guide = self.find_element_with_fallback(
                android_driver, resource_id="llWalletDepositGuide"
            )
            assert deposit_guide is not None, "Wallet Deposit Guide 섹션이 없음"

        with allure.step("One-time deposit limit 안내 확인"):
            limit_note = self.find_element_with_fallback(
                android_driver, resource_id="txvOneTimeLimitNote"
            )
            assert limit_note is not None, "One-time deposit limit 안내가 없음"
            assert "500,000" in limit_note.text, f"한도 금액 불일치: {limit_note.text}"

        with allure.step("Minimum transaction amount 안내 확인"):
            min_note = self.find_element_with_fallback(
                android_driver, resource_id="txvMinLimitNote"
            )
            assert min_note is not None, "Minimum transaction 안내가 없음"
            assert "1,000" in min_note.text, f"최소 금액 불일치: {min_note.text}"

        with allure.step("Confirm and Apply 버튼 확인"):
            submit_btn = self.find_element_with_fallback(
                android_driver, resource_id="btn_submit1"
            )
            assert submit_btn is not None, "Confirm and Apply 버튼이 없음"
            assert submit_btn.text == "Confirm and Apply", f"버튼 텍스트 불일치: {submit_btn.text}"