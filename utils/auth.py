"""Authentication and session helpers.

This module centralizes repeatable flows like navigating to the login screen and
performing login so that new tests can start from a logged-in state.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager

from appium.webdriver.common.appiumby import AppiumBy  # type: ignore
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


try:
    import allure  # type: ignore
except Exception:  # pragma: no cover
    allure = None


DEFAULT_RESOURCE_ID_PREFIX = os.getenv(
    "GME_RESOURCE_ID_PREFIX",
    "com.gmeremit.online.gmeremittance_native.stag:id",
)

DEFAULT_USERNAME = os.getenv("GME_TEST_USERNAME", "gme_qualitytest44")
DEFAULT_PIN = os.getenv("GME_TEST_PIN", "123456")


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
        - This function is intentionally conservative and mirrors the current
          `gme1_test.py` behavior (it does not assert the post-login state).
        - If you need stronger verification, pass a custom wait in the calling
          test (e.g., wait for a known element on the home screen).
    """
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
