"""
pytest conftest - 테스트 픽스처 및 설정
"""
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

from config.capabilities import ANDROID_CAPS, IOS_CAPS, get_appium_server_url


def pytest_addoption(parser):
    """커맨드라인 옵션 추가"""
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        help="테스트 플랫폼: android 또는 ios"
    )
    parser.addoption(
        "--app",
        action="store",
        default="",
        help="앱 파일 경로 (.apk 또는 .ipa/.app)"
    )


@pytest.fixture(scope="session")
def platform(request):
    """현재 테스트 플랫폼 반환"""
    return request.config.getoption("--platform").lower()


@pytest.fixture(scope="function")
def driver(request, platform):
    """Appium 드라이버 생성 픽스처"""
    app_path = request.config.getoption("--app")

    if platform == "android":
        caps = ANDROID_CAPS.copy()
        if app_path:
            caps["app"] = app_path
        options = UiAutomator2Options().load_capabilities(caps)
    elif platform == "ios":
        caps = IOS_CAPS.copy()
        if app_path:
            caps["app"] = app_path
        options = XCUITestOptions().load_capabilities(caps)
    else:
        raise ValueError(f"지원하지 않는 플랫폼: {platform}")

    driver = webdriver.Remote(
        command_executor=get_appium_server_url(),
        options=options
    )
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(scope="function")
def android_driver(request):
    """Android 전용 드라이버"""
    app_path = request.config.getoption("--app")
    caps = ANDROID_CAPS.copy()
    if app_path:
        caps["app"] = app_path

    options = UiAutomator2Options().load_capabilities(caps)
    driver = webdriver.Remote(
        command_executor=get_appium_server_url(),
        options=options
    )
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(scope="function")
def ios_driver(request):
    """iOS 전용 드라이버"""
    app_path = request.config.getoption("--app")
    caps = IOS_CAPS.copy()
    if app_path:
        caps["app"] = app_path

    options = XCUITestOptions().load_capabilities(caps)
    driver = webdriver.Remote(
        command_executor=get_appium_server_url(),
        options=options
    )
    driver.implicitly_wait(10)

    yield driver

    driver.quit()
