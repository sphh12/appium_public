"""pytest conftest - 테스트 픽스처 및 설정"""
import base64
from datetime import datetime
import json
import time
from pathlib import Path

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy

from config.capabilities import ANDROID_CAPS, IOS_CAPS, get_appium_server_url

from utils.initial_screens import handle_initial_screens

try:
    import allure  # type: ignore
except Exception:  # pragma: no cover
    allure = None


def _get_any_driver(item):
    return (
        item.funcargs.get("driver")
        or item.funcargs.get("android_driver")
        or item.funcargs.get("ios_driver")
    )


def _safe_allure_attach(name: str, data: bytes, attachment_type):
    if allure is None:
        return
    try:
        allure.attach(data, name=name, attachment_type=attachment_type)
    except Exception:
        return


def _dismiss_system_ui_dialog(driver, max_attempts=3, wait_after_dismiss=2):
    """
    'System UI isn't responding' 팝업이 있으면 Wait 버튼을 클릭하여 닫음

    Args:
        driver: Appium 드라이버
        max_attempts: 최대 시도 횟수
        wait_after_dismiss: 팝업 닫은 후 대기 시간(초)
    """
    for attempt in range(max_attempts):
        try:
            # 짧은 implicit wait 설정 (팝업 확인용)
            driver.implicitly_wait(2)

            # "Wait" 버튼 찾기 (android.widget.Button with text "Wait")
            wait_button = driver.find_element(
                by=AppiumBy.XPATH,
                value="//android.widget.Button[@text='Wait' or @text='기다리기' or @text='대기']"
            )
            wait_button.click()
            print(f"[INFO] System UI dialog dismissed (attempt {attempt + 1})")

            # 팝업 닫은 후 시스템 안정화 대기
            time.sleep(wait_after_dismiss)

        except Exception:
            # 팝업이 없으면 정상 - 루프 종료
            break
        finally:
            # implicit wait 원복
            driver.implicitly_wait(10)


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

    parser.addoption(
        "--record-video",
        action="store_true",
        default=False,
        help="테스트 실패 시 화면녹화(mp4)를 Allure에 첨부"
    )


def pytest_configure(config):
    results_dir = config.getoption("allure_report_dir") or "allure-results"
    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)

    platform_name = (config.getoption("platform") or "android").lower()
    app_path = config.getoption("app") or ""
    record_video = bool(config.getoption("record_video"))

    caps = ANDROID_CAPS if platform_name == "android" else IOS_CAPS
    effective_app = app_path or str(caps.get("app", ""))

    env_lines = [
        f"platform={platform_name}",
        f"deviceName={caps.get('deviceName', '')}",
        f"platformVersion={caps.get('platformVersion', '')}",
        f"automationName={caps.get('automationName', '')}",
        f"app={effective_app}",
        f"appiumServer={get_appium_server_url()}",
        f"recordVideo={record_video}",
    ]
    (results_path / "environment.properties").write_text(
        "\n".join(env_lines) + "\n",
        encoding="utf-8",
    )

    categories = [
        {
            "name": "Appium 서버 연결 실패",
            "matchedStatuses": ["broken", "failed"],
            "traceRegex": ".*(ConnectionRefusedError|WinError 10061|MaxRetryError|Failed to establish a new connection).*",
        },
        {
            "name": "UI 동기화/대기 타임아웃",
            "matchedStatuses": ["broken", "failed"],
            "traceRegex": ".*(TimeoutException|Timed out|WebDriverWait).*",
        },
        {
            "name": "요소 탐색 실패",
            "matchedStatuses": ["broken", "failed"],
            "traceRegex": ".*(NoSuchElementException|Unable to locate element).*",
        },
        {
            "name": "Stale element",
            "matchedStatuses": ["broken", "failed"],
            "traceRegex": ".*(StaleElementReferenceException|StaleObjectException).*",
        },
    ]
    (results_path / "categories.json").write_text(
        json.dumps(categories, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    driver = _get_any_driver(item)
    if not driver:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if report.failed:
        try:
            png = driver.get_screenshot_as_png()
            _safe_allure_attach(
                name=f"screenshot_{item.name}_{timestamp}",
                data=png,
                attachment_type=getattr(allure.attachment_type, "PNG", None),
            )
        except Exception:
            pass

    if item.config.getoption("--record-video") and getattr(item, "_video_recording_started", False):
        if not getattr(item, "_video_recording_stopped", False):
            try:
                video_b64 = driver.stop_recording_screen()
                video_bytes = base64.b64decode(video_b64)
                status = "failed" if report.failed else "passed" if report.passed else report.outcome
                _safe_allure_attach(
                    name=f"video_{status}_{item.name}_{timestamp}",
                    data=video_bytes,
                    attachment_type=getattr(allure.attachment_type, "MP4", None),
                )
                item._video_recording_stopped = True
            except Exception:
                pass


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    results_dir = config.getoption("allure_report_dir") or "allure-results"
    terminalreporter.write_sep("=", "Allure report")
    terminalreporter.write_line(f"Generate: allure generate {results_dir} -o allure-report --clean")
    terminalreporter.write_line(f"Serve   : allure serve {results_dir}")
    terminalreporter.write_line("Open    : allure open allure-report")


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

    # Android인 경우 System UI 팝업 처리
    if platform == "android":
        _dismiss_system_ui_dialog(driver)

        # noReset=False 등으로 최초 실행 화면이 뜰 수 있으므로 공통 처리
        if request.node.get_closest_marker("skip_initial_screens") is None:
            handle_initial_screens(driver)

    if request.config.getoption("--record-video"):
        try:
            driver.start_recording_screen()
            request.node._video_recording_started = True
        except Exception:
            request.node._video_recording_started = False

    yield driver

    if request.config.getoption("--record-video") and getattr(request.node, "_video_recording_started", False):
        if not getattr(request.node, "_video_recording_stopped", False):
            try:
                driver.stop_recording_screen()
            except Exception:
                pass

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

    # System UI 팝업 처리 (에뮬레이터 부팅 직후 발생 가능)
    _dismiss_system_ui_dialog(driver)

    # noReset=False 등으로 최초 실행 화면이 뜰 수 있으므로 공통 처리
    if request.node.get_closest_marker("skip_initial_screens") is None:
        handle_initial_screens(driver)

    if request.config.getoption("--record-video"):
        try:
            driver.start_recording_screen()
            request.node._video_recording_started = True
        except Exception:
            request.node._video_recording_started = False

    yield driver

    if request.config.getoption("--record-video") and getattr(request.node, "_video_recording_started", False):
        if not getattr(request.node, "_video_recording_stopped", False):
            try:
                driver.stop_recording_screen()
            except Exception:
                pass

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

    if request.config.getoption("--record-video"):
        try:
            driver.start_recording_screen()
            request.node._video_recording_started = True
        except Exception:
            request.node._video_recording_started = False

    yield driver

    if request.config.getoption("--record-video") and getattr(request.node, "_video_recording_started", False):
        if not getattr(request.node, "_video_recording_stopped", False):
            try:
                driver.stop_recording_screen()
            except Exception:
                pass

    driver.quit()
