"""Initial screen handling for Android app onboarding flows.

This module centralizes logic for handling first-run screens that can appear
when `noReset=False` (e.g., language selection, terms and conditions).

It is intentionally conservative: it only acts when it positively identifies
known screens.
"""

from __future__ import annotations

import time

from appium.webdriver.common.appiumby import AppiumBy  # type: ignore
from selenium.common.exceptions import NoSuchElementException


DEFAULT_RESOURCE_ID_PREFIX = "com.gmeremit.online.gmeremittance_native.stag:id"


def _id(resource_id_prefix: str, suffix: str) -> str:
    return f"{resource_id_prefix}/{suffix}"


def is_main_screen(driver, resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX) -> bool:
    """Main screen is defined as the one containing the Login button."""
    try:
        driver.find_element(by=AppiumBy.ID, value=_id(resource_id_prefix, "btn_lgn"))
        return True
    except NoSuchElementException:
        return False


def is_login_screen(driver, resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX) -> bool:
    """Login screen is defined as the one containing the username input."""
    try:
        driver.find_element(by=AppiumBy.ID, value=_id(resource_id_prefix, "usernameId"))
        return True
    except NoSuchElementException:
        return False


def handle_language_selection(driver, resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX) -> bool:
    """Handle language selection screen (003.xml).

    Screen signature:
    - RecyclerView with resource-id `...:id/languageRv`

    Action:
    - Tap the row containing text "English" (preferred)
    - Fallback: tap the first row
    """
    language_rv_id = _id(resource_id_prefix, "languageRv")
    try:
        driver.find_element(by=AppiumBy.ID, value=language_rv_id)
    except NoSuchElementException:
        return False

    # Click the clickable parent row of the "English" label.
    try:
        english_row = driver.find_element(
            by=AppiumBy.XPATH,
            value=(
                f'//*[@resource-id="{language_rv_id}"]'
                '//*[@text="English"]/..'
            ),
        )
        english_row.click()
        return True
    except NoSuchElementException:
        pass

    # Fallback: first clickable ViewGroup child.
    try:
        rows = driver.find_elements(
            by=AppiumBy.XPATH,
            value=f'//*[@resource-id="{language_rv_id}"]/android.view.ViewGroup',
        )
        if rows:
            rows[0].click()
            return True
    except Exception:
        return False

    return False


def handle_terms_and_conditions(driver, resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX) -> bool:
    """Handle terms and conditions screen (004.xml).

    Screen signature:
    - TextView `...:id/screenTitle` contains "Terms"

    Action:
    - Tap `...:id/agreeAllContainer` if present
    - Scroll to bottom of `...:id/scrollView`
    - Tap Next/Confirm-like button if present
    """
    screen_title_id = _id(resource_id_prefix, "screenTitle")
    try:
        screen_title = driver.find_element(by=AppiumBy.ID, value=screen_title_id)
    except NoSuchElementException:
        return False

    if "Terms" not in (screen_title.text or ""):
        return False

    did_action = False

    try:
        agree_all = driver.find_element(by=AppiumBy.ID, value=_id(resource_id_prefix, "agreeAllContainer"))
        agree_all.click()
        did_action = True
        time.sleep(0.5)
    except NoSuchElementException:
        pass

    # Try UiScrollable on the known ScrollView.
    try:
        driver.find_element(
            by=AppiumBy.ANDROID_UIAUTOMATOR,
            value=(
                'new UiScrollable(new UiSelector().resourceId('
                f'"{_id(resource_id_prefix, "scrollView")}"'
                ')).scrollToEnd(5)'
            ),
        )
    except Exception:
        try:
            driver.swipe(540, 1900, 540, 700, 600)
        except Exception:
            pass

    next_button_ids = [
        "btnNext",
        "btn_next",
        "btnConfirm",
        "btn_confirm",
        "btnSubmit",
        "btnContinue",
        "btn_done",
    ]
    for btn_id in next_button_ids:
        try:
            driver.find_element(by=AppiumBy.ID, value=_id(resource_id_prefix, btn_id)).click()
            return True
        except NoSuchElementException:
            continue

    try:
        driver.find_element(
            by=AppiumBy.ANDROID_UIAUTOMATOR,
            value=(
                'new UiSelector().clickable(true).textMatches('
                '"(?i)(next|confirm|continue|done|ok|agree)"'
                ')'
            ),
        ).click()
        return True
    except NoSuchElementException:
        pass

    return did_action


def handle_initial_screens(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    max_attempts: int = 6,
    wait_between_attempts: float = 1.5,
) -> bool:
    """Try to clear known first-run screens until main/login is visible."""
    for _ in range(max_attempts):
        if is_main_screen(driver, resource_id_prefix) or is_login_screen(driver, resource_id_prefix):
            return True

        did_something = False

        if handle_language_selection(driver, resource_id_prefix):
            did_something = True

        if handle_terms_and_conditions(driver, resource_id_prefix):
            did_something = True

        if not did_something:
            time.sleep(wait_between_attempts)
        else:
            time.sleep(1.0)

    return is_main_screen(driver, resource_id_prefix) or is_login_screen(driver, resource_id_prefix)
