"""Shift 후 키보드 상태 진단 스크립트.

비밀번호 필드 클릭 → 키보드 UI 덤프 → Shift 클릭 → 키보드 UI 덤프(Shift 후)
→ 특수문자 전환 → 키보드 UI 덤프(특수문자)
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
from lxml import etree

from utils.language import ensure_english_language

load_dotenv()

PACKAGE = "com.gmeremit.online.gmeremittance_native"
ACTIVITY = ".splash_screen.view.SplashScreen"
RID = f"{PACKAGE}:id"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui_dumps", "debug_keyboard")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_ui_dump(driver, filename):
    """UI 소스를 파일로 저장하고 keypadContainer 내 키 정보를 출력."""
    xml = driver.page_source
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"\n[DUMP] {filepath} 저장 완료")

    # keypadContainer 내 모든 클릭 가능한 요소의 content-desc 출력
    root = etree.fromstring(xml.encode("utf-8"))
    keypad_elems = root.xpath(
        f'//*[@resource-id="{RID}/keypadContainer"]//android.widget.ImageView[@clickable="true"]'
    )
    print(f"[INFO] keypadContainer 내 클릭 가능한 ImageView: {len(keypad_elems)}개")
    for elem in keypad_elems:
        desc = elem.get("content-desc", "(없음)")
        bounds = elem.get("bounds", "")
        print(f"  - content-desc: '{desc}'  bounds: {bounds}")

    # ImageView 외 다른 클릭 가능한 요소도 확인
    other_elems = root.xpath(
        f'//*[@resource-id="{RID}/keypadContainer"]//*[@clickable="true"]'
    )
    non_imageview = [e for e in other_elems if e.tag != "android.widget.ImageView"]
    if non_imageview:
        print(f"\n[INFO] 기타 클릭 가능 요소: {len(non_imageview)}개")
        for elem in non_imageview:
            desc = elem.get("content-desc", "(없음)")
            text = elem.get("text", "(없음)")
            cls = elem.tag
            print(f"  - {cls} content-desc: '{desc}' text: '{text}'")


def main():
    # 앱 초기화
    subprocess.run(["adb", "shell", "am", "force-stop", PACKAGE], capture_output=True)
    time.sleep(1)

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "emulator-5554"
    options.app_package = PACKAGE
    options.app_activity = ACTIVITY
    options.no_reset = True
    options.auto_grant_permissions = True
    options.new_command_timeout = 300
    options.force_app_launch = True
    options.app_wait_activity = "*"

    print("[1] Appium 드라이버 연결 중...")
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    print(f"[1] 드라이버 연결 완료")

    try:
        time.sleep(5)

        # 언어 설정
        ensure_english_language(driver, resource_id_prefix=RID, timeout=15)

        # 로그인 화면으로 이동
        try:
            login_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((AppiumBy.ID, f"{RID}/btn_lgn"))
            )
            login_btn.click()
            time.sleep(2)
        except TimeoutException:
            print("[!] btn_lgn 미발견")

        # 아이디 입력
        username = os.getenv("LIVE_ID", "")
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, f"{RID}/usernameId"))
        )
        username_field.clear()
        username_field.send_keys(username)
        print(f"[2] 아이디 입력: {username[:3]}***")

        # 비밀번호 필드 클릭 → 보안 키보드 열기
        pw_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((AppiumBy.ID, f"{RID}/securityKeyboardEditText"))
        )
        pw_field.click()
        time.sleep(1.5)

        # Step 1: 기본 상태 (소문자) 키보드 덤프
        print("\n=== [1/3] 기본 키보드 상태 (소문자) ===")
        save_ui_dump(driver, "01_keyboard_lowercase.xml")

        # Step 2: Shift 클릭
        print("\n=== [2/3] Shift 클릭 후 키보드 상태 (대문자) ===")
        keypad_id = f"{RID}/keypadContainer"
        try:
            shift_xpath = (
                f'//android.widget.FrameLayout[@resource-id="{keypad_id}"]'
                f'//android.widget.ImageView[@content-desc="대문자 키보드 변경"]'
            )
            shift_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, shift_xpath))
            )
            shift_btn.click()
            print("[OK] Shift 클릭 성공")
            time.sleep(0.5)
        except (NoSuchElementException, TimeoutException):
            print("[!] Shift 버튼 못 찾음 → 모든 content-desc 확인")

        save_ui_dump(driver, "02_keyboard_uppercase.xml")

        # Step 3: 특수문자 전환
        print("\n=== [3/3] 특수문자 모드 키보드 상태 ===")
        try:
            # Shift 상태에서 특수문자 버튼 찾기
            for desc in ["특수문자변경", "특수문자 변경", "특수문자"]:
                try:
                    sp_xpath = (
                        f'//android.widget.FrameLayout[@resource-id="{keypad_id}"]'
                        f'//android.widget.ImageView[@content-desc="{desc}"]'
                    )
                    sp_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, sp_xpath))
                    )
                    sp_btn.click()
                    print(f"[OK] '{desc}' 클릭 성공")
                    break
                except (NoSuchElementException, TimeoutException):
                    continue
            time.sleep(0.5)
        except Exception as e:
            print(f"[!] 특수문자 전환 실패: {e}")

        save_ui_dump(driver, "03_keyboard_special.xml")

        print("\n[완료] 디버깅 완료! ui_dumps/debug_keyboard/ 폴더를 확인하세요.")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise
    finally:
        driver.quit()
        print("[완료] 드라이버 종료")


if __name__ == "__main__":
    main()
