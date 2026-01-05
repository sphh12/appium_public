"""
유틸리티 헬퍼 함수
"""
import time
import os
from datetime import datetime


def wait(seconds: float):
    """지정된 시간 동안 대기"""
    time.sleep(seconds)


def get_timestamp() -> str:
    """현재 타임스탬프 반환"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_report_dir():
    """리포트 디렉토리 생성"""
    report_dir = "reports"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    return report_dir


def save_screenshot_with_timestamp(driver, prefix: str = "screenshot"):
    """타임스탬프가 포함된 스크린샷 저장"""
    create_report_dir()
    filename = f"reports/{prefix}_{get_timestamp()}.png"
    driver.save_screenshot(filename)
    return filename


def scroll_to_element(driver, locator, max_scrolls: int = 5):
    """요소가 나타날 때까지 스크롤"""
    from appium.webdriver.common.appiumby import AppiumBy
    from selenium.common.exceptions import NoSuchElementException

    for _ in range(max_scrolls):
        try:
            element = driver.find_element(*locator)
            if element.is_displayed():
                return element
        except NoSuchElementException:
            pass

        # 아래로 스와이프
        size = driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.8)
        end_y = int(size['height'] * 0.2)
        driver.swipe(start_x, start_y, start_x, end_y, 800)

    raise NoSuchElementException(f"요소를 찾을 수 없습니다: {locator}")


def get_device_info(driver) -> dict:
    """디바이스 정보 반환"""
    return {
        "platform": driver.capabilities.get("platformName"),
        "platform_version": driver.capabilities.get("platformVersion"),
        "device_name": driver.capabilities.get("deviceName"),
        "automation_name": driver.capabilities.get("automationName"),
    }
