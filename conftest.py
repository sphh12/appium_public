"""pytest conftest - 테스트 픽스처 및 설정"""
import base64
from datetime import datetime
import getpass
import json
import platform as _platform
import subprocess
import sys
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


def _safe_run_git(args: list[str], cwd: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            check=True,
            capture_output=True,
            text=True,
        )
        return (proc.stdout or "").strip()
    except Exception:
        return ""


def _write_executor_json(results_path: Path, build_name: str) -> None:
    executor = {
        "name": getpass.getuser() or "local",
        "type": "local",
        "buildName": build_name,
        "buildUrl": "",
        "reportName": "appium-mobile-test",
        "reportUrl": "",
    }
    (results_path / "executor.json").write_text(
        json.dumps(executor, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


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
        help="테스트 화면녹화(mp4) 수행(실패/스킵/broken 시 Allure 첨부)"
    )

    parser.addoption(
        "--allure-attach",
        action="store",
        default="hybrid",
        choices=["hybrid", "all", "fail-skip"],
        help=(
            "Allure 첨부 정책: hybrid(기본, FAIL/SKIP/BROKEN만 첨부), "
            "all(성공 포함 전체 첨부). fail-skip은 이전 값 호환용"
        ),
    )


def pytest_configure(config):
    try:
        results_dir = config.getoption("allure_report_dir")
    except Exception:
        results_dir = None
    results_dir = results_dir or "allure-results"
    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)

    platform_name = (config.getoption("platform") or "android").lower()
    app_path = config.getoption("app") or ""
    record_video = bool(config.getoption("record_video"))
    allure_attach = str(config.getoption("allure_attach") or "hybrid")
    if allure_attach == "fail-skip":
        allure_attach = "hybrid"

    caps = ANDROID_CAPS if platform_name == "android" else IOS_CAPS
    effective_app = app_path or str(caps.get("app", ""))

    repo_root = Path(getattr(config, "rootpath", Path.cwd()))
    git_branch = _safe_run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    git_commit = _safe_run_git(["rev-parse", "--short", "HEAD"], cwd=repo_root)
    git_message = _safe_run_git(["log", "-1", "--pretty=%s"], cwd=repo_root)
    build_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}|{platform_name}" + (
        f"|{git_branch}@{git_commit}" if (git_branch or git_commit) else ""
    )

    env_lines = [
        f"platform={platform_name}",
        f"deviceName={caps.get('deviceName', '')}",
        f"platformVersion={caps.get('platformVersion', '')}",
        f"automationName={caps.get('automationName', '')}",
        f"app={effective_app}",
        f"appiumServer={get_appium_server_url()}",
        f"recordVideo={record_video}",
        f"allureAttach={allure_attach}",
        f"os={_platform.platform()}",
        f"python={sys.version.split()[0]}",
        f"gitBranch={git_branch}",
        f"gitCommit={git_commit}",
        f"gitMessage={git_message}",
    ]
    (results_path / "environment.properties").write_text(
        "\n".join(env_lines) + "\n",
        encoding="utf-8",
    )

    _write_executor_json(results_path, build_name)

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

    # 실패/스킵은 setup 단계에서도 발생할 수 있어 캡처 범위를 넓힘
    if report.when not in ("setup", "call", "teardown"):
        return

    driver = _get_any_driver(item)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    attach_mode = str(item.config.getoption("allure_attach") or "hybrid")
    if attach_mode == "fail-skip":
        attach_mode = "hybrid"
    attach_all = attach_mode == "all"

    # 전체 단계(setup/call/teardown) 중 한 번이라도 실패/스킵이면 기록
    if report.failed:
        item._allure_any_failed = True
    if report.skipped:
        item._allure_any_skipped = True

    # 스크린샷: hybrid는 FAIL/SKIP/BROKEN(대부분 setup/teardown 실패=report.failed)에만,
    # all 모드에선 PASS도(call 단계에서) 첨부.
    want_screenshot = (report.failed or report.skipped) or (attach_all and report.when == "call")

    # 부가 진단(page source/caps/logcat): hybrid는 실패(=broken 포함)만, all 모드에선 PASS도(call 단계에서) 첨부.
    want_diagnostics = report.failed or (attach_all and report.when == "call")

    if want_screenshot and not getattr(item, "_allure_screen_attached", False):
        if driver:
            try:
                png = driver.get_screenshot_as_png()
                status = (
                    "failed"
                    if report.failed
                    else "skipped"
                    if report.skipped
                    else "passed"
                    if report.passed
                    else report.outcome
                )
                phase = report.when
                _safe_allure_attach(
                    name=f"screenshot_{status}_{phase}_{item.name}_{timestamp}.png",
                    data=png,
                    attachment_type=getattr(allure.attachment_type, "PNG", None),
                )
                item._allure_screen_attached = True
            except Exception:
                pass

    if want_diagnostics and driver:
        try:
            source = getattr(driver, "page_source", "")
            if source:
                _safe_allure_attach(
                    name=f"page_source_{item.name}_{timestamp}.xml",
                    data=source.encode("utf-8", errors="replace"),
                    attachment_type=getattr(allure.attachment_type, "XML", None)
                    or getattr(allure.attachment_type, "TEXT", None),
                )
        except Exception:
            pass

        try:
            caps = getattr(driver, "capabilities", None)
            if caps:
                _safe_allure_attach(
                    name=f"capabilities_{item.name}_{timestamp}.json",
                    data=json.dumps(caps, ensure_ascii=False, indent=2).encode("utf-8"),
                    attachment_type=getattr(allure.attachment_type, "JSON", None)
                    or getattr(allure.attachment_type, "TEXT", None),
                )
        except Exception:
            pass

        try:
            platform_name = (item.config.getoption("platform") or "android").lower()
            if platform_name == "android":
                logs = driver.get_log("logcat")
                if logs:
                    # 너무 커질 수 있어 최근 일부만 첨부
                    tail = logs[-300:] if len(logs) > 300 else logs
                    log_text = "\n".join(json.dumps(entry, ensure_ascii=False) for entry in tail)
                    _safe_allure_attach(
                        name=f"logcat_{item.name}_{timestamp}.txt",
                        data=log_text.encode("utf-8", errors="replace"),
                        attachment_type=getattr(allure.attachment_type, "TEXT", None),
                    )
        except Exception:
            pass

    # 비디오: fixture teardown에서 stop_recording_screen() 결과를 저장해두고,
    # 여기서 상태에 따라 Allure에 첨부한다 (driver가 이미 quit 되어도 첨부 가능).
    record_video = bool(item.config.getoption("record_video"))
    video_bytes = getattr(item, "_recorded_video_bytes", None)
    if record_video and video_bytes and not getattr(item, "_allure_video_attached", False):
        if report.when == "teardown":
            any_failed = bool(getattr(item, "_allure_any_failed", False))
            any_skipped = bool(getattr(item, "_allure_any_skipped", False))
            if attach_all or any_failed or any_skipped:
                try:
                    stop_ts = getattr(item, "_video_stop_timestamp", timestamp)
                    status = "failed" if any_failed else "skipped" if any_skipped else "passed"
                    _safe_allure_attach(
                        name=f"video_{status}_teardown_{item.name}_{stop_ts}.mp4",
                        data=video_bytes,
                        attachment_type=getattr(allure.attachment_type, "MP4", None),
                    )
                    item._allure_video_attached = True
                except Exception:
                    pass


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    try:
        results_dir = config.getoption("allure_report_dir")
    except Exception:
        results_dir = None
    results_dir = results_dir or "allure-results"
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
                video_b64 = driver.stop_recording_screen()
                request.node._video_recording_stopped = True
                request.node._video_stop_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if video_b64:
                    request.node._recorded_video_bytes = base64.b64decode(video_b64)
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
                video_b64 = driver.stop_recording_screen()
                request.node._video_recording_stopped = True
                request.node._video_stop_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if video_b64:
                    request.node._recorded_video_bytes = base64.b64decode(video_b64)
            except Exception:
                pass

    driver.quit()


@pytest.fixture(scope="function")
def android_driver_logged_in(android_driver):
    """로그인 완료된 Android 드라이버.

    신규 테스트 작성 시 이 픽스처를 사용하면 로그인 모듈을 앞에 반복 작성하지 않아도 됩니다.
    """

    from utils.auth import login

    login(android_driver)
    return android_driver


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
                video_b64 = driver.stop_recording_screen()
                request.node._video_recording_stopped = True
                request.node._video_stop_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if video_b64:
                    request.node._recorded_video_bytes = base64.b64decode(video_b64)
            except Exception:
                pass

    driver.quit()
