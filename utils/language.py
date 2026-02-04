"""Language selection helpers.

앱 첫 화면에서 언어를 설정하는 기능을 제공합니다.
로그인 전에 호출하여 앱 언어를 English로 설정합니다.

화면 흐름:
  1. 메인 화면: "언어 선택" 버튼 (selectedLanguageText) 클릭
  2. 언어 목록 화면: languageRv에서 원하는 언어 선택
  3. 메인 화면으로 복귀 (선택한 언어 적용됨)

주요 함수:
  - set_language_to_english(): 앱 언어를 English로 변경
  - ensure_english_language(): 로그인 전 English 설정 (실패 시 예외)

사용 예시:
    from utils.language import set_language_to_english
    set_language_to_english(driver)
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

try:
    import allure
except ImportError:
    allure = None

# 환경변수에서 resource-id 접두사 로드
DEFAULT_RESOURCE_ID_PREFIX = os.getenv(
    "GME_RESOURCE_ID_PREFIX",
    "com.gmeremit.online.gmeremittance_native.stag:id",
)


def _id(resource_id_prefix: str, suffix: str) -> str:
    """resource-id 전체 경로 생성."""
    return f"{resource_id_prefix}/{suffix}"


@contextmanager
def _step(name: str):
    """Allure step context manager."""
    if allure is None:
        yield
    else:
        with allure.step(name):
            yield


def is_language_list_screen(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 3,
) -> bool:
    """현재 화면이 언어 목록 화면인지 확인합니다.

    Args:
        driver: Appium WebDriver 인스턴스
        resource_id_prefix: 앱의 resource-id 접두사
        timeout: 대기 시간 (초)

    Returns:
        bool: 언어 목록 화면 (languageRv가 있는 화면)이면 True
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, _id(resource_id_prefix, "languageRv"))
            )
        )
        return True
    except (NoSuchElementException, TimeoutException):
        return False


# 이전 버전 호환성을 위한 alias
is_language_selection_screen = is_language_list_screen


def is_main_screen_with_language_button(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 3,
) -> bool:
    """현재 화면이 언어 선택 버튼이 있는 메인 화면인지 확인합니다.

    Args:
        driver: Appium WebDriver 인스턴스
        resource_id_prefix: 앱의 resource-id 접두사
        timeout: 대기 시간 (초)

    Returns:
        bool: 언어 선택 버튼 (selectedLanguageText)이 있는 메인 화면이면 True
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, _id(resource_id_prefix, "selectedLanguageText"))
            )
        )
        return True
    except (NoSuchElementException, TimeoutException):
        return False


def open_language_list(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 10,
) -> bool:
    """메인 화면에서 언어 선택 버튼을 클릭하여 언어 목록을 엽니다.

    Args:
        driver: Appium WebDriver 인스턴스
        resource_id_prefix: 앱의 resource-id 접두사
        timeout: 대기 시간 (초)

    Returns:
        bool: 언어 목록 열기 성공 여부
    """
    try:
        with _step("언어 선택 버튼 클릭"):
            # 언어 선택 버튼 클릭
            lang_button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(
                    (AppiumBy.ID, _id(resource_id_prefix, "selectedLanguageText"))
                )
            )
            lang_button.click()
            time.sleep(1)

        # 언어 목록이 나타날 때까지 대기
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, _id(resource_id_prefix, "languageRv"))
            )
        )
        return True

    except (NoSuchElementException, TimeoutException):
        return False


def set_language_to_english(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 10,
) -> bool:
    """앱 언어를 English로 설정합니다.

    메인 화면에서 언어 선택 버튼을 클릭하고, 언어 목록에서 English를 선택합니다.

    Args:
        driver: Appium WebDriver 인스턴스
        resource_id_prefix: 앱의 resource-id 접두사
        timeout: 대기 시간 (초)

    Returns:
        bool: 언어 설정 성공 여부
    """
    return set_language(
        driver,
        language_text="English",
        resource_id_prefix=resource_id_prefix,
        timeout=timeout,
    )


def set_language(
    driver,
    language_text: str,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 10,
) -> bool:
    """앱 언어를 지정된 언어로 설정합니다.

    지원 언어:
        - English
        - 한국어
        - ភាសាខ្មែរ (Khmer)
        - ไทย (Thai)
        - සිංහල (Sinhala)
        - Монгол хэл (Mongolian)
        - မြန်မာUnicode (Myanmar)
        - नेपाली (Nepali)
        - Bahasa Indonesia
        - বাংলাদেশ (Bengali)
        - Русский язык (Russian)

    Args:
        driver: Appium WebDriver 인스턴스
        language_text: 선택할 언어 텍스트 (예: "English", "한국어")
        resource_id_prefix: 앱의 resource-id 접두사
        timeout: 대기 시간 (초)

    Returns:
        bool: 언어 설정 성공 여부
    """
    # 1. 이미 언어 목록 화면인지 확인
    if not is_language_list_screen(driver, resource_id_prefix, timeout=2):
        # 메인 화면에서 언어 선택 버튼이 있는지 확인
        if not is_main_screen_with_language_button(driver, resource_id_prefix, timeout):
            return False

        # 언어 목록 열기
        if not open_language_list(driver, resource_id_prefix, timeout):
            return False

    # 2. 언어 목록에서 선택
    with _step(f"언어 목록에서 {language_text} 선택"):
        return _select_language_from_list(
            driver,
            language_text=language_text,
            resource_id_prefix=resource_id_prefix,
            timeout=timeout,
        )


def _select_language_from_list(
    driver,
    language_text: str,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 10,
) -> bool:
    """언어 목록에서 지정된 언어를 선택합니다.

    Args:
        driver: Appium WebDriver 인스턴스
        language_text: 선택할 언어 텍스트
        resource_id_prefix: 앱의 resource-id 접두사
        timeout: 대기 시간 (초)

    Returns:
        bool: 언어 선택 성공 여부
    """
    # 방법 1: UiSelector 사용 (Android 전용, 가장 안정적)
    try:
        ui_selector = f'new UiSelector().resourceId("{_id(resource_id_prefix, "countryLanguageText")}").text("{language_text}")'
        language_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)
            )
        )
        language_element.click()
        time.sleep(1.5)
        return True
    except (NoSuchElementException, TimeoutException):
        pass

    # 방법 2: 텍스트로 직접 찾기 (폴백)
    try:
        text_xpath = f"//android.widget.TextView[@text='{language_text}']"
        language_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((AppiumBy.XPATH, text_xpath))
        )
        language_element.click()
        time.sleep(1.5)
        return True
    except (NoSuchElementException, TimeoutException):
        pass

    # 방법 3: 스크롤하며 찾기
    return _select_language_with_scroll(
        driver,
        language_text=language_text,
        resource_id_prefix=resource_id_prefix,
        timeout=timeout,
    )


def _select_language_with_scroll(
    driver,
    language_text: str,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 10,
    max_scrolls: int = 3,
) -> bool:
    """스크롤하면서 언어를 찾아 선택합니다.

    Args:
        driver: Appium WebDriver 인스턴스
        language_text: 선택할 언어 텍스트
        resource_id_prefix: 앱의 resource-id 접두사
        timeout: 대기 시간 (초)
        max_scrolls: 최대 스크롤 횟수

    Returns:
        bool: 언어 선택 성공 여부
    """
    ui_selector = f'new UiSelector().text("{language_text}")'

    for _ in range(max_scrolls):
        try:
            language_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)
                )
            )
            language_element.click()
            time.sleep(1.5)
            return True

        except (NoSuchElementException, TimeoutException):
            _scroll_down(driver)
            time.sleep(0.5)

    return False


def _scroll_down(driver, scroll_ratio: float = 0.5) -> None:
    """화면을 아래로 스크롤합니다."""
    size = driver.get_window_size()
    start_x = size["width"] // 2
    start_y = int(size["height"] * 0.7)
    end_y = int(size["height"] * (0.7 - scroll_ratio * 0.4))

    driver.swipe(start_x, start_y, start_x, end_y, duration=300)


def ensure_english_language(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 10,
) -> None:
    """앱 시작 시 메인 화면에서 English를 선택합니다.

    이 함수는 로그인 flow 전에 호출되어야 합니다.
    메인 화면에 언어 선택 버튼이 없으면 아무 작업도 하지 않습니다.

    Args:
        driver: Appium WebDriver 인스턴스
        resource_id_prefix: 앱의 resource-id 접두사
        timeout: 대기 시간 (초)

    Raises:
        RuntimeError: 언어 선택에 실패한 경우
    """
    # 메인 화면에 언어 선택 버튼이 있는지 확인
    if is_main_screen_with_language_button(driver, resource_id_prefix, timeout):
        success = set_language_to_english(driver, resource_id_prefix, timeout)
        if not success:
            raise RuntimeError(
                "언어 설정에 실패했습니다. "
                "UI 구조가 변경되었거나 English 옵션을 찾을 수 없습니다."
            )
