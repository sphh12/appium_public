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
from utils.auth import login
from utils.initial_screens import handle_initial_screens

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

# 캡처 파일 번호 카운터
_file_counter = 0

# 팝업 캡처 저장 폴더 (main에서 설정, dismiss_popup에서 자동 사용)
_popup_capture_folder = None


def _id(suffix):
    """리소스 ID 전체 경로 생성"""
    return f"{RID}/{suffix}"


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

    # 타임아웃 → 디버그 덤프
    print("  [post-login] Home 탭 미도달 (타임아웃)")
    if folder:
        save_dump(driver, folder, "debug_post_login_timeout", verify=False)
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


# =========================================================================
# 각 탭 탐색 함수
# =========================================================================

def explore_home(driver, folder):
    """Home 탭 탐색"""
    print("\n===== [HOME] 탭 탐색 =====")
    click_tab(driver, "Home")
    ensure_clean_screen(driver)
    save_dump(driver, folder, "home_main")

    # 스크롤해서 하단 영역도 캡처
    scroll_down(driver)
    save_dump(driver, folder, "home_scrolled")
    scroll_up(driver)

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
        save_dump(driver, folder, "hamburger_menu", verify=False)

        # 드로어 스크롤해서 더 보기
        scroll_down(driver)
        save_dump(driver, folder, "hamburger_menu_scrolled", verify=False)
        scroll_up(driver)

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

                save_dump(driver, folder, f"menu_{name}")

                # 서브 탭이 있으면 캡처
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
    """현재 화면의 서브 탭을 캡처"""
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
                        save_dump(driver, folder, f"{prefix}_{safe}")
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
                        save_dump(driver, folder, f"{prefix}_{safe}")
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
    save_dump(driver, folder, "card_main")

    # 스크롤해서 하단도 캡처
    scroll_down(driver)
    save_dump(driver, folder, "card_scrolled")
    scroll_up(driver)

    # 서브 탭 캡처
    _capture_sub_tabs(driver, folder, "card")


def explore_event(driver, folder):
    """Event 탭 탐색 (팝업 완전 제거 후 캡처)"""
    print("\n===== [EVENT] 탭 탐색 =====")
    if not click_tab(driver, "Event"):
        print("  [error] Event 탭 클릭 실패")
        return

    time.sleep(1)
    ensure_clean_screen(driver)
    save_dump(driver, folder, "event_main")

    # 스크롤해서 하단도 캡처
    scroll_down(driver)
    save_dump(driver, folder, "event_scrolled")
    scroll_up(driver)

    # 서브 탭 캡처
    _capture_sub_tabs(driver, folder, "event")


def explore_profile(driver, folder):
    """Profile 탭 탐색 (팝업 완전 제거 후 캡처)"""
    print("\n===== [PROFILE] 탭 탐색 =====")
    if not click_tab(driver, "Profile"):
        print("  [error] Profile 탭 클릭 실패")
        return

    time.sleep(1)
    ensure_clean_screen(driver)
    save_dump(driver, folder, "profile_main")

    # 스크롤 캡처
    scroll_down(driver)
    save_dump(driver, folder, "profile_scrolled")
    scroll_up(driver)

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
        print("[explore] 앱 화면 로딩 대기...")
        app_ready = False
        for wait_round in range(15):  # 최대 30초 대기
            time.sleep(2)
            try:
                # Home 탭 확인 (이미 로그인된 상태)
                driver.find_element(
                    AppiumBy.XPATH, "//*[@content-desc='Home']"
                )
                print("[explore] Home 화면 감지 → 이미 로그인된 상태")
                app_ready = True
                break
            except NoSuchElementException:
                pass
            except WebDriverException as e:
                if "instrumentation" in str(e).lower():
                    print(f"  [wait] UiAutomator2 재시작 중... ({(wait_round + 1) * 2}초)")
                    time.sleep(3)
                    continue
                pass

            # 로그인 화면 확인
            try:
                if check_login_needed(driver):
                    print("[explore] 로그인 화면 감지")
                    app_ready = True
                    break
            except WebDriverException:
                pass

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
                # 로그인 실패 시 디버그 덤프 저장
                print(f"[explore] 로그인 실패: {login_err}")
                save_dump(driver, folder, "debug_login_failed", verify=False)
                raise
            time.sleep(3)
            # 로그인 후: Home 탭이 나타날 때까지 대기하면서 팝업 처리
            # dismiss_all_popups의 back 키가 앱을 종료시킬 수 있으므로, 먼저 Home 탭 대기
            print("[explore] 로그인 후 Home 화면 대기...")
            _wait_for_home_after_login(driver, folder, timeout=30)
        else:
            print("[explore] 이미 로그인된 상태 - 팝업 정리")
            dismiss_all_popups(driver, max_rounds=3)

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
        sections = [
            ("Home", explore_home),
            ("Hamburger", explore_hamburger),
            ("History", explore_history),
            ("Card", explore_card),
            ("Event", explore_event),
            ("Profile", explore_profile),
        ]
        for name, func in sections:
            try:
                func(driver, folder)
            except Exception as e:
                print(f"\n[explore] {name} 탐색 중 에러: {type(e).__name__}: {e}")
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
