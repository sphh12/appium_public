"""Authentication and session helpers.

This module centralizes repeatable flows like navigating to the login screen and
performing login so that new tests can start from a logged-in state.

환경변수 설정:
  - TEST_USERNAME: 테스트 사용자 ID
  - TEST_PIN: 테스트 사용자 PIN
  - RESOURCE_ID_PREFIX: 앱의 resource-id 접두사 (예: com.example.app:id)
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager

from appium.webdriver.common.appiumby import AppiumBy  # type: ignore
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


try:
    import allure  # type: ignore
except Exception:  # pragma: no cover
    allure = None


# 환경변수에서 설정 로드 (기본값은 예시)
DEFAULT_RESOURCE_ID_PREFIX = os.getenv(
    "RESOURCE_ID_PREFIX",
    "com.example.app:id",  # 실제 앱의 패키지명으로 변경하세요
)

DEFAULT_USERNAME = os.getenv("TEST_USERNAME", "")  # 환경변수로 설정하세요
DEFAULT_PIN = os.getenv("TEST_PIN", "")  # 환경변수로 설정하세요


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
) -> None:
    """Perform login flow.

    Notes:
        - 환경변수 TEST_USERNAME, TEST_PIN을 설정하거나 파라미터로 전달하세요.
        - If you need stronger verification, pass a custom wait in the calling
          test (e.g., wait for a known element on the home screen).
    """
    if not username or not pin:
        raise ValueError(
            "username과 pin이 필요합니다. "
            "환경변수 TEST_USERNAME, TEST_PIN을 설정하거나 파라미터로 전달하세요."
        )

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

    # 로그인 후 팝업 처리 (있을 경우에만)
    _handle_post_login_popup_if_present(driver, resource_id_prefix=resource_id_prefix)


def _handle_post_login_popup_if_present(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 3,
) -> bool:
    """로그인 후 팝업이 있으면 처리합니다.

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

        with _step("로그인 후 팝업 처리"):
            # 체크박스 클릭
            checkbox.click()
            time.sleep(0.5)

            # OK 버튼 클릭 (체크박스 클릭 후 활성화됨)
            ok_button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH, "//android.widget.Button[@text='OK']")
                )
            )
            ok_button.click()
            time.sleep(1)

        return True

    except (NoSuchElementException, TimeoutException):
        # 팝업이 없으면 그냥 넘어감
        return False
