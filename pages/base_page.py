"""
Page Object Model - Base Page
모든 페이지 클래스의 기본 클래스
"""
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BasePage:
    """기본 페이지 클래스"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find_element(self, locator: tuple, timeout: int = 10):
        """요소 찾기 (대기 포함)"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator: tuple, timeout: int = 10):
        """여러 요소 찾기"""
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)

    def click(self, locator: tuple):
        """요소 클릭"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def input_text(self, locator: tuple, text: str):
        """텍스트 입력"""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        """요소의 텍스트 가져오기"""
        return self.find_element(locator).text

    def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
        """요소가 화면에 보이는지 확인"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def wait_for_element(self, locator: tuple, timeout: int = 10):
        """요소가 나타날 때까지 대기"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 800):
        """스와이프 동작"""
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)

    def swipe_up(self):
        """위로 스와이프"""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.8)
        end_y = int(size['height'] * 0.2)
        self.swipe(start_x, start_y, start_x, end_y)

    def swipe_down(self):
        """아래로 스와이프"""
        size = self.driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.2)
        end_y = int(size['height'] * 0.8)
        self.swipe(start_x, start_y, start_x, end_y)

    def take_screenshot(self, filename: str):
        """스크린샷 저장"""
        self.driver.save_screenshot(f"reports/{filename}.png")

    def go_back(self):
        """뒤로 가기"""
        self.driver.back()

    def hide_keyboard(self):
        """키보드 숨기기"""
        try:
            self.driver.hide_keyboard()
        except:
            pass  # 키보드가 없으면 무시
