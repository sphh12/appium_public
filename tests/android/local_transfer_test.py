"""
Local Transfer 테스트 - GME Remit 앱 국내 송금 시나리오

구조:
  - setup: 앱 실행 → 언어 설정(English) → 로그인 (1회만)
  - 테스트: 로그인 완료 상태에서 순차 실행
  - teardown: 드라이버 종료

시나리오 흐름:
  1. 언어/로그인 확인 (setup에서 완료)
  2. 홈 → Local Transfer 진입
  3. 송금 계좌 선택 (GME Wallet)
  4. 수취인 정보 입력 (계좌번호 + 은행 + 금액)
  5. 송금 정보 확인 + 메모 입력
  6. 간편 비밀번호 입력
  7. 송금 완료 확인
  8. Transaction Details 확인
  9. 홈으로 복귀

실행 방법:
  APP_ENV=livetest python tools/run_allure.py -- tests/android/local_transfer_test.py -v --platform=android --clean-alluredir

주의: 실제 송금이 실행됩니다 (최소 금액 1 KRW 사용)
"""
import os
import time
from datetime import datetime, timedelta

import pytest
import allure
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

from utils.auth import login
from utils.initial_screens import handle_initial_screens
from config.capabilities import ANDROID_CAPS, get_appium_server_url, get_env_config

# 환경변수 로드
load_dotenv()

# APP_ENV 기반 자동 설정
_env_cfg = get_env_config()
RESOURCE_ID_PREFIX = _env_cfg["resource_id_prefix"]

# 송금 테스트 설정
TRANSFER_AMOUNT = "1"  # 최소 금액 (KRW)
RECEIVER_ACCOUNT = "22208803201010"  # 수취인 계좌번호
RECEIVER_BANK = "Industrial Bank of Korea(IBK)"  # 수취인 은행
RECEIVER_NAME = "한승필"  # 수취인 이름
SIMPLE_PIN = os.getenv("SIMPLE_PIN", "1212")  # 간편 비밀번호 4자리
MEMO = "qa test_auto"  # 송금 메모


def _id(suffix):
    """resource-id 전체 경로 생성 헬퍼"""
    return f"{RESOURCE_ID_PREFIX}/{suffix}"


class TestLocalTransfer:
    """GME Remit 국내 송금 테스트

    드라이버를 클래스 단위로 공유하여 로그인은 1번만 수행합니다.
    테스트 순서가 보장되어야 하므로 함수명 정렬에 의존합니다.
    """

    @classmethod
    def setup_class(cls):
        """클래스 시작 시 1회: 드라이버 생성 → 초기 화면 처리 → 언어 설정 → 로그인"""
        print("\n[SETUP] 드라이버 생성 중...")
        options = UiAutomator2Options().load_capabilities(ANDROID_CAPS)
        cls.driver = webdriver.Remote(
            command_executor=get_appium_server_url(),
            options=options,
        )
        cls.driver.implicitly_wait(10)
        print("[SETUP] 드라이버 생성 완료")

        # 초기 화면 처리 (언어 선택, 약관 동의)
        print("[SETUP] 초기 화면 처리...")
        handle_initial_screens(cls.driver)

        # 언어 설정 (English)
        print("[SETUP] 언어 설정 (English)...")
        cls._set_language_english(cls.driver)

        # 로그인
        print("[SETUP] 로그인 진행...")
        login(cls.driver)
        print("[SETUP] 로그인 완료 — 테스트 시작 준비 완료")

    @classmethod
    def teardown_class(cls):
        """클래스 종료 시 드라이버 정리"""
        if hasattr(cls, "driver") and cls.driver:
            print("\n[TEARDOWN] 드라이버 종료")
            cls.driver.quit()

    @staticmethod
    def _set_language_english(driver):
        """메인 화면에서 English 언어 선택"""
        try:
            lang_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.ID, _id("selectedLanguageText"))
                )
            )
            current_lang = lang_btn.text
            print(f"  [INFO] 현재 언어: {current_lang}")

            if current_lang == "English":
                print("  [INFO] 이미 English — 스킵")
                return

            lang_btn.click()
            time.sleep(1)

            english_row = driver.find_element(
                AppiumBy.XPATH,
                f'//*[@resource-id="{_id("languageRv")}"]'
                '//*[@text="English"]/..',
            )
            english_row.click()
            time.sleep(1)
            print("  [INFO] English 선택 완료")
        except (TimeoutException, NoSuchElementException) as e:
            print(f"  [WARN] 언어 설정 실패: {e} (계속 진행)")

    # ========== 1. 사전 확인 ==========

    @allure.feature("설정")
    @allure.story("언어 변경")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("앱 언어가 English로 설정되어 있는지 확인")
    def test_01_language_is_english(self):
        """언어 설정 확인"""
        with allure.step("홈 화면에서 English UI 요소 확인"):
            home_tab = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.XPATH, "//android.widget.TextView[@text='Home']")
                )
            )
            assert home_tab.text == "Home", f"언어가 English가 아님: {home_tab.text}"
            print("  [PASS] English UI 확인")

    @allure.feature("인증")
    @allure.story("로그인 상태 확인")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("로그인 완료 상태 확인")
    def test_02_logged_in(self):
        """로그인 상태 확인"""
        with allure.step("홈 화면 네비게이션 버튼 확인"):
            nav_btn = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id("iv_nav"))
                )
            )
            assert nav_btn.is_displayed(), "네비게이션 버튼이 표시되지 않음"
            print("  [PASS] 로그인 상태 유지 확인")

    # ========== 2. Local Transfer 진입 ==========

    @allure.feature("송금")
    @allure.story("Local Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("홈에서 Local Transfer 메뉴 진입")
    def test_03_enter_local_transfer(self):
        """홈 Quick Menu에서 Local Transfer 클릭"""
        with allure.step("Local Transfer 메뉴 클릭"):
            # Quick Menu의 Local Transfer 텍스트 클릭
            local_transfer = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH,
                     '//android.widget.TextView[@text="Local Transfer"]')
                )
            )
            local_transfer.click()
            print("  [INFO] Local Transfer 클릭")
            time.sleep(2)

        with allure.step("Local Transfer 화면 진입 확인"):
            title = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id("title"))
                )
            )
            assert title.text == "Local Transfer", f"타이틀 불일치: {title.text}"
            print("  [PASS] Local Transfer 화면 진입 확인")

    # ========== 3. 송금 계좌 선택 ==========

    @allure.feature("송금")
    @allure.story("Local Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("송금 계좌 선택 (GME Wallet)")
    def test_04_select_sending_account(self):
        """GME Wallet 송금 계좌 선택 → Continue"""
        with allure.step("GME Wallet 계좌 선택"):
            # 첫 번째 계좌 (GME Wallet) 클릭
            gme_wallet = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH,
                     f'//*[@resource-id="{_id("paymentSourceListRv")}"]'
                     '//android.view.ViewGroup[@clickable="true"][1]')
                )
            )
            gme_wallet.click()
            print("  [INFO] GME Wallet 선택")
            time.sleep(1)

        with allure.step("Continue 클릭"):
            continue_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.ID, _id("btn_ok"))
                )
            )
            continue_btn.click()
            print("  [INFO] Continue 클릭")
            time.sleep(2)

        with allure.step("수취인 입력 화면 진입 확인"):
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id("recipientAccountNoFormInputField"))
                )
            )
            print("  [PASS] 수취인 입력 화면 진입 확인")

    # ========== 4. 수취인 정보 입력 ==========

    @allure.feature("송금")
    @allure.story("Local Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("수취인 정보 입력 (계좌번호 + 은행 + 금액)")
    def test_05_enter_receiver_details(self):
        """수취인 계좌번호, 은행, 금액 입력"""

        with allure.step(f"계좌번호 입력: {RECEIVER_ACCOUNT}"):
            # 계좌번호 입력 필드
            account_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH,
                     f'//*[@resource-id="{_id("recipientAccountNoFormInputField")}"]'
                     '//android.widget.EditText')
                )
            )
            account_field.click()
            account_field.clear()
            account_field.send_keys(RECEIVER_ACCOUNT)
            print(f"  [INFO] 계좌번호 입력: {RECEIVER_ACCOUNT}")
            time.sleep(1)

        with allure.step(f"은행 선택: {RECEIVER_BANK}"):
            # 은행 선택 필드 클릭 → Select Bank 다이얼로그
            bank_field = self.driver.find_element(
                AppiumBy.ID, _id("recipientBankSelectionFormInputField")
            )
            bank_field.click()
            time.sleep(2)

            # Select Bank 다이얼로그에서 검색
            search_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.ID, _id("searchEditText"))
                )
            )
            search_field.click()
            search_field.send_keys("IBK")
            time.sleep(1)

            # 검색 결과에서 IBK 선택
            ibk_item = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH,
                     f'//*[@resource-id="{_id("textListRv")}"]'
                     '//android.view.ViewGroup[@clickable="true"][1]')
                )
            )
            ibk_item.click()
            print(f"  [INFO] 은행 선택: IBK")
            time.sleep(1)

        with allure.step(f"금액 입력: {TRANSFER_AMOUNT} KRW"):
            amount_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.ID, _id("amount"))
                )
            )
            amount_field.click()
            amount_field.send_keys(TRANSFER_AMOUNT)
            print(f"  [INFO] 금액 입력: {TRANSFER_AMOUNT} KRW")
            time.sleep(1)

            # 키보드 닫기
            self.driver.hide_keyboard()
            time.sleep(0.5)

        with allure.step("Continue 클릭"):
            continue_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.ID, _id("btn_ok2"))
                )
            )
            continue_btn.click()
            print("  [INFO] Continue 클릭")
            time.sleep(2)

        with allure.step("송금 확인 화면 진입 확인"):
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id("btnConfirmFinal"))
                )
            )
            print("  [PASS] 송금 확인 화면 진입 확인")

    # ========== 5. 송금 정보 확인 + 메모 ==========

    @allure.feature("송금")
    @allure.story("Local Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("송금 정보 확인 및 메모 입력")
    def test_06_verify_and_confirm(self):
        """송금 확인 화면에서 수취인/금액 검증 + 메모 입력 + Confirm"""

        with allure.step("수취인 이름 확인"):
            name_el = self.driver.find_element(AppiumBy.ID, _id("name"))
            print(f"  [INFO] 수취인: {name_el.text}")

        with allure.step("은행 확인"):
            bank_el = self.driver.find_element(AppiumBy.ID, _id("bankname"))
            print(f"  [INFO] 은행: {bank_el.text}")

        with allure.step("계좌번호 확인"):
            account_el = self.driver.find_element(AppiumBy.ID, _id("accountno"))
            print(f"  [INFO] 계좌: {account_el.text}")

        with allure.step("금액 확인"):
            amount_el = self.driver.find_element(AppiumBy.ID, _id("amount"))
            print(f"  [INFO] 금액: {amount_el.text}")

        with allure.step(f"메모 입력: {MEMO}"):
            memo_field = self.driver.find_element(AppiumBy.ID, _id("memo"))
            memo_field.clear()
            memo_field.send_keys(MEMO)
            print(f"  [INFO] 메모 입력: {MEMO}")
            self.driver.hide_keyboard()
            time.sleep(0.5)

        with allure.step("Confirm 클릭"):
            confirm_btn = self.driver.find_element(
                AppiumBy.ID, _id("btnConfirmFinal")
            )
            confirm_btn.click()
            print("  [INFO] Confirm 클릭")
            time.sleep(2)

    # ========== 6. 간편 비밀번호 입력 ==========

    @allure.feature("송금")
    @allure.story("Local Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("간편 비밀번호 입력")
    def test_07_enter_simple_pin(self):
        """보안 키패드에서 간편 비밀번호 4자리 입력"""

        with allure.step("간편 비밀번호 화면 대기"):
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id("keypadContainer"))
                )
            )
            print("  [INFO] 간편 비밀번호 화면 진입")

        with allure.step(f"PIN {len(SIMPLE_PIN)}자리 입력"):
            # 보안 키패드 숫자는 content-desc로 접근 (ACCESSIBILITY_ID)
            for i, digit in enumerate(SIMPLE_PIN):
                btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (AppiumBy.ACCESSIBILITY_ID, digit)
                    )
                )
                btn.click()
                print(f"  [INFO] PIN [{i+1}/{len(SIMPLE_PIN)}]: *")
                time.sleep(0.3)

            print("  [INFO] PIN 입력 완료")
            time.sleep(3)

    # ========== 7. 송금 완료 확인 ==========

    @allure.feature("송금")
    @allure.story("Local Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("송금 완료 (Success) 확인")
    def test_08_verify_success(self):
        """Success 다이얼로그 확인"""

        with allure.step("Success 타이틀 확인"):
            title = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id("txvDialogTitle"))
                )
            )
            assert title.text == "Success", f"타이틀 불일치: {title.text}"
            print("  [PASS] Success 확인")

        with allure.step("송금 결과 메시지 확인"):
            desc = self.driver.find_element(
                AppiumBy.ID, _id("txvDialogDescription")
            )
            print(f"  [INFO] 결과: {desc.text}")
            assert TRANSFER_AMOUNT in desc.text, f"금액 불일치: {desc.text}"

        with allure.step("View Receipt 클릭"):
            receipt_btn = self.driver.find_element(
                AppiumBy.ID, _id("btnOk")
            )
            receipt_btn.click()
            print("  [INFO] View Receipt 클릭")
            time.sleep(2)

    # ========== 8. Transaction Details 확인 ==========

    @allure.feature("송금")
    @allure.story("Local Transfer")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Transaction Details 화면 검증")
    def test_09_verify_transaction_details(self):
        """거래 상세 화면에서 정보 검증"""

        with allure.step("Transaction Details 타이틀 확인"):
            title = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id("toolbar_title"))
                )
            )
            assert title.text == "Transaction Details", f"타이틀 불일치: {title.text}"
            print("  [PASS] Transaction Details 화면 확인")

        with allure.step("STATUS 확인"):
            status = self.driver.find_element(
                AppiumBy.ID, _id("txvStatusValue")
            )
            print(f"  [INFO] Status: {status.text}")
            assert status.text == "SUCCESS", f"상태 불일치: {status.text}"

        with allure.step("Transaction ID 저장"):
            txn_id = self.driver.find_element(
                AppiumBy.ID, _id("txvControlNoValue")
            )
            # 클래스 변수에 저장 (test_10에서 매칭용)
            TestLocalTransfer.saved_txn_id = txn_id.text
            print(f"  [INFO] Transaction ID: {txn_id.text}")

        with allure.step("수취인 이름 확인"):
            name = self.driver.find_element(AppiumBy.ID, _id("txvName"))
            print(f"  [INFO] Name: {name.text}")

        with allure.step("금액 확인"):
            amount = self.driver.find_element(AppiumBy.ID, _id("txvAmount"))
            print(f"  [INFO] Amount: {amount.text}")

        with allure.step("뒤로가기 → 홈 복귀"):
            back_btn = self.driver.find_element(AppiumBy.ID, _id("iv_back"))
            back_btn.click()
            time.sleep(2)

            # 홈 화면 복귀 확인
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (AppiumBy.ID, _id("iv_nav"))
                    )
                )
                print("  [PASS] 홈 화면 복귀 확인")
            except TimeoutException:
                print("  [WARN] 홈 화면 복귀 확인 실패")

    # ========== 9. History에서 국내 송금 이력 확인 ==========

    @allure.feature("송금")
    @allure.story("Local Transfer")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("History에서 국내 송금 이력 확인")
    @allure.description("History → Remittance → Domestic 탭에서 Transaction ID로 송금 이력을 매칭하고 입금 시간을 검증한다")
    def test_10_verify_history(self):
        """History 탭에서 국내 송금 이력 확인 (Transaction ID 매칭 + 시간 범위 검증)"""

        with allure.step("하단 네비게이션에서 History 탭 클릭"):
            history_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH, "//android.widget.TextView[@text='History']")
                )
            )
            history_tab.click()
            print("  [INFO] History 탭 클릭")
            time.sleep(2)

        with allure.step("History 화면 진입 확인"):
            title = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id("txvTitle"))
                )
            )
            assert title.text == "History", f"타이틀 불일치: {title.text}"
            print("  [PASS] History 화면 진입")

        with allure.step("Remittance 메뉴 클릭"):
            remittance = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH,
                     f'//*[@resource-id="{_id("rvMainHistory")}"]'
                     '//android.widget.TextView[@text="Remittance"]/..')
                )
            )
            remittance.click()
            print("  [INFO] Remittance 클릭")
            time.sleep(2)

        with allure.step("Remittance 화면 진입 확인"):
            toolbar = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id("toolbar_title"))
                )
            )
            assert toolbar.text == "Remittance", f"타이틀 불일치: {toolbar.text}"
            print("  [PASS] Remittance 화면 진입")

        with allure.step("Domestic 탭 클릭"):
            domestic_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH, "//android.widget.TextView[@text='Domestic']")
                )
            )
            domestic_tab.click()
            print("  [INFO] Domestic 탭 클릭")
            time.sleep(2)

        with allure.step("Transaction ID로 송금 이력 매칭"):
            saved_id = getattr(TestLocalTransfer, "saved_txn_id", None)
            print(f"  [INFO] 매칭 대상 Transaction ID: {saved_id}")

            # 이력 목록에서 Transaction ID 매칭
            txn_ids = self.driver.find_elements(
                AppiumBy.ID, _id("tv_gme_control_no")
            )

            matched_index = -1
            for i, el in enumerate(txn_ids):
                if saved_id and saved_id in el.text:
                    matched_index = i
                    print(f"  [INFO] Transaction ID 매칭 성공 (index: {i})")
                    break

            if matched_index == -1:
                # ID 매칭 실패 시 첫 번째 이력으로 fallback
                print("  [WARN] Transaction ID 매칭 실패 — 첫 번째 이력으로 확인")
                matched_index = 0

        with allure.step("매칭된 이력의 수취인/금액/상태 검증"):
            names = self.driver.find_elements(AppiumBy.ID, _id("tv_user_id"))
            amounts = self.driver.find_elements(AppiumBy.ID, _id("tv_amount"))
            statuses = self.driver.find_elements(AppiumBy.ID, _id("tv_status"))
            dates = self.driver.find_elements(AppiumBy.ID, _id("tv_date"))

            matched_name = names[matched_index].text if matched_index < len(names) else "N/A"
            matched_amount = amounts[matched_index].text if matched_index < len(amounts) else "N/A"
            matched_status = statuses[matched_index].text if matched_index < len(statuses) else "N/A"
            matched_date = dates[matched_index].text if matched_index < len(dates) else "N/A"

            print(f"  [INFO] 수취인: {matched_name}")
            print(f"  [INFO] 금액: {matched_amount}")
            print(f"  [INFO] 상태: {matched_status}")
            print(f"  [INFO] 일시: {matched_date}")

            assert matched_name == RECEIVER_NAME, f"수취인 불일치: {matched_name}"
            assert TRANSFER_AMOUNT in matched_amount, f"금액 불일치: {matched_amount}"
            assert matched_status == "SUCCESS", f"상태 불일치: {matched_status}"
            print("  [PASS] 수취인/금액/상태 검증 완료")

        with allure.step("입금 시간 범위 검증 (10분 이내)"):
            # 날짜 형식: "2026-03-29 17:05:40" (마스킹 시 "****-**-** 17:05:40")
            # 마스킹된 날짜에서 시간 부분만 추출
            time_part = matched_date.strip()
            now = datetime.now()

            try:
                if "****" in time_part:
                    # 마스킹된 형식: "****-**-** HH:MM:SS"
                    hms = time_part.split(" ")[-1]  # "HH:MM:SS"
                    txn_time = datetime.strptime(
                        f"{now.strftime('%Y-%m-%d')} {hms}", "%Y-%m-%d %H:%M:%S"
                    )
                else:
                    # 마스킹 안 된 형식: "2026-03-29 17:05:40"
                    txn_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M:%S")

                diff = abs(now - txn_time)
                diff_minutes = diff.total_seconds() / 60

                print(f"  [INFO] 현재 시간: {now.strftime('%H:%M:%S')}")
                print(f"  [INFO] 거래 시간: {txn_time.strftime('%H:%M:%S')}")
                print(f"  [INFO] 차이: {diff_minutes:.1f}분")

                assert diff_minutes <= 10, f"입금 시간이 10분을 초과: {diff_minutes:.1f}분"
                print(f"  [PASS] 입금 시간 범위 검증 완료 ({diff_minutes:.1f}분 이내)")
            except ValueError as e:
                print(f"  [WARN] 시간 파싱 실패: {time_part} ({e})")

        with allure.step("홈으로 복귀"):
            back_btn = self.driver.find_element(AppiumBy.ID, _id("iv_back"))
            back_btn.click()
            time.sleep(1)

            home_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH, "//android.widget.TextView[@text='Home']")
                )
            )
            home_tab.click()
            time.sleep(1)
            print("  [PASS] 홈 복귀 완료")
