"""
앱 화면 자동 탐색 및 UI 덤프 캡처 스크립트

사용법:
    python tools/explore_app.py

동작:
    1. 앱 실행 → 로그인 (필요 시)
    2. 각 하단 탭 (Home, History, Card, Event, Profile) 탐색
    3. 햄버거 메뉴 열어서 메뉴 항목 캡처
    4. 주요 서브 화면 진입 및 캡처
    5. 결과를 ui_dumps/explore_YYYYMMDD_HHMM/ 폴더에 저장
"""

import os
import sys
import time
import re
import xml.etree.ElementTree as ET
from datetime import datetime

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 프로젝트 루트 경로
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from config.capabilities import ANDROID_CAPS, get_appium_server_url
from utils.auth import login, _handle_simple_password_screen
from utils.initial_screens import handle_initial_screens
from utils.helpers import save_error_logcat

# Live / Staging 전환 설정
# USE_LIVE=True → Live 앱, False → Staging 앱
USE_LIVE = os.getenv("USE_LIVE", "true").lower() in ("true", "1", "yes")

if USE_LIVE:
    RID = "com.gmeremit.online.gmeremittance_native:id"
    _LOGIN_USER = os.getenv("LIVE_ID", "")
    _LOGIN_PIN = os.getenv("LIVE_PW", "")
    print(f"[config] Live 앱 모드 (패키지: {RID.split(':')[0]})")
else:
    RID = os.getenv(
        "GME_RESOURCE_ID_PREFIX",
        "com.gmeremit.online.gmeremittance_native.stag:id",
    )
    _LOGIN_USER = os.getenv("STG_ID", "")
    _LOGIN_PIN = os.getenv("STG_PW", "")
    print(f"[config] Staging 앱 모드 (패키지: {RID.split(':')[0]})")

# 간편비밀번호 (Simple Password)
_SIMPLE_PIN = os.getenv("SIMPLE_PIN", "1234")

# 캡처 파일 번호 카운터
_file_counter = 0

# 팝업 캡처 저장 폴더 (main에서 설정, dismiss_popup에서 자동 사용)
_popup_capture_folder = None


def _id(suffix):
    """리소스 ID 전체 경로 생성"""
    return f"{RID}/{suffix}"


def _enter_simple_pin(driver, pin=None):
    """Simple Password 잠금화면에서 PIN을 직접 입력합니다.

    숫자 키패드는 매번 랜덤 배치 → content-desc로 각 숫자를 찾아 클릭.
    우회(Login with ID/Password)가 아닌 직접 입력 방식.

    Args:
        pin: 4자리 PIN 문자열 (기본: _SIMPLE_PIN 환경변수)

    Returns:
        bool: PIN 입력 성공 여부
    """
    if pin is None:
        pin = _SIMPLE_PIN
    driver.implicitly_wait(0)
    try:
        for digit in pin:
            try:
                key = driver.find_element(
                    AppiumBy.XPATH,
                    f"//android.widget.ImageView[@content-desc='{digit}']"
                )
                key.click()
                time.sleep(0.3)
            except NoSuchElementException:
                print(f"  [pin] 숫자 '{digit}' 키 없음")
                return False
        print(f"  [pin] Simple PIN 입력 완료 ({len(pin)}자리)")
        return True
    finally:
        driver.implicitly_wait(2)


def next_idx():
    """순차 파일 번호 반환"""
    global _file_counter
    _file_counter += 1
    return _file_counter


def setup_driver():
    """Appium 드라이버 생성.

    이미 설치된 앱에 연결하기 위해:
    - app (APK 경로) 제거 → 재설치 방지
    - appPackage/appActivity 지정 → 기존 앱에 연결
    - noReset=True → 앱 데이터 보존 (로그인 세션 유지)
    """
    caps = dict(ANDROID_CAPS)
    caps["noReset"] = True

    # APK 경로 제거 (이미 설치된 앱 사용)
    caps.pop("app", None)

    # 앱 패키지/액티비티 지정
    pkg = RID.split(":")[0]
    caps["appPackage"] = pkg
    # Live: SplashScreen, Staging: ActivityMain
    if USE_LIVE:
        caps["appActivity"] = f"{pkg}.splash_screen.view.SplashScreen"
    else:
        caps["appActivity"] = f"{pkg}.splash_screen.view.ActivityMain"

    # Appium이 앱을 자동 실행 (autoLaunch 기본값 True)

    options = UiAutomator2Options()
    for k, v in caps.items():
        options.set_capability(k, v)

    print(f"[explore] Appium 서버 연결: {get_appium_server_url()}")
    driver = webdriver.Remote(get_appium_server_url(), options=options)
    driver.implicitly_wait(2)
    return driver


def save_dump(driver, folder, name, verify=True):
    """현재 화면 UI 덤프를 XML로 저장.

    Args:
        verify: True이면 캡처 전 팝업/시스템UI 여부 검증
    """
    idx = next_idx()

    # 캡처 전 화면 검증
    if verify:
        status = verify_app_screen(driver)
        if status == "popup":
            print(f"  [{idx:03d}] 팝업 감지 → 닫기 후 재캡처")
            dismiss_all_popups(driver, max_rounds=3)
            time.sleep(0.5)
        elif status == "system":
            print(f"  [{idx:03d}] 시스템 UI 감지 → 캡처 스킵 (복구 필요)")
            return None

    try:
        xml = driver.page_source

        # Activity 정보를 XML 주석으로 삽입
        try:
            activity = driver.current_activity or "unknown"
            package = driver.current_package or "unknown"
            comment = f"<!-- Activity: {activity} | Package: {package} -->\n"
            if xml.startswith("<?xml"):
                decl_end = xml.index("?>") + 2
                xml = xml[:decl_end] + "\n" + comment + xml[decl_end:].lstrip("\n")
            else:
                xml = comment + xml
        except Exception:
            pass

        filename = f"{idx:03d}_{name}.xml"
        filepath = os.path.join(folder, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml)
        size_kb = len(xml.encode('utf-8')) // 1024
        print(f"  [{idx:03d}] {filename} 저장 완료 ({size_kb}KB)")
        return filepath
    except Exception as e:
        print(f"  [{idx:03d}] {name}.xml 저장 실패: {e}")
        return None


def dismiss_popup(driver, max_attempts=5, capture_folder=None):
    """모달 팝업(배너/바텀시트/다이얼로그) 닫기.

    Args:
        capture_folder: 팝업 캡처 저장 폴더. None이면 _popup_capture_folder 사용.

    처리 순서:
    1. Renew Auto Debit: btn_okay ("Renew Account") 클릭 → iv_back으로 복귀
    2. In-App Banner: imgvCross (X 버튼) 또는 btnTwo ("Cancel")
    3. 공통: btn_close, btnCancel
    4. content-desc="close"
    5. touch_outside (바텀시트 외부)
    6. design_bottom_sheet → 백키
    7. 시스템 백키 (앱 종료 방지 안전장치 포함)
    """
    # 모듈 레벨 폴더가 설정되어 있으면 자동 사용
    if capture_folder is None:
        capture_folder = _popup_capture_folder
    driver.implicitly_wait(0)
    try:
        for attempt in range(max_attempts):
            closed = False

            # 1. Renew Auto Debit 팝업: btn_okay 클릭 → iv_back 복귀
            try:
                btn_okay = driver.find_element(AppiumBy.ID, _id("btn_okay"))
                if btn_okay.is_displayed():
                    # 팝업 캡처 (닫기 전)
                    if capture_folder:
                        save_dump(driver, capture_folder, "popup_renew_auto_debit", verify=False)
                    btn_okay.click()
                    print(f"  [popup] Renew Auto Debit → btn_okay 클릭 (시도 {attempt + 1})")
                    time.sleep(2)
                    # Renew 후 이동한 화면에서 뒤로가기
                    try:
                        back_btn = driver.find_element(AppiumBy.ID, _id("iv_back"))
                        back_btn.click()
                        print(f"  [popup] Renew 후 iv_back 복귀")
                        time.sleep(1.5)
                    except (NoSuchElementException, WebDriverException):
                        # iv_back 없으면 시스템 백키
                        driver.back()
                        print(f"  [popup] Renew 후 시스템 백키 복귀")
                        time.sleep(1.5)
                    closed = True
            except (NoSuchElementException, WebDriverException):
                pass

            if closed:
                continue

            # 2. 알려진 닫기 버튼들 (우선순위 순서)
            # btnCancel 제거: 초기 설정 화면에서 Cancel 누르면 앱 종료됨
            close_ids = [
                "imgvCross",      # In-App Banner X 버튼
                "btnTwo",         # In-App Banner "Cancel" 버튼
                "btn_close",      # 공통 닫기
                "btn_diaog_ok",   # Connection Failed 등 에러 팝업 OK 버튼 (resource-id 오타 그대로)
            ]
            for cid in close_ids:
                try:
                    el = driver.find_element(AppiumBy.ID, _id(cid))
                    if el.is_displayed():
                        # 팝업 캡처 (닫기 전)
                        if capture_folder:
                            save_dump(driver, capture_folder, f"popup_{cid}", verify=False)
                        el.click()
                        print(f"  [popup] {cid} 닫기 (시도 {attempt + 1})")
                        time.sleep(1)
                        closed = True
                        break
                except (NoSuchElementException, WebDriverException):
                    pass

            if closed:
                continue

            # 2. content-desc="close" 로 범용 닫기
            try:
                el = driver.find_element(
                    AppiumBy.XPATH, "//*[@content-desc='close']"
                )
                if el.is_displayed():
                    el.click()
                    print(f"  [popup] content-desc='close' 닫기 (시도 {attempt + 1})")
                    time.sleep(1)
                    closed = True
            except (NoSuchElementException, WebDriverException):
                pass

            if closed:
                continue

            # 3. touch_outside (바텀시트 외부 터치로 닫기)
            try:
                el = driver.find_element(AppiumBy.ID, _id("touch_outside"))
                if el.is_displayed():
                    el.click()
                    print(f"  [popup] touch_outside 닫기 (시도 {attempt + 1})")
                    time.sleep(1)
                    closed = True
            except (NoSuchElementException, WebDriverException):
                pass

            if closed:
                continue

            # 4. design_bottom_sheet가 보이면 시스템 백키로 닫기
            try:
                el = driver.find_element(AppiumBy.ID, _id("design_bottom_sheet"))
                if el.is_displayed():
                    driver.back()
                    print(f"  [popup] 바텀시트 → 백키 닫기 (시도 {attempt + 1})")
                    time.sleep(1.5)
                    closed = True
            except (NoSuchElementException, WebDriverException):
                pass

            if closed:
                continue

            # 5. 하단 탭이 보이면 팝업 없는 것으로 판단
            try:
                driver.find_element(
                    AppiumBy.XPATH, "//*[@content-desc='Home']"
                )
                # 하단 탭 보이면 팝업 없음 → 정상
                break
            except (NoSuchElementException, WebDriverException):
                # 하단 탭 안 보임 → 백키 시도 전에 앱 내인지 확인
                pkg = RID.split(":")[0]
                try:
                    current = driver.current_package
                    if current != pkg:
                        # 이미 앱 밖 → 백키 중단
                        print(f"  [popup] 앱 외부 감지 ({current}) → 백키 중단")
                        break
                    driver.back()
                    print(f"  [popup] 시스템 백키로 닫기 (시도 {attempt + 1})")
                    time.sleep(1.5)
                    # 백키 후 앱이 종료되었는지 확인
                    current_after = driver.current_package
                    if current_after != pkg:
                        print(f"  [popup] 백키로 앱 종료됨 → 앱 재활성화")
                        driver.activate_app(pkg)
                        time.sleep(3)
                        break
                except WebDriverException:
                    break
    finally:
        driver.implicitly_wait(2)


def dismiss_all_popups(driver, max_rounds=3, capture_folder=None):
    """팝업을 여러 라운드에 걸쳐 완전히 닫기.

    로그인 후 여러 팝업이 순차적으로 나타날 수 있어서
    한 번 dismiss 후 다시 확인하는 반복 로직.
    """
    # 모듈 레벨 폴더가 설정되어 있으면 자동 사용
    if capture_folder is None:
        capture_folder = _popup_capture_folder
    for round_num in range(max_rounds):
        # 팝업 닫기 시도
        dismiss_popup(driver, max_attempts=3, capture_folder=capture_folder)
        time.sleep(0.5)

        # 앱 화면이 정상인지 확인
        driver.implicitly_wait(0)
        try:
            # 하단 탭이 보이고 팝업 요소가 없으면 정상
            home_tab = driver.find_elements(
                AppiumBy.XPATH, "//*[@content-desc='Home']"
            )
            popup_elements = driver.find_elements(
                AppiumBy.ID, _id("imgvCross")
            ) + driver.find_elements(
                AppiumBy.ID, _id("touch_outside")
            ) + driver.find_elements(
                AppiumBy.ID, _id("design_bottom_sheet")
            )

            has_popup = any(el.is_displayed() for el in popup_elements if popup_elements)

            if home_tab and not has_popup:
                print(f"  [popup] 팝업 클리어 완료 (라운드 {round_num + 1})")
                break
        except (NoSuchElementException, WebDriverException):
            pass
        finally:
            driver.implicitly_wait(2)


def verify_app_screen(driver):
    """현재 화면이 실제 앱 화면인지 검증.

    Returns:
        str: "app" (앱 화면), "popup" (팝업 오버레이), "system" (시스템 UI/런처)
    """
    driver.implicitly_wait(0)
    try:
        # 앱 패키지명 확인 (page_source의 package 속성)
        try:
            source = driver.page_source[:2000]  # 상위 부분만 확인 (성능)
            if "com.android.systemui" in source:
                print("  [verify] 시스템 UI 감지 (notification panel)")
                return "system"
            if "com.google.android.apps.nexuslauncher" in source:
                print("  [verify] 런처 감지 (앱 크래시 의심)")
                return "system"
        except Exception:
            pass

        # 팝업 요소 확인
        popup_ids = ["imgvCross", "touch_outside", "design_bottom_sheet",
                     "bannerImageView", "inAppBannersViewPager"]
        for pid in popup_ids:
            try:
                el = driver.find_element(AppiumBy.ID, _id(pid))
                if el.is_displayed():
                    print(f"  [verify] 팝업 요소 발견: {pid}")
                    return "popup"
            except (NoSuchElementException, WebDriverException):
                pass

        # 하단 탭 확인 (앱 화면의 핵심 지표)
        try:
            driver.find_element(
                AppiumBy.XPATH, "//*[@content-desc='Home']"
            )
            return "app"
        except (NoSuchElementException, WebDriverException):
            pass

        # 서브 화면 확인 (iv_back 또는 btnBack 있으면 앱 서브화면)
        for back_id in ["iv_back", "btnBack", "toolbar_title"]:
            try:
                driver.find_element(AppiumBy.ID, _id(back_id))
                return "app"
            except (NoSuchElementException, WebDriverException):
                pass

        return "unknown"
    finally:
        driver.implicitly_wait(2)


def ensure_clean_screen(driver, max_retries=3):
    """팝업을 모두 닫고 앱 화면이 깨끗한 상태를 보장.

    Returns:
        bool: 앱 화면이 정상이면 True
    """
    for retry in range(max_retries):
        status = verify_app_screen(driver)
        if status == "app":
            return True
        elif status == "popup":
            print(f"  [clean] 팝업 감지 → 닫기 시도 (retry {retry + 1})")
            dismiss_popup(driver, max_attempts=5)
            time.sleep(1)
        elif status == "system":
            print(f"  [clean] 시스템 UI → 백키로 복귀 시도 (retry {retry + 1})")
            try:
                driver.back()
                time.sleep(2)
            except WebDriverException:
                return False
        else:
            # unknown → 백키 시도
            try:
                driver.back()
                time.sleep(1)
            except WebDriverException:
                return False

    return verify_app_screen(driver) == "app"


def click_tab(driver, content_desc, timeout=10):
    """하단 탭을 content-desc로 클릭 후 팝업까지 완전히 처리"""
    try:
        tab = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (AppiumBy.XPATH, f"//*[@content-desc='{content_desc}']")
            )
        )
        tab.click()
        print(f"  [tab] {content_desc} 탭 클릭")
        time.sleep(2)
        # 탭 전환 후 팝업 완전 닫기 (여러 라운드)
        dismiss_all_popups(driver, max_rounds=3)
        return True
    except (NoSuchElementException, TimeoutException):
        print(f"  [tab] {content_desc} 탭 클릭 실패")
        return False


def go_back_to_home(driver, max_attempts=5):
    """어떤 화면에서든 홈으로 안정적으로 복귀.

    전략:
    1. iv_back / btnBack 반복 클릭 (서브 화면 탈출)
    2. 시스템 백키 (드로어/팝업 닫기)
    3. Home 탭 직접 클릭
    4. 팝업 전체 정리
    """
    for attempt in range(max_attempts):
        # 팝업 먼저 정리
        dismiss_popup(driver, max_attempts=3)

        # Home 탭이 이미 보이고 선택된 상태인지 확인
        driver.implicitly_wait(0)
        try:
            home = driver.find_element(
                AppiumBy.XPATH, "//*[@content-desc='Home']"
            )
            if home.is_displayed():
                home.click()
                time.sleep(1.5)
                dismiss_all_popups(driver, max_rounds=2)
                driver.implicitly_wait(2)
                print(f"  [home] 홈 복귀 완료 (시도 {attempt + 1})")
                return True
        except (NoSuchElementException, WebDriverException):
            pass
        finally:
            driver.implicitly_wait(2)

        # iv_back 버튼으로 뒤로가기
        try:
            back = driver.find_element(AppiumBy.ID, _id("iv_back"))
            back.click()
            print(f"  [home] iv_back 클릭 (시도 {attempt + 1})")
            time.sleep(1.5)
            continue
        except (NoSuchElementException, WebDriverException):
            pass

        # btnBack 버튼
        try:
            back = driver.find_element(AppiumBy.ID, _id("btnBack"))
            back.click()
            print(f"  [home] btnBack 클릭 (시도 {attempt + 1})")
            time.sleep(1.5)
            continue
        except (NoSuchElementException, WebDriverException):
            pass

        # 시스템 백키
        try:
            driver.back()
            print(f"  [home] 시스템 백키 (시도 {attempt + 1})")
            time.sleep(1.5)
        except WebDriverException:
            pass

    print("  [home] 홈 복귀 실패 - 최대 시도 초과")
    return False


def go_back(driver):
    """뒤로가기"""
    try:
        back = driver.find_element(AppiumBy.ID, _id("iv_back"))
        back.click()
        time.sleep(1.5)
        dismiss_popup(driver)
        return
    except (NoSuchElementException, WebDriverException):
        pass

    # btnBack 시도
    try:
        back = driver.find_element(AppiumBy.ID, _id("btnBack"))
        back.click()
        time.sleep(1.5)
        dismiss_popup(driver)
        return
    except (NoSuchElementException, WebDriverException):
        pass

    try:
        driver.back()
        time.sleep(1.5)
        dismiss_popup(driver)
    except WebDriverException:
        pass


def get_app_package():
    """앱 패키지명 반환 (resource ID prefix에서 추출)"""
    # "com.gmeremit.online.gmeremittance_native.stag:id" → "com.gmeremit.online.gmeremittance_native.stag"
    return RID.split(":")[0]


def ensure_app_running(driver, max_retries=3):
    """앱이 실행 중인지 확인하고, 미실행 시 activate_app으로 시작.

    Returns:
        bool: 앱이 정상 실행 중이면 True
    """
    pkg = get_app_package()

    for retry in range(max_retries):
        # 현재 포그라운드 앱 확인
        try:
            current = driver.current_package
            print(f"  [app] 현재 패키지: {current}")
            if current == pkg:
                return True
        except Exception:
            pass

        # 앱이 포그라운드가 아니면 활성화
        print(f"  [app] 앱 활성화 시도 (retry {retry + 1})")
        try:
            driver.activate_app(pkg)
            time.sleep(5)  # 스플래시 스크린 대기
            current = driver.current_package
            print(f"  [app] 활성화 후 패키지: {current}")
            if current == pkg:
                return True
        except Exception as e:
            print(f"  [app] activate_app 실패: {e}")

    return False


def _handle_permission_guide(driver):
    """앱 최초 실행 시 권한 안내 화면 처리.

    'Guide for using the service' 화면에서 [Agree] (btnConfirm) 클릭.
    Cancel을 누르면 앱이 종료되므로 반드시 Agree를 눌러야 함.
    이후 Android 시스템 권한 팝업(Allow/Deny)도 처리.
    """
    driver.implicitly_wait(0)
    try:
        # 권한 안내 화면 확인 (tv_one: "Guide for using the service")
        try:
            el = driver.find_element(AppiumBy.ID, _id("btnConfirm"))
            if el.is_displayed():
                print("  [initial] 권한 안내 화면 → Agree 클릭")
                el.click()
                time.sleep(2)

                # Android 시스템 권한 팝업 처리 (Allow / While using the app)
                for _ in range(5):
                    try:
                        # "While using the app" 또는 "Allow"
                        allow_btn = driver.find_element(
                            AppiumBy.ID,
                            "com.android.permissioncontroller:id/permission_allow_foreground_only_button"
                        )
                        allow_btn.click()
                        print("  [initial] 시스템 권한 → Allow (foreground)")
                        time.sleep(1)
                        continue
                    except (NoSuchElementException, WebDriverException):
                        pass

                    try:
                        allow_btn = driver.find_element(
                            AppiumBy.ID,
                            "com.android.permissioncontroller:id/permission_allow_button"
                        )
                        allow_btn.click()
                        print("  [initial] 시스템 권한 → Allow")
                        time.sleep(1)
                        continue
                    except (NoSuchElementException, WebDriverException):
                        pass

                    try:
                        deny_btn = driver.find_element(
                            AppiumBy.ID,
                            "com.android.permissioncontroller:id/permission_deny_button"
                        )
                        deny_btn.click()
                        print("  [initial] 시스템 권한 → Deny (선택 권한)")
                        time.sleep(1)
                        continue
                    except (NoSuchElementException, WebDriverException):
                        break
        except (NoSuchElementException, WebDriverException):
            pass
    finally:
        driver.implicitly_wait(2)


def _wait_for_home_after_login(driver, folder, timeout=30):
    """로그인 후 Home 탭이 나타날 때까지 대기하면서 팝업 처리.

    dismiss_all_popups의 back 키가 앱을 종료시킬 수 있으므로,
    back 키 대신 알려진 팝업 버튼만 클릭하는 안전한 방식으로 처리.
    """
    import time as _t
    start = _t.time()
    while _t.time() - start < timeout:
        driver.implicitly_wait(0)
        try:
            # Home 탭이 보이면 성공
            driver.find_element(AppiumBy.XPATH, "//*[@content-desc='Home']")
            driver.implicitly_wait(2)
            print("  [post-login] Home 탭 발견 → 로그인 성공")
            # Home 도달 후 팝업 정리 (이제 back 키 사용 안전)
            dismiss_all_popups(driver, max_rounds=3)
            return True
        except (NoSuchElementException, WebDriverException):
            pass

        # 알려진 팝업/화면 요소 처리 (back 키 없이)
        handled = False

        # Renew Auto Debit 팝업
        try:
            btn = driver.find_element(AppiumBy.ID, _id("btn_okay"))
            if btn.is_displayed():
                if folder:
                    save_dump(driver, folder, "popup_renew_auto_debit", verify=False)
                btn.click()
                print("  [post-login] Renew Auto Debit → btn_okay 클릭")
                _t.sleep(2)
                try:
                    back = driver.find_element(AppiumBy.ID, _id("iv_back"))
                    back.click()
                    print("  [post-login] iv_back 복귀")
                except (NoSuchElementException, WebDriverException):
                    pass
                _t.sleep(1.5)
                handled = True
        except (NoSuchElementException, WebDriverException):
            pass

        # In-App Banner
        for cid in ["imgvCross", "btnTwo", "btn_close"]:
            try:
                el = driver.find_element(AppiumBy.ID, _id(cid))
                if el.is_displayed():
                    if folder:
                        save_dump(driver, folder, f"popup_{cid}", verify=False)
                    el.click()
                    print(f"  [post-login] 팝업 닫기: {cid}")
                    _t.sleep(1)
                    handled = True
                    break
            except (NoSuchElementException, WebDriverException):
                pass

        # Connection Failed 등 에러 팝업
        try:
            el = driver.find_element(AppiumBy.ID, _id("btn_diaog_ok"))
            if el.is_displayed():
                el.click()
                print("  [post-login] 에러 팝업 → OK 클릭")
                _t.sleep(1)
                handled = True
        except (NoSuchElementException, WebDriverException):
            pass

        # 지문 인증 설정 (나중에)
        try:
            el = driver.find_element(AppiumBy.ID, _id("txt_pennytest_msg"))
            if el.is_displayed():
                el.click()
                print("  [post-login] 지문 인증 → 나중에")
                _t.sleep(1)
                handled = True
        except (NoSuchElementException, WebDriverException):
            pass

        # 보이스피싱 경고
        try:
            el = driver.find_element(AppiumBy.ID, _id("check_customer"))
            if el.is_displayed():
                el.click()
                _t.sleep(0.5)
                # 확인 버튼
                for txt in ["확인", "OK", "Ok"]:
                    try:
                        btn = driver.find_element(
                            AppiumBy.XPATH, f"//android.widget.Button[@text='{txt}']")
                        btn.click()
                        break
                    except (NoSuchElementException, WebDriverException):
                        pass
                print("  [post-login] 보이스피싱 경고 처리")
                _t.sleep(1)
                handled = True
        except (NoSuchElementException, WebDriverException):
            pass

        driver.implicitly_wait(2)

        if not handled:
            _t.sleep(2)
            print(f"  [post-login] 대기 중... ({int(_t.time() - start)}초)")

    # 타임아웃 → 디버그 덤프 + logcat
    print("  [post-login] Home 탭 미도달 (타임아웃)")
    if folder:
        save_dump(driver, folder, "debug_post_login_timeout", verify=False)
        save_error_logcat(driver, folder, "error_post_login_timeout")
    return False


def check_login_needed(driver):
    """로그인이 필요한지 확인.

    먼저 앱이 실행 중인지 확인 후 로그인 요소를 찾습니다.
    """
    try:
        driver.find_element(AppiumBy.ID, _id("usernameId"))
        return True
    except NoSuchElementException:
        pass
    try:
        driver.find_element(AppiumBy.ID, _id("btn_lgn"))
        return True
    except NoSuchElementException:
        pass
    return False


def scroll_down(driver, times=1):
    """화면 아래로 스크롤"""
    size = driver.get_window_size()
    start_x = size['width'] // 2
    start_y = int(size['height'] * 0.7)
    end_y = int(size['height'] * 0.3)
    for _ in range(times):
        driver.swipe(start_x, start_y, start_x, end_y, 800)
        time.sleep(1)


def scroll_up(driver, times=1):
    """화면 위로 스크롤"""
    size = driver.get_window_size()
    start_x = size['width'] // 2
    start_y = int(size['height'] * 0.3)
    end_y = int(size['height'] * 0.7)
    for _ in range(times):
        driver.swipe(start_x, start_y, start_x, end_y, 800)
        time.sleep(1)


def _extract_visible_texts(page_source):
    """XML page_source에서 표시된 텍스트 값들을 추출 (빈 값 제외).

    스크롤 전/후 화면 비교에 사용.
    text 속성뿐 아니라 content-desc도 포함하여 이미지 버튼도 감지.
    """
    texts = set(t for t in re.findall(r'text="([^"]*)"', page_source) if t.strip())
    descs = set(d for d in re.findall(r'content-desc="([^"]*)"', page_source) if d.strip())
    return texts | descs


def _log_interactive_elements(sources, base_name):
    """캡처된 page_source(XML) 목록에서 모든 인터랙티브 요소를 분류·출력.

    스크롤 전/후 캡처한 XML을 합쳐서 분석하므로,
    화면 전체(위~아래)의 모든 클릭/토글/스와이프 가능 요소를 확인할 수 있음.

    분류 기준:
    - nav_buttons: clickable + text 있음 (화면 이동 버튼)
    - icon_buttons: clickable + text 없음 (아이콘 버튼, ImageView 등)
    - toggles: checkable 또는 Switch/ToggleButton 클래스
    - viewpagers: ViewPager/RecyclerView with scrollable + horizontal-scroll
    - scrollable: scrollable="true" (스크롤 가능 영역)

    Args:
        sources: page_source(XML 문자열) 리스트
        base_name: 화면 식별용 이름 (로그 출력용)
    """
    # 하단 네비게이션/시스템 UI 요소 제외 목록
    SKIP_IDS = {
        "navigation_home", "navigation_history", "navigation_card",
        "navigation_event", "navigation_profile",
        "statusBarBackground", "navigationBarBackground",
        "action_bar_root", "content",
    }
    # 결과 저장: resource-id 기준으로 중복 제거
    nav_buttons = {}      # resource-id → (text, content-desc, class)
    icon_buttons = {}
    toggles = {}
    viewpagers = {}
    scrollables = {}

    for source in sources:
        try:
            root = ET.fromstring(source)
        except ET.ParseError:
            continue

        for elem in root.iter():
            rid = elem.get("resource-id", "")
            # 패키지명 접두사 제거 (예: com.gmeremit.online:id/btn_ok → btn_ok)
            short_id = rid.split("/")[-1] if "/" in rid else rid
            if short_id in SKIP_IDS or not short_id:
                continue

            cls = elem.get("class", "")
            text = elem.get("text", "").strip()
            desc = elem.get("content-desc", "").strip()
            clickable = elem.get("clickable") == "true"
            checkable = elem.get("checkable") == "true"
            scrollable = elem.get("scrollable") == "true"
            display = text or desc or short_id

            # 토글/스위치 분류
            if checkable or cls in ("android.widget.Switch", "android.widget.ToggleButton"):
                toggles[short_id] = (display, cls)
            # ViewPager 분류
            elif "ViewPager" in cls:
                viewpagers[short_id] = (display, cls)
            # 스크롤 가능 영역
            elif scrollable:
                scrollables[short_id] = (display, cls)
            # 클릭 가능 요소 분류
            elif clickable:
                if text or desc:
                    nav_buttons[short_id] = (display, cls)
                else:
                    icon_buttons[short_id] = (short_id, cls)

    # 리포트 출력
    total = len(nav_buttons) + len(icon_buttons) + len(toggles) + len(viewpagers)
    print(f"\n  [검증] {base_name}: 인터랙티브 요소 총 {total}개 발견")
    if nav_buttons:
        print(f"    ▸ 버튼 ({len(nav_buttons)}개): {', '.join(nav_buttons.keys())}")
    if icon_buttons:
        print(f"    ▸ 아이콘 버튼 ({len(icon_buttons)}개): {', '.join(icon_buttons.keys())}")
    if toggles:
        print(f"    ▸ 토글/스위치 ({len(toggles)}개): {', '.join(toggles.keys())}")
    if viewpagers:
        print(f"    ▸ ViewPager ({len(viewpagers)}개): {', '.join(viewpagers.keys())}")
    if scrollables:
        print(f"    ▸ 스크롤 영역 ({len(scrollables)}개): {', '.join(scrollables.keys())}")

    return {
        "nav_buttons": nav_buttons,
        "icon_buttons": icon_buttons,
        "toggles": toggles,
        "viewpagers": viewpagers,
        "scrollables": scrollables,
    }


def _capture_viewpager_pages(driver, folder, base_name):
    """ViewPager를 감지하고, 가로 스와이프하여 각 페이지를 캡처.

    동작 원리:
    1. page_source에서 ViewPager 요소 검색
    2. dotsIndicator (페이지 인디케이터)로 페이지 수 파악
    3. 현재 페이지 이후의 페이지를 스와이프하며 캡처
    4. 캡처 완료 후 원래 페이지로 복귀

    Args:
        driver: Appium 드라이버
        folder: 저장 폴더
        base_name: 파일명 기본 접두사

    Returns:
        list: 저장된 파일 경로 목록
    """
    saved_files = []
    try:
        source = driver.page_source
        root = ET.fromstring(source)
    except Exception:
        return saved_files

    # ViewPager 요소 찾기
    viewpager = None
    for elem in root.iter():
        cls = elem.get("class", "")
        if "ViewPager" in cls:
            viewpager = elem
            break

    if viewpager is None:
        return saved_files

    # ViewPager 영역 좌표 추출
    bounds_str = viewpager.get("bounds", "")
    if not bounds_str:
        return saved_files

    # bounds 파싱: "[x1,y1][x2,y2]"
    coords = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
    if len(coords) < 2:
        return saved_files
    x1, y1 = int(coords[0][0]), int(coords[0][1])
    x2, y2 = int(coords[1][0]), int(coords[1][1])

    # dotsIndicator로 페이지 수 파악
    page_count = 0
    for elem in root.iter():
        rid = elem.get("resource-id", "")
        if "dotsIndicator" in rid or "dots_indicator" in rid or "page_indicator" in rid:
            # 인디케이터의 자식 수 = 페이지 수
            page_count = len(list(elem))
            break

    if page_count <= 1:
        # 인디케이터를 못 찾으면 2페이지로 가정하고 1회 스와이프 시도
        page_count = 2

    vp_rid = viewpager.get("resource-id", "ViewPager")
    short_id = vp_rid.split("/")[-1] if "/" in vp_rid else vp_rid
    print(f"  [ViewPager] {base_name}: '{short_id}' 감지 - {page_count}페이지")

    # 스와이프 좌표 계산 (ViewPager 영역 내에서 가로 스와이프)
    center_y = (y1 + y2) // 2
    swipe_start_x = x1 + int((x2 - x1) * 0.8)   # 오른쪽에서
    swipe_end_x = x1 + int((x2 - x1) * 0.2)      # 왼쪽으로

    # 현재 첫 페이지는 이미 캡처됨 → 2번째 페이지부터 캡처
    swipe_count = 0
    for page_num in range(2, page_count + 1):
        driver.swipe(swipe_start_x, center_y, swipe_end_x, center_y, 600)
        swipe_count += 1
        time.sleep(1)

        page_suffix = f"vp_page{page_num}"
        print(f"  [ViewPager] {base_name}: 페이지 {page_num}/{page_count} 캡처")
        filepath = save_dump(driver, folder, f"{base_name}_{page_suffix}", verify=False)
        if filepath:
            saved_files.append(filepath)

    # 원래 페이지로 복귀 (역방향 스와이프)
    for _ in range(swipe_count):
        driver.swipe(swipe_end_x, center_y, swipe_start_x, center_y, 600)
        time.sleep(0.5)

    return saved_files


def scroll_and_capture(driver, folder, base_name, max_scrolls=5, verify=True):
    """화면을 스크롤하면서 각 위치의 UI 덤프를 캡처.

    동작 원리:
    1. 초기 화면 캡처 (base_name)
    2. 스크롤 다운 후 화면 텍스트 비교
    3. 새로운 콘텐츠가 발견되면 캡처 (base_name_scrolled, base_name_scrolled_2, ...)
    4. 새 콘텐츠 없으면 중지 (하단 도달)
    5. 스크롤한 만큼 다시 올려서 원위치 복귀

    Args:
        driver: Appium 드라이버
        folder: 저장 폴더
        base_name: 파일명 기본 접두사 (예: "card_main", "menu_Settings")
        max_scrolls: 최대 스크롤 횟수 (기본 5)
        verify: save_dump 시 팝업/시스템UI 검증 여부 (기본 True)

    Returns:
        list: 저장된 파일 경로 목록
    """
    saved_files = []
    all_seen_texts = set()
    captured_sources = []  # 검증용: 각 스크롤 위치의 page_source 수집
    scroll_count = 0

    # 1. 초기 화면 캡처
    filepath = save_dump(driver, folder, base_name, verify=verify)
    if filepath:
        saved_files.append(filepath)

    try:
        initial_source = driver.page_source
        all_seen_texts = _extract_visible_texts(initial_source)
        captured_sources.append(initial_source)
    except Exception:
        return saved_files

    # 2. 스크롤하면서 캡처
    for scroll_num in range(1, max_scrolls + 1):
        scroll_down(driver)
        scroll_count += 1
        time.sleep(0.5)

        try:
            current_source = driver.page_source
        except Exception:
            break

        current_texts = _extract_visible_texts(current_source)
        new_texts = current_texts - all_seen_texts

        if not new_texts:
            print(f"  [scroll] {base_name}: 스크롤 {scroll_num}회 - 새 콘텐츠 없음 → 중지")
            break

        # 파일명: base_name_scrolled (1회차), base_name_scrolled_2 (2회차), ...
        suffix = "scrolled" if scroll_num == 1 else f"scrolled_{scroll_num}"
        print(f"  [scroll] {base_name}: 스크롤 {scroll_num}회 - 신규 텍스트 {len(new_texts)}개")
        filepath = save_dump(driver, folder, f"{base_name}_{suffix}", verify=verify)
        if filepath:
            saved_files.append(filepath)
        all_seen_texts |= current_texts
        captured_sources.append(current_source)

    # 3. 원위치 복귀 (스크롤한 만큼 올리기)
    if scroll_count > 0:
        scroll_up(driver, times=scroll_count)

    # 4. 인터랙티브 요소 검증 리포트 출력
    if captured_sources:
        _log_interactive_elements(captured_sources, base_name)

    # 5. ViewPager 감지 시 가로 스와이프 캡처
    vp_files = _capture_viewpager_pages(driver, folder, base_name)
    saved_files.extend(vp_files)

    return saved_files


# =========================================================================
# 각 탭 탐색 함수
# =========================================================================

def explore_home(driver, folder):
    """Home 탭 탐색"""
    print("\n===== [HOME] 탭 탐색 =====")
    click_tab(driver, "Home")
    ensure_clean_screen(driver)
    scroll_and_capture(driver, folder, "home_main")

    # 알림 화면은 생략 (이전 캡처에서 확인 완료, Appium 불안정 유발)


def explore_hamburger(driver, folder):
    """햄버거 메뉴(Side Drawer) 탐색 - 개선된 복귀 로직"""
    print("\n===== [HAMBURGER MENU] 탐색 =====")
    click_tab(driver, "Home", timeout=5)
    time.sleep(1)

    try:
        nav = driver.find_element(AppiumBy.ID, _id("iv_nav"))
        nav.click()
        print("  [click] 햄버거 메뉴 열기")
        time.sleep(2)
        # 드로어도 스크롤하며 캡처 (verify=False: 드로어는 오버레이)
        scroll_and_capture(driver, folder, "hamburger_menu", verify=False)

        # 메뉴 항목: resource ID 기반으로 직접 클릭 (텍스트 기반보다 안정적)
        # APP_STRUCTURE.md에서 확인된 메뉴 항목
        menu_by_id = [
            ("manageAccountsViewGroup", "Link_Bank_Account"),
            ("manageInboundAccountsViewGroup", "Inbound_Account"),
            ("manageHistoryViewGroup", "History_Menu"),
            ("view_branch", "Branch"),
            ("view_about_gme", "About_GME"),
            ("view_setting", "Settings"),
            ("privacypolicy", "Privacy_Policy"),
            ("termsconditions", "Terms_and_Conditions"),
            # view_logout 제외
        ]

        for rid, name in menu_by_id:
            # 홈으로 복귀 확인
            if not go_back_to_home(driver):
                print(f"  [error] 홈 복귀 실패 → 메뉴 탐색 중단")
                break
            time.sleep(1)

            # 드로어 열기
            if not _open_drawer(driver):
                print(f"  [error] 드로어 열기 실패 → '{name}' 스킵")
                continue
            time.sleep(1)

            try:
                el = driver.find_element(AppiumBy.ID, _id(rid))
                el.click()
                print(f"  [click] 메뉴: {name} ({rid})")
                time.sleep(2)
                dismiss_all_popups(driver, max_rounds=2)
                ensure_clean_screen(driver)

                # 메뉴 화면 + 스크롤 캡처
                scroll_and_capture(driver, folder, f"menu_{name}")

                # 서브 탭이 있으면 캡처 (각 탭에서도 스크롤)
                _capture_sub_tabs(driver, folder, f"menu_{name}")

            except NoSuchElementException:
                print(f"  [warn] 메뉴 '{name}' ({rid}) 없음 → 스킵")
            except Exception as e:
                print(f"  [error] 메뉴 '{name}' 접근 실패: {e}")

        # 마지막에 홈으로 복귀
        go_back_to_home(driver)

    except NoSuchElementException:
        print("  [error] 햄버거 메뉴 버튼 없음")


def _collect_drawer_items(driver):
    """드로어에서 메뉴 항목 텍스트 수집"""
    texts = []
    seen = set()

    # 여러 패턴으로 텍스트 수집
    xpaths = [
        "//android.widget.NavigationView//android.widget.TextView",
        "//androidx.drawerlayout.widget.DrawerLayout//android.widget.TextView",
        "//android.widget.ListView//android.widget.TextView",
        "//androidx.recyclerview.widget.RecyclerView//android.widget.TextView",
        "//*[@clickable='true']//android.widget.TextView",
    ]

    for xpath in xpaths:
        try:
            elements = driver.find_elements(AppiumBy.XPATH, xpath)
            for el in elements:
                text = (el.get_attribute("text") or "").strip()
                if text and text not in seen and len(text) > 1:
                    seen.add(text)
                    texts.append(text)
        except Exception:
            pass

    return texts


def _open_drawer(driver):
    """드로어 열기 (홈에서).

    Returns:
        bool: 드로어 열기 성공 여부
    """
    try:
        # 먼저 Home 탭 확인
        driver.find_element(
            AppiumBy.XPATH, "//*[@content-desc='Home' and @selected='true']"
        )
    except NoSuchElementException:
        click_tab(driver, "Home", timeout=5)
        time.sleep(1)

    try:
        nav = driver.find_element(AppiumBy.ID, _id("iv_nav"))
        nav.click()
        time.sleep(1.5)

        # 드로어가 실제로 열렸는지 확인
        driver.implicitly_wait(0)
        try:
            driver.find_element(AppiumBy.ID, _id("iv_close"))
            print("  [drawer] 드로어 열기 성공")
            return True
        except NoSuchElementException:
            # iv_close 없어도 nav_drawer 확인
            try:
                driver.find_element(AppiumBy.ID, _id("nav_drawer"))
                print("  [drawer] 드로어 열기 성공")
                return True
            except NoSuchElementException:
                print("  [warn] 드로어 열기 확인 실패")
                return False
        finally:
            driver.implicitly_wait(2)
    except NoSuchElementException:
        print("  [warn] 햄버거 버튼 없음")
        return False


def _capture_sub_tabs(driver, folder, prefix):
    """현재 화면의 서브 탭을 캡처 (각 탭에서 스크롤 캡처 수행)"""
    try:
        # HorizontalScrollView 내 탭
        tabs = driver.find_elements(
            AppiumBy.XPATH,
            "//android.widget.HorizontalScrollView//android.widget.TextView"
        )
        if len(tabs) > 1:
            for tab in tabs[1:]:
                try:
                    text = (tab.get_attribute("text") or "").strip()
                    if text:
                        tab.click()
                        time.sleep(1.5)
                        safe = re.sub(r'[^\w]', '_', text).strip('_')
                        # 각 탭에서 스크롤하며 캡처
                        scroll_and_capture(driver, folder, f"{prefix}_{safe}")
                except Exception:
                    pass
    except Exception:
        pass

    # TabLayout 내 탭
    try:
        tabs = driver.find_elements(
            AppiumBy.XPATH,
            "//com.google.android.material.tabs.TabLayout//android.widget.TextView"
        )
        if len(tabs) > 1:
            for tab in tabs[1:]:
                try:
                    text = (tab.get_attribute("text") or "").strip()
                    if text:
                        tab.click()
                        time.sleep(1.5)
                        safe = re.sub(r'[^\w]', '_', text).strip('_')
                        # 각 탭에서 스크롤하며 캡처
                        scroll_and_capture(driver, folder, f"{prefix}_{safe}")
                except Exception:
                    pass
    except Exception:
        pass


def explore_history(driver, folder):
    """History 탭 탐색 (팝업 완전 제거 후 캡처)"""
    print("\n===== [HISTORY] 탭 탐색 =====")

    # History 탭 클릭 + 팝업 정리
    if not click_tab(driver, "History"):
        print("  [error] History 탭 클릭 실패")
        return

    # 화면 안정화 대기 + 추가 팝업 제거
    time.sleep(1)
    ensure_clean_screen(driver)
    save_dump(driver, folder, "history_main")

    # 카테고리 탭 (Overseas, Schedule History, Domestic, Inbound)
    for tab_name in ["Overseas", "Schedule History", "Domestic", "Inbound"]:
        try:
            tab = driver.find_element(
                AppiumBy.XPATH,
                f"//*[@content-desc='{tab_name}' or @text='{tab_name}']"
            )
            tab.click()
            time.sleep(1.5)
            safe = re.sub(r'[^\w ]', '_', tab_name).strip('_')
            save_dump(driver, folder, f"history_{safe}")
            print(f"  [tab] History > {tab_name}")
        except NoSuchElementException:
            print(f"  [skip] History > {tab_name}")

    # My Usage 버튼
    try:
        usage = driver.find_element(AppiumBy.ID, _id("usages"))
        usage.click()
        print("  [click] My Usage")
        time.sleep(2)
        dismiss_all_popups(driver)
        ensure_clean_screen(driver)
        save_dump(driver, folder, "history_my_usage")
        go_back(driver)
    except NoSuchElementException:
        print("  [skip] My Usage 버튼 없음")

    # History 내 RecyclerView 항목 탐색
    click_tab(driver, "History", timeout=5)
    time.sleep(1)

    # 스크롤해서 카테고리 항목 찾기
    categories = ["Remittance", "Account", "GMEPay", "Top-up", "Coupon Box"]
    for cat in categories:
        try:
            el = driver.find_element(
                AppiumBy.XPATH,
                f"//android.widget.TextView[contains(@text, '{cat}')]"
            )
            el.click()
            print(f"  [click] History > {cat}")
            time.sleep(2)
            dismiss_all_popups(driver)
            safe = re.sub(r'[^\w]', '_', cat).strip('_')
            save_dump(driver, folder, f"history_cat_{safe}")

            # 서브 탭 캡처
            _capture_sub_tabs(driver, folder, f"history_cat_{safe}")

            go_back(driver)
            time.sleep(1)
            click_tab(driver, "History", timeout=5)
            time.sleep(1)
        except NoSuchElementException:
            pass


def explore_card(driver, folder):
    """Card 탭 탐색 (팝업 완전 제거 후 캡처)"""
    print("\n===== [CARD] 탭 탐색 =====")
    if not click_tab(driver, "Card"):
        print("  [error] Card 탭 클릭 실패")
        return

    time.sleep(1)
    ensure_clean_screen(driver)
    scroll_and_capture(driver, folder, "card_main")

    # 서브 탭 캡처 (각 탭에서도 스크롤 캡처 수행)
    _capture_sub_tabs(driver, folder, "card")


def _has_screen_changed(before_texts, driver):
    """클릭 전/후 화면이 변했는지 판별.

    클릭 후 page_source의 텍스트를 추출하여, 클릭 전 텍스트와 비교.
    새로운 텍스트가 3개 이상이거나, 전체 텍스트의 30% 이상 변했으면 화면 전환으로 판단.

    Returns:
        tuple: (changed: bool, after_source: str)
    """
    try:
        after_source = driver.page_source
    except Exception:
        return False, ""
    after_texts = _extract_visible_texts(after_source)
    new_texts = after_texts - before_texts
    removed_texts = before_texts - after_texts
    total_change = len(new_texts) + len(removed_texts)
    total_all = len(before_texts | after_texts) or 1

    change_ratio = total_change / total_all
    changed = len(new_texts) >= 3 or change_ratio >= 0.3

    if changed:
        print(f"    → 화면 변화 감지 (신규 텍스트 {len(new_texts)}개, 변화율 {change_ratio:.0%})")
    else:
        print(f"    → 화면 변화 없음 (신규 텍스트 {len(new_texts)}개, 변화율 {change_ratio:.0%})")
    return changed, after_source


def explore_card_3rd_depth(driver, folder):
    """Card 탭 3rd depth 서브화면 캡처 (c1~c12)

    Card Features 화면에서 클릭 가능한 요소를 하나씩 진입 → 캡처 → 복귀.

    핵심 로직:
    - 클릭 전 화면 텍스트 저장 → 클릭 → 화면 변화 감지 → 변화 있으면 캡처
    - 클릭 후 dismiss_all_popups를 호출하지 않음 (서브화면을 닫아버리는 문제 방지)
    - 서브화면에서는 save_dump만 사용 (ViewPager 중복 캡처 방지)

    특수 처리:
    - c9 (upArrow): 화면 이동이 아닌 UI 확장 → 현재 화면 캡처
    - c10 (ViewPager +): 스와이프 후 + 버튼 클릭
    - c11~c12: 스크롤 아래 요소 → 스크롤 후 접근
    """
    print("\n===== [CARD 3rd Depth] 서브화면 탐색 =====")

    def _go_to_card():
        """Card 탭으로 이동 + 팝업 정리 (탐색 시작 전에만 사용)"""
        if not click_tab(driver, "Card"):
            return False
        time.sleep(2)
        dismiss_all_popups(driver, max_rounds=2)
        ensure_clean_screen(driver)
        return True

    def _get_card_texts():
        """현재 Card 화면의 텍스트를 추출 (비교 기준용)"""
        try:
            return _extract_visible_texts(driver.page_source)
        except Exception:
            return set()

    if not _go_to_card():
        print("  [error] Card 탭 클릭 실패")
        return

    # --- 초기 화면(스크롤 없이 보이는) 요소들 ---
    # popup_type: 클릭 시 팝업/바텀시트로 열리는 요소 (verify=False로 캡처)
    top_elements = [
        ("c1", "llBalance", "Balance_Detail", False),
        ("c2", "btn_gme_wallet_transfer", "Transfer", False),
        ("c3", "btn_gme_wallet_deposit", "Deposit", False),
        ("c4", "rlCashBackView", "Cashback", False),
        ("c5", "rlCardUsageView", "Card_Usage", False),
        ("c6", "rlTransportationHistoryView", "Transportation_History", False),
        ("c7", "zeropay_scan_icon", "QR_Scan", True),
        ("c8", "transferIcon", "Transport_Charge", True),
    ]

    for code, rid, name, is_popup in top_elements:
        # 매번 Card 탭에서 시작
        if not _go_to_card():
            print(f"  [error] Card 복귀 실패 → 중단")
            return

        try:
            # 클릭 전 화면 텍스트 저장
            before_texts = _get_card_texts()

            el = driver.find_element(AppiumBy.ID, _id(rid))
            el.click()
            print(f"  [click] {code}: {name} ({rid})")
            time.sleep(2.5)

            # 화면 변화 감지 (dismiss_all_popups 호출 안 함!)
            changed, _ = _has_screen_changed(before_texts, driver)

            if changed:
                # 팝업/바텀시트 요소는 verify=False로 캡처 (닫히는 것 방지)
                save_dump(driver, folder, f"card3_{code}_{name}", verify=not is_popup)

                if is_popup:
                    # 팝업 형태는 스크롤 불필요 → back으로 닫기
                    print(f"    → 팝업/바텀시트 형태 → 캡처 후 닫기")
                    driver.back()
                    time.sleep(1)
                else:
                    # 일반 서브화면: 스크롤 아래 콘텐츠 확인
                    scroll_down(driver)
                    time.sleep(0.5)
                    try:
                        scrolled_source = driver.page_source
                        scrolled_texts = _extract_visible_texts(scrolled_source)
                        if scrolled_texts - before_texts:
                            save_dump(driver, folder, f"card3_{code}_{name}_scrolled")
                    except Exception:
                        pass
                    scroll_up(driver, times=1)
                    # 복귀: iv_back → 실패 시 Android back
                    go_back(driver)
                    time.sleep(1)
            else:
                print(f"  [skip] {code}: 화면 변화 없음 → 캡처 생략")
                # 변화 없어도 복귀 시도 (혹시 이동했을 수 있으므로)
                go_back(driver)
                time.sleep(1)

        except NoSuchElementException:
            print(f"  [warn] {code}: '{rid}' 요소 없음 → 스킵")
        except Exception as e:
            print(f"  [error] {code}: {name} - {e}")
            try:
                driver.back()
                time.sleep(1)
            except Exception:
                pass

    # --- c9: upArrow (확장 메뉴 - 화면 이동 아님, UI 확장) ---
    print("\n  --- c9: upArrow (확장 메뉴) ---")
    if not _go_to_card():
        print("  [error] Card 복귀 실패")
        return

    try:
        before_texts = _get_card_texts()
        arrow = driver.find_element(AppiumBy.ID, _id("upArrow"))
        arrow.click()
        print("  [click] c9: upArrow (메뉴 확장)")
        time.sleep(1.5)

        changed, _ = _has_screen_changed(before_texts, driver)
        if changed:
            save_dump(driver, folder, "card3_c9_Expanded_Menu")
        else:
            print("  [skip] c9: 변화 없음 → 캡처 생략")

        # 다시 접기
        try:
            arrow2 = driver.find_element(AppiumBy.ID, _id("upArrow"))
            arrow2.click()
            time.sleep(0.5)
        except Exception:
            pass
    except NoSuchElementException:
        print("  [warn] c9: 'upArrow' 없음 → 스킵")
    except Exception as e:
        print(f"  [error] c9: upArrow - {e}")

    # --- c10: ViewPager 2페이지 → '+' 버튼 (카드 추가) ---
    print("\n  --- c10: ViewPager + 버튼 (카드 추가) ---")
    if not _go_to_card():
        print("  [error] Card 복귀 실패")
        return

    try:
        before_texts = _get_card_texts()

        # ViewPager 영역 찾기
        vp = driver.find_element(AppiumBy.ID, _id("gmeCardViewPager"))
        vp_rect = vp.rect
        print(f"  [info] ViewPager 영역: x={vp_rect['x']}, y={vp_rect['y']}, "
              f"w={vp_rect['width']}, h={vp_rect['height']}")

        center_y = vp_rect['y'] + vp_rect['height'] // 2
        # 스와이프 범위를 ViewPager 내부로 확실히 제한
        margin = int(vp_rect['width'] * 0.1)
        swipe_start = vp_rect['x'] + vp_rect['width'] - margin  # 우측 끝 근처
        swipe_end = vp_rect['x'] + margin                        # 좌측 끝 근처

        # 오른쪽 → 왼쪽 스와이프 (느린 속도로 확실하게)
        driver.swipe(swipe_start, center_y, swipe_end, center_y, 1000)
        print("  [swipe] ViewPager → 2페이지 (시도 1)")
        time.sleep(2)

        changed, _ = _has_screen_changed(before_texts, driver)
        if not changed:
            # 재시도: 더 느리게 + 약간 다른 y좌표
            alt_y = vp_rect['y'] + int(vp_rect['height'] * 0.4)
            driver.swipe(swipe_start, alt_y, swipe_end, alt_y, 1500)
            print("  [swipe] ViewPager → 2페이지 (시도 2, 느린 속도)")
            time.sleep(2)
            changed, _ = _has_screen_changed(before_texts, driver)

        if not changed:
            # 3차 시도: 화면 전체 너비 기준 스와이프
            screen = driver.get_window_size()
            sw = screen['width']
            driver.swipe(int(sw * 0.85), center_y, int(sw * 0.15), center_y, 1200)
            print("  [swipe] ViewPager → 2페이지 (시도 3, 전체 너비)")
            time.sleep(2)
            changed, _ = _has_screen_changed(before_texts, driver)

        if changed:
            # 2페이지 캡처 (verify=False: 팝업 아닌 정상 화면)
            save_dump(driver, folder, "card3_c10_ViewPager_Page2", verify=False)

            # 2페이지에서 클릭 가능한 요소 탐색 (+ 버튼 찾기)
            try:
                source_p2 = driver.page_source
                root = ET.fromstring(source_p2)
                # clickable 요소 중 ViewPager 내부의 것을 모두 로그
                vp_clickables = []
                for elem in root.iter():
                    if elem.get("clickable") == "true":
                        rid_val = elem.get("resource-id", "")
                        short = rid_val.split("/")[-1] if "/" in rid_val else rid_val
                        text = elem.get("text", "")
                        desc = elem.get("content-desc", "")
                        cls = elem.get("class", "")
                        vp_clickables.append((short, text, desc, cls))
                if vp_clickables:
                    print(f"    → 2페이지 클릭 가능 요소 {len(vp_clickables)}개:")
                    for s, t, d, c in vp_clickables[:10]:
                        label = t or d or s or c
                        print(f"      - {s}: '{label}'")
            except Exception:
                pass

            # '+' 버튼 클릭 시도
            plus_ids = ["iv_add_card", "btn_add_card", "addCard", "add_card",
                        "imgAddCard", "add_new_card", "btnAddCard"]
            plus_clicked = False
            for pid in plus_ids:
                try:
                    plus_btn = driver.find_element(AppiumBy.ID, _id(pid))
                    plus_btn.click()
                    plus_clicked = True
                    print(f"  [click] c10: + 버튼 ({pid})")
                    break
                except NoSuchElementException:
                    continue

            if not plus_clicked:
                try:
                    plus_btn = driver.find_element(
                        AppiumBy.XPATH,
                        "//*[contains(@content-desc,'add') or contains(@content-desc,'Add') "
                        "or contains(@content-desc,'카드') or @text='+' or @text='Add Card']"
                    )
                    plus_btn.click()
                    plus_clicked = True
                    print("  [click] c10: + 버튼 (XPath)")
                except NoSuchElementException:
                    print("  [warn] c10: + 버튼 미확인 → 2페이지 캡처만 완료")

            if plus_clicked:
                time.sleep(2.5)
                save_dump(driver, folder, "card3_c10_Add_Card")
                go_back(driver)
                time.sleep(1)
        else:
            print("  [skip] c10: ViewPager 스와이프 3회 시도 실패")

        # Card 탭으로 복귀 (ViewPager 원위치)
        click_tab(driver, "Card")
        time.sleep(1)

    except NoSuchElementException:
        print("  [warn] c10: 'gmeCardViewPager' 없음 → 스킵")
    except Exception as e:
        print(f"  [error] c10: ViewPager - {e}")

    # --- c11~c12: 스크롤 아래 요소 ---
    # is_popup: 팝업/바텀시트 형태 여부
    print("\n  --- c11~c12: 스크롤 아래 요소 ---")
    scroll_elements = [
        ("c11", "performance_card_layout", "EasyGo_Card", False),
        ("c12", "rlGlobalQRScanView", "Global_QR_Scan", True),
    ]

    for code, rid, name, is_popup in scroll_elements:
        if not _go_to_card():
            print(f"  [error] Card 복귀 실패 → 중단")
            return

        full_rid = _id(rid)
        found = False
        before_texts = _get_card_texts()

        # 방법 1: UiScrollable로 자동 스크롤하여 요소 찾기
        try:
            el = driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable(new UiSelector().scrollable(true))'
                f'.scrollIntoView(new UiSelector().resourceId("{full_rid}"))'
            )
            el.click()
            print(f"  [click] {code}: {name} (UiScrollable)")
            found = True
        except Exception as e1:
            print(f"  [info] {code}: UiScrollable 실패 ({e1.__class__.__name__})")

            # 방법 2: 수동 스크롤 + find_element (5회까지)
            if not _go_to_card():
                continue
            before_texts = _get_card_texts()

            for scroll_try in range(5):
                scroll_down(driver)
                time.sleep(1)
                # ID로 먼저 찾기
                try:
                    el = driver.find_element(AppiumBy.ID, full_rid)
                    el.click()
                    print(f"  [click] {code}: {name} (스크롤 {scroll_try + 1}회 후, ID)")
                    found = True
                    break
                except NoSuchElementException:
                    pass
                # DOM에 있는지 체크
                try:
                    src = driver.page_source
                    if rid in src:
                        print(f"  [debug] {code}: 스크롤 {scroll_try + 1}회 후 DOM에 존재")
                except Exception:
                    pass

            # 방법 3: text 기반 검색 (EasyGo, Global QR)
            if not found:
                text_map = {
                    "performance_card_layout": "EasyGo",
                    "rlGlobalQRScanView": "Global QR",
                }
                search_text = text_map.get(rid)
                if search_text:
                    if not _go_to_card():
                        continue
                    before_texts = _get_card_texts()
                    for scroll_try in range(5):
                        scroll_down(driver)
                        time.sleep(1)
                        try:
                            el = driver.find_element(
                                AppiumBy.XPATH,
                                f"//*[contains(@text, '{search_text}')]"
                                f"/ancestor::*[@clickable='true'][1]"
                            )
                            el.click()
                            print(f"  [click] {code}: {name} (text '{search_text}' 기반)")
                            found = True
                            break
                        except NoSuchElementException:
                            pass

        if found:
            time.sleep(2.5)
            changed, _ = _has_screen_changed(before_texts, driver)
            if changed:
                save_dump(driver, folder, f"card3_{code}_{name}", verify=not is_popup)
                if is_popup:
                    print(f"    → 팝업/바텀시트 형태 → 캡처 후 닫기")
                    driver.back()
                    time.sleep(1)
                else:
                    go_back(driver)
                    time.sleep(1)
            else:
                print(f"  [skip] {code}: 화면 변화 없음 → 캡처 생략")
                go_back(driver)
                time.sleep(1)
        else:
            print(f"  [warn] {code}: '{rid}' 스크롤 후에도 없음 → 스킵")

    print("\n===== [CARD 3rd Depth] 탐색 완료 =====")


def explore_event(driver, folder):
    """Event 탭 탐색 (팝업 완전 제거 후 캡처)"""
    print("\n===== [EVENT] 탭 탐색 =====")
    if not click_tab(driver, "Event"):
        print("  [error] Event 탭 클릭 실패")
        return

    time.sleep(1)
    ensure_clean_screen(driver)
    scroll_and_capture(driver, folder, "event_main")

    # 서브 탭 캡처 (각 탭에서도 스크롤 캡처 수행)
    _capture_sub_tabs(driver, folder, "event")


def explore_profile(driver, folder):
    """Profile 탭 탐색 (팝업 완전 제거 후 캡처)"""
    print("\n===== [PROFILE] 탭 탐색 =====")
    if not click_tab(driver, "Profile"):
        print("  [error] Profile 탭 클릭 실패")
        return

    time.sleep(1)
    ensure_clean_screen(driver)
    scroll_and_capture(driver, folder, "profile_main")

    # Profile 내 클릭 가능한 메뉴 항목 탐색
    exclude_kw = ["password", "비밀번호", "logout", "로그아웃", "탈퇴",
                  "delete", "withdraw", "change login", "change simple"]
    _explore_profile_items(driver, folder, exclude_kw)


def _explore_profile_items(driver, folder, exclude_kw):
    """Profile 화면의 메뉴 항목 탐색"""
    # 클릭 가능한 레이아웃들 찾기 (resource-id가 Layout으로 끝나는 것들)
    layout_ids = [
        "fullname", "phoneLayout", "emailLayout", "addressLayout",
        "occupationLayout", "passportLayout", "arcLayout",
        "editProfileView",
    ]

    for lid in layout_ids:
        # 제외 대상 확인
        if any(kw in lid.lower() for kw in exclude_kw):
            print(f"  [skip] '{lid}' - 제외 대상")
            continue

        try:
            el = driver.find_element(AppiumBy.ID, _id(lid))
            if el.get_attribute("clickable") == "true" or el.get_attribute("enabled") == "true":
                el.click()
                print(f"  [click] Profile > {lid}")
                time.sleep(2)
                dismiss_popup(driver)
                save_dump(driver, folder, f"profile_{lid}")
                go_back(driver)
                time.sleep(1)
                click_tab(driver, "Profile", timeout=5)
                time.sleep(1)
        except NoSuchElementException:
            pass
        except Exception as e:
            print(f"  [error] Profile > {lid}: {e}")
            click_tab(driver, "Profile", timeout=5)
            time.sleep(1)


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    folder = os.path.join(PROJECT_ROOT, "ui_dumps", f"explore_{timestamp}")
    os.makedirs(folder, exist_ok=True)
    print(f"[explore] 저장 폴더: {folder}")

    # 팝업 캡처 폴더를 모듈 레벨에 설정 (dismiss_popup에서 자동 사용)
    global _popup_capture_folder
    _popup_capture_folder = folder
    print(f"[explore] 시작 시간: {datetime.now().strftime('%H:%M:%S')}")

    driver = None
    try:
        driver = setup_driver()
        print("[explore] 드라이버 연결 완료")
        time.sleep(3)

        # 앱 실행 상태 확인 및 활성화
        if not ensure_app_running(driver):
            print("[explore] 앱 실행 실패 - 중단")
            return
        print("[explore] 앱 실행 확인 완료")

        # 앱 로딩 대기 (로그인 화면 또는 Home 화면이 나올 때까지)
        # 모든 검사를 implicitly_wait(0) + find_elements로 수행 → 빠른 감지
        print("[explore] 앱 화면 로딩 대기...")
        app_ready = False
        for wait_round in range(20):  # 최대 40초 대기
            time.sleep(2)
            driver.implicitly_wait(0)
            try:
                # 1. Home 탭 확인 (이미 로그인된 상태)
                home_els = driver.find_elements(
                    AppiumBy.XPATH, "//*[@content-desc='Home']"
                )
                if home_els:
                    print("[explore] Home 화면 감지 → 이미 로그인된 상태")
                    app_ready = True
                    break

                # 2. 로그인 화면 확인 (usernameId 또는 btn_lgn)
                login_els = driver.find_elements(AppiumBy.ID, _id("usernameId"))
                login_btn_els = driver.find_elements(AppiumBy.ID, _id("btn_lgn"))
                if login_els or login_btn_els:
                    print("[explore] 로그인 화면 감지")
                    app_ready = True
                    break

                # 3. Simple Password 잠금화면 (resource-id로 감지 - 더 안정적)
                pin_dots = driver.find_elements(AppiumBy.ID, _id("input_dot_1"))
                login_bypass = driver.find_elements(AppiumBy.ID, _id("loginpwidhidpass"))
                if pin_dots or login_bypass:
                    print("[explore] Simple Password 잠금화면 감지 → PIN 직접 입력")
                    if _enter_simple_pin(driver, _SIMPLE_PIN):
                        time.sleep(3)
                        app_ready = True
                        break
                    else:
                        # PIN 입력 실패 → ID/Password 우회
                        print("[explore] PIN 입력 실패 → ID/Password 우회 시도")
                        _handle_simple_password_screen(driver, timeout=5)
                        time.sleep(2)
                        app_ready = True
                        break

                # 4. Connection Failed 등 에러 팝업 (btn_diaog_ok)
                error_ok = driver.find_elements(AppiumBy.ID, _id("btn_diaog_ok"))
                if error_ok:
                    print(f"  [wait] 에러 팝업 감지 → OK 클릭")
                    error_ok[0].click()
                    time.sleep(2)
                    continue

            except WebDriverException as e:
                if "instrumentation" in str(e).lower():
                    print(f"  [wait] UiAutomator2 재시작 중... ({(wait_round + 1) * 2}초)")
                    time.sleep(3)
                    continue
            finally:
                driver.implicitly_wait(2)

            print(f"  [wait] 앱 로딩 중... ({(wait_round + 1) * 2}초)")

        if not app_ready:
            # 초기 설정 화면 처리 (권한 동의, 언어 선택, 약관 등)
            print("[explore] 초기 설정 화면 감지 시도...")
            _handle_permission_guide(driver)
            time.sleep(2)

            # 언어/약관 등 나머지 초기 화면 처리
            handle_initial_screens(driver, resource_id_prefix=RID, max_attempts=8)
            time.sleep(2)

            # 초기 화면 처리 후 다시 Home/Login 확인
            try:
                driver.find_element(AppiumBy.XPATH, "//*[@content-desc='Home']")
                print("[explore] 초기 설정 후 Home 화면 도달")
                app_ready = True
            except (NoSuchElementException, WebDriverException):
                pass

            if not app_ready and check_login_needed(driver):
                print("[explore] 초기 설정 후 로그인 화면 도달")
                app_ready = True

            if not app_ready:
                # 마지막으로 앱 재활성화 시도
                pkg = get_app_package()
                print(f"[explore] 앱 로딩 실패 → 재활성화 시도 ({pkg})")
                try:
                    driver.activate_app(pkg)
                    time.sleep(5)
                except Exception:
                    pass

        # 로그인 필요 여부 확인
        if check_login_needed(driver):
            print(f"[explore] 로그인 필요 - {'Live' if USE_LIVE else 'Staging'} 계정으로 진행")
            # 디버그: 로그인 전 화면 캡처
            save_dump(driver, folder, "debug_before_login", verify=False)
            try:
                # set_english=False: handle_initial_screens()에서 이미 English 설정 완료
                login(driver, username=_LOGIN_USER, pin=_LOGIN_PIN,
                      resource_id_prefix=RID, set_english=False)
                print("[explore] 로그인 완료")
            except Exception as login_err:
                # 로그인 실패 시 디버그 덤프 + logcat 저장
                print(f"[explore] 로그인 실패: {login_err}")
                save_dump(driver, folder, "debug_login_failed", verify=False)
                save_error_logcat(driver, folder, "error_login_failed")
                raise
            time.sleep(3)
            # 로그인 후: Home 탭이 나타날 때까지 대기하면서 팝업 처리
            # dismiss_all_popups의 back 키가 앱을 종료시킬 수 있으므로, 먼저 Home 탭 대기
            print("[explore] 로그인 후 Home 화면 대기...")
            _wait_for_home_after_login(driver, folder, timeout=30)
        else:
            print("[explore] 이미 로그인된 상태 - Home 화면 대기 및 팝업 정리")
            _wait_for_home_after_login(driver, folder, timeout=30)

        # Home 탭 최종 확인
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (AppiumBy.XPATH, "//*[@content-desc='Home']")
                )
            )
            print("[explore] 메인 화면 확인 완료")
        except TimeoutException:
            print("[explore] 메인 화면 미도달 - 중단")
            return

        # 최종 화면 상태 확인
        status = verify_app_screen(driver)
        print(f"[explore] 초기 화면 상태: {status}\n")

        # 탐색 실행 (각 섹션 독립 에러 처리, UiAutomator2 크래시 복구)
        # 실행 옵션: python explore_app.py [섹션명]
        #   전체: python explore_app.py (인자 없음)
        #   특정: python explore_app.py card_3rd
        all_sections = {
            "home": ("Home", explore_home),
            "hamburger": ("Hamburger", explore_hamburger),
            "history": ("History", explore_history),
            "card": ("Card", explore_card),
            "card_3rd": ("Card 3rd Depth", explore_card_3rd_depth),
            "event": ("Event", explore_event),
            "profile": ("Profile", explore_profile),
        }
        # 기본 실행 순서 (전체 탐색 시)
        default_order = ["home", "hamburger", "history", "card", "event", "profile"]

        # 커맨드라인 인자 확인
        target = sys.argv[1].lower() if len(sys.argv) > 1 else None
        if target and target in all_sections:
            sections = [all_sections[target]]
            print(f"[explore] 선택된 섹션: {target}")
        elif target:
            print(f"[explore] 알 수 없는 섹션: '{target}'")
            print(f"[explore] 사용 가능: {', '.join(all_sections.keys())}")
            return
        else:
            sections = [all_sections[k] for k in default_order]
        for name, func in sections:
            try:
                func(driver, folder)
            except Exception as e:
                print(f"\n[explore] {name} 탐색 중 에러: {type(e).__name__}: {e}")
                # 에러 시 logcat 캡처
                try:
                    save_error_logcat(driver, folder, f"error_{name.lower()}")
                except Exception:
                    pass
                # UiAutomator2 크래시 시 드라이버 재생성
                if "instrumentation" in str(e).lower() or "proxy" in str(e).lower():
                    print("[explore] UiAutomator2 크래시 감지 - 드라이버 재생성")
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    time.sleep(3)
                    driver = setup_driver()
                    time.sleep(5)
                    ensure_app_running(driver)
                    dismiss_all_popups(driver, max_rounds=3)
                    click_tab(driver, "Home", timeout=10)
                else:
                    try:
                        # 앱이 실행 중인지 먼저 확인
                        ensure_app_running(driver)
                        driver.back()
                        time.sleep(1)
                        dismiss_all_popups(driver, max_rounds=2)
                        click_tab(driver, "Home", timeout=5)
                    except Exception:
                        pass

        # 결과 요약
        print(f"\n{'='*50}")
        print(f"[explore] 탐색 완료!")
        print(f"[explore] 종료 시간: {datetime.now().strftime('%H:%M:%S')}")
        print(f"[explore] 저장 폴더: {folder}")
        files = sorted(os.listdir(folder))
        print(f"[explore] 총 {len(files)}개 파일 캡처:")
        for f in files:
            size = os.path.getsize(os.path.join(folder, f))
            print(f"  {f} ({size // 1024}KB)")

    except Exception as e:
        print(f"\n[explore] 에러 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
            print("[explore] 드라이버 종료")


if __name__ == "__main__":
    main()
