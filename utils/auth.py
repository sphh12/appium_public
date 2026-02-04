"""Authentication and session helpers.

This module centralizes repeatable flows like navigating to the login screen and
performing login so that new tests can start from a logged-in state.

환경변수 설정:
  - STG_ID / STG_PW: Staging 테스트 계정 (기본)
  - LIVE_ID / LIVE_PW: Live 테스트 계정
  - GME_RESOURCE_ID_PREFIX: 앱의 resource-id 접두사

.env 파일 또는 환경변수로 설정하세요.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager

from appium.webdriver.common.appiumby import AppiumBy  # type: ignore
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv

from utils.language import ensure_english_language

# 환경변수 로드 (.env 파일)
load_dotenv()

try:
    import allure  # type: ignore
except Exception:  # pragma: no cover
    allure = None


# 환경변수에서 설정 로드
DEFAULT_RESOURCE_ID_PREFIX = os.getenv(
    "GME_RESOURCE_ID_PREFIX",
    "com.gmeremit.online.gmeremittance_native.stag:id",
)

# 민감정보는 반드시 환경변수로 설정 (기본값 없음)
# STG (Staging) 계정이 기본값, LIVE 계정은 별도 함수로 사용
DEFAULT_USERNAME = os.getenv("STG_ID", "")
DEFAULT_PIN = os.getenv("STG_PW", "")

# Live 계정 정보
LIVE_USERNAME = os.getenv("LIVE_ID", "")
LIVE_PIN = os.getenv("LIVE_PW", "")


def _id(resource_id_prefix: str, suffix: str) -> str:
    return f"{resource_id_prefix}/{suffix}"


@contextmanager
def _step(name: str):
    if allure is None:
        yield
        return

    with allure.step(name):
        yield


def is_login_screen(driver, resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX) -> bool:
    """Login screen is defined as the one containing the username input."""
    try:
        driver.find_element(by=AppiumBy.ID, value=_id(resource_id_prefix, "usernameId"))
        return True
    except NoSuchElementException:
        return False


def navigate_to_login_screen(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 15,
) -> None:
    """Navigate from main screen to login screen if needed."""
    if is_login_screen(driver, resource_id_prefix):
        return

    with _step("로그인 화면 진입"):
        login_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((AppiumBy.ID, _id(resource_id_prefix, "btn_lgn")))
        )
        login_btn.click()

        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.ID, _id(resource_id_prefix, "usernameId")))
        )


def _tap_security_keyboard_complete(driver, timeout: float = 10) -> None:
    # 앱 언어/버전에 따라 버튼 텍스트가 바뀔 수 있어 후보를 둠.
    candidates = ["입력완료", "COMPLETE", "Complete", "완료"]
    last_error: Exception | None = None

    for label in candidates:
        try:
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, label))
            ).click()
            return
        except Exception as e:
            last_error = e

    if last_error is not None:
        raise last_error


def enter_pin_via_security_keyboard(
    driver,
    pin: str,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 10,
) -> None:
    """Enter PIN by tapping security keyboard digits and the Complete button."""
    with _step("비밀번호 입력"):
        pw_field = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, _id(resource_id_prefix, "securityKeyboardEditText"))
            )
        )
        pw_field.click()

        for digit in pin:
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, str(digit)))
            ).click()

        _tap_security_keyboard_complete(driver, timeout=timeout)


def login(
    driver,
    username: str = DEFAULT_USERNAME,
    pin: str = DEFAULT_PIN,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 15,
    post_login_sleep: float = 2.0,
    set_english: bool = True,
) -> None:
    """Perform login flow.

    Args:
        driver: Appium WebDriver 인스턴스
        username: 로그인 아이디 (기본값: 환경변수 STG_ID)
        pin: 로그인 비밀번호 (기본값: 환경변수 STG_PW)
        resource_id_prefix: 앱의 resource-id 접두사
        timeout: 대기 시간 (초)
        post_login_sleep: 로그인 후 대기 시간 (초)
        set_english: True이면 언어 선택 화면에서 English 자동 선택 (기본값: True)

    Notes:
        - 환경변수 STG_ID/STG_PW (Staging) 또는 LIVE_ID/LIVE_PW (Live)를 설정하세요.
        - If you need stronger verification, pass a custom wait in the calling
          test (e.g., wait for a known element on the home screen).
    """
    if not username or not pin:
        raise ValueError(
            "username과 pin이 필요합니다. "
            "환경변수 STG_ID/STG_PW 또는 LIVE_ID/LIVE_PW를 설정하거나 "
            ".env 파일에 추가하세요."
        )

    # 언어 선택 화면이 나타나면 English 선택
    if set_english:
        ensure_english_language(driver, resource_id_prefix=resource_id_prefix, timeout=timeout)

    navigate_to_login_screen(driver, resource_id_prefix=resource_id_prefix, timeout=timeout)

    with _step("아이디 입력"):
        username_field = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.ID, _id(resource_id_prefix, "usernameId")))
        )
        try:
            username_field.clear()
        except Exception:
            pass
        username_field.send_keys(username)

    enter_pin_via_security_keyboard(
        driver,
        pin=pin,
        resource_id_prefix=resource_id_prefix,
        timeout=timeout,
    )

    with _step("로그인 완료 대기"):
        time.sleep(post_login_sleep)

    # 로그인 후 팝업 처리 (순서: 지문 인증 → 보이스피싱)
    # 앱 버전에 따라 순서가 다를 수 있으므로 반복 체크
    _handle_post_login_popups(driver, resource_id_prefix=resource_id_prefix)


def _handle_post_login_popups(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    max_attempts: int = 3,
) -> None:
    """로그인 후 발생할 수 있는 팝업들을 순차적으로 처리합니다.

    앱 버전에 따라 팝업 순서가 다를 수 있으므로 반복 체크합니다.
    - 지문 인증 설정 화면
    - 보이스피싱 경고 팝업
    """
    for _ in range(max_attempts):
        fingerprint_handled = _handle_fingerprint_setup_if_present(
            driver, resource_id_prefix=resource_id_prefix
        )
        phishing_handled = _handle_voice_phishing_popup_if_present(
            driver, resource_id_prefix=resource_id_prefix
        )

        # 두 팝업 모두 없으면 종료
        if not fingerprint_handled and not phishing_handled:
            break


def _handle_voice_phishing_popup_if_present(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 3,
) -> bool:
    """로그인 후 보이스피싱 경고 팝업이 있으면 처리합니다.

    Returns:
        bool: 팝업을 처리했으면 True, 팝업이 없었으면 False
    """
    try:
        # 체크박스가 있는지 짧은 timeout으로 확인
        checkbox = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, _id(resource_id_prefix, "check_customer"))
            )
        )

        with _step("보이스피싱 경고 팝업 처리"):
            # 체크박스 클릭
            checkbox.click()
            time.sleep(0.5)

            # 확인 버튼 클릭 (체크박스 클릭 후 활성화됨)
            # 버튼 텍스트: "확인", "OK" 등 다양할 수 있음
            confirm_button_texts = ["확인", "OK", "ok", "Ok"]
            button_clicked = False

            for text in confirm_button_texts:
                try:
                    confirm_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (AppiumBy.XPATH, f"//android.widget.Button[@text='{text}']")
                        )
                    )
                    confirm_button.click()
                    button_clicked = True
                    break
                except (NoSuchElementException, TimeoutException):
                    continue

            if not button_clicked:
                # 텍스트로 못 찾으면 활성화된 버튼 찾기
                try:
                    any_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (AppiumBy.XPATH, "//android.widget.Button[@enabled='true']")
                        )
                    )
                    any_button.click()
                except (NoSuchElementException, TimeoutException):
                    pass

            time.sleep(1)

        return True

    except (NoSuchElementException, TimeoutException):
        # 팝업이 없으면 그냥 넘어감
        return False


def _handle_fingerprint_setup_if_present(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 2,
) -> bool:
    """로그인 후 지문 인증 설정 화면이 있으면 [나중에] 버튼을 탭합니다.

    Returns:
        bool: 화면을 처리했으면 True, 화면이 없었으면 False
    """
    # 1. resource-id로 먼저 시도 (가장 안정적)
    # "나중에" 버튼: txt_pennytest_msg (TextView)
    try:
        later_element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (AppiumBy.ID, _id(resource_id_prefix, "txt_pennytest_msg"))
            )
        )

        with _step("지문 인증 설정 화면 - 나중에 선택"):
            later_element.click()
            time.sleep(1)

        return True

    except (NoSuchElementException, TimeoutException):
        pass

    # 2. 텍스트로 폴백 (다른 버전/언어 대응)
    later_button_texts = ["나중에", "Later", "LATER", "다음에", "취소", "Cancel"]
    xpath_conditions = " or ".join([f"@text='{t}'" for t in later_button_texts])
    xpath = f"//*[{xpath_conditions}]"

    try:
        later_element = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
        )

        with _step("지문 인증 설정 화면 - 나중에 선택"):
            later_element.click()
            time.sleep(1)

        return True

    except (NoSuchElementException, TimeoutException):
        # 화면이 없으면 그냥 넘어감
        return False
