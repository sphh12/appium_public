"""Live 앱 로그인 테스트 - 전체 로그인 + 간편비밀번호 설정 플로우

테스트 흐름:
1. 앱 상태 초기화 (force-stop)
2. 앱 실행
3. 언어 변경 (English)
4. 로그인 화면 진입 (btn_lgn)
5. 아이디 입력 (usernameId)
6. 비밀번호 입력 (커스텀 보안 키보드 - QWERTY)
7. 로그인 (btn_submit)
8. 간편비밀번호 설정 (4자리 2회 입력)
9. 성공 팝업 확인 (btnOk)
10. 홈 화면 도달 확인 (drawer_home)
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv

from utils.auth import login

load_dotenv()

# Live 앱 설정
PACKAGE = "com.gmeremit.online.gmeremittance_native"
ACTIVITY = ".splash_screen.view.SplashScreen"
RID = f"{PACKAGE}:id"

# 환경변수에서 계정 정보
USERNAME = os.getenv("LIVE_ID", "")
PIN = os.getenv("LIVE_PW", "")
SIMPLE_PIN = os.getenv("SIMPLE_PIN", "1234")

if not USERNAME or not PIN:
    print("[ERROR] LIVE_ID / LIVE_PW 환경변수를 설정하세요.")
    sys.exit(1)


def _reset_app():
    """테스트 시작 전 앱 상태 초기화 (force-stop).

    pm clear는 사용하지 않음 → 시스템 권한 다이얼로그 회피.
    이전 로그인 상태/간편비밀번호는 navigate_to_login_screen에서 처리.
    """
    print("[0] 앱 상태 초기화 중...")
    subprocess.run(
        ["adb", "shell", "am", "force-stop", PACKAGE],
        capture_output=True,
    )
    time.sleep(1)
    print("[0] 앱 초기화 완료")


def _verify_home_screen(driver, timeout=10):
    """로그인 후 홈 화면에 도달했는지 확인합니다.

    홈 화면 특징 (UI 덤프 016_HomeV2.xml / 021_GME_Wallet_Number.xml):
    - drawer_home (DrawerLayout)
    - scrollViewHomeFragment
    - bottomBar (하단 네비게이션: Home, History, Card, Send, More)
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, f"{RID}/drawer_home")
            )
        )
        print("[검증] 홈 화면 도달 확인 (drawer_home)")
        return True
    except (NoSuchElementException, TimeoutException):
        pass

    # 폴백: bottomBar 확인
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, f"{RID}/bottomBar")
            )
        )
        print("[검증] 홈 화면 도달 확인 (bottomBar)")
        return True
    except (NoSuchElementException, TimeoutException):
        print("[검증] 홈 화면 감지 실패")
        return False


def main():
    # 테스트 전 앱 상태 초기화
    _reset_app()

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "emulator-5554"
    options.app_package = PACKAGE
    options.app_activity = ACTIVITY
    options.no_reset = True
    options.auto_grant_permissions = True
    options.new_command_timeout = 300
    # force-stop 후에도 앱이 확실히 재실행되도록 설정
    options.force_app_launch = True
    options.app_wait_activity = "*"

    print("[1] Appium 드라이버 연결 중...")
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    print(f"[1] 드라이버 연결 완료 - session: {driver.session_id}")

    try:
        # 앱이 포그라운드에 있는지 확인
        time.sleep(3)
        current = driver.current_package
        if current != PACKAGE:
            print(f"[1] 앱이 포그라운드에 없음 ({current}) → activate_app 실행")
            driver.activate_app(PACKAGE)
            time.sleep(5)
        else:
            print(f"[1] 앱 포그라운드 확인: {current}")

        # 스플래시 화면이 지나갈 때까지 대기
        time.sleep(3)

        # 로그인 전체 흐름 실행
        # auth.py의 login()이 아래를 모두 처리:
        #   1. 언어 선택 (English)
        #   2. 로그인 화면 진입 (btn_lgn)
        #   3. ID/PW 입력 (커스텀 보안 키보드)
        #   4. 로그인 실행 + 에러 확인
        #   5. 후속 팝업 처리 (지문인증, 보이스피싱)
        #   6. 간편비밀번호 설정 (simple_pin 지정 시)
        print(f"[2] 로그인 시작 - ID: {USERNAME[:3]}***")
        login(
            driver,
            username=USERNAME,
            pin=PIN,
            resource_id_prefix=RID,
            set_english=True,
            timeout=20,
            simple_pin=SIMPLE_PIN,
        )
        print("[2] 로그인 + 간편비밀번호 설정 완료!")

        # 홈 화면 도달 확인
        time.sleep(3)
        if _verify_home_screen(driver):
            activity = driver.current_activity
            print(f"\n[결과] 테스트 성공! (Activity: {activity})")
        else:
            activity = driver.current_activity
            print(f"\n[결과] 홈 화면 미확인 (Activity: {activity})")

    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
        # 실패 시 스크린샷 저장
        try:
            screenshot_path = "/Users/sph/appium/ui_dumps/login_fail_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"[DEBUG] 스크린샷 저장: {screenshot_path}")
        except Exception:
            pass
        raise
    finally:
        driver.quit()
        print("[완료] 드라이버 종료")


if __name__ == "__main__":
    main()
