"""언어 변경 모듈 단독 테스트.

실행 방법:
    pytest tests/test_language_module.py -v -s

또는 직접 실행:
    python tests/test_language_module.py
"""

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.capabilities import ANDROID_CAPS, get_appium_server_url
from utils.language import (
    is_language_selection_screen,
    is_main_screen_with_language_button,
    open_language_list,
    set_language_to_english,
    set_language,
)

# 디버그 파일 저장 경로
DEBUG_DIR = Path(__file__).parent.parent / "debug_output"


class TestLanguageModule:
    """언어 선택 모듈 테스트."""

    @pytest.fixture(autouse=True)
    def setup_driver(self):
        """드라이버 설정."""
        options = UiAutomator2Options()
        options.load_capabilities(ANDROID_CAPS)

        self.driver = webdriver.Remote(
            get_appium_server_url(),
            options=options
        )
        yield
        self.driver.quit()

    def test_language_screen_detection(self):
        """언어 선택 화면 감지 테스트."""
        # 앱 시작 후 언어 선택 화면인지 확인
        result = is_language_selection_screen(self.driver, timeout=10)
        print(f"\n언어 선택 화면 감지: {result}")
        assert result, "언어 선택 화면이 나타나지 않음"

    def test_set_language_to_english(self):
        """English 언어 선택 테스트."""
        # 언어 선택 화면 대기
        assert is_language_selection_screen(self.driver, timeout=10), "언어 선택 화면 없음"

        # English 선택
        result = set_language_to_english(self.driver)
        print(f"\nEnglish 선택 결과: {result}")
        assert result, "English 선택 실패"


def save_debug_files(driver, step_name: str) -> dict:
    """디버그 파일 저장 (스크린샷, page_source XML)."""
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_step_name = step_name.replace(" ", "_").replace("/", "_")

    saved_files = {}

    # 스크린샷 저장
    try:
        screenshot_path = DEBUG_DIR / f"{timestamp}_{safe_step_name}.png"
        driver.save_screenshot(str(screenshot_path))
        saved_files["screenshot"] = screenshot_path
        print(f"    [DEBUG] 스크린샷 저장: {screenshot_path}")
    except Exception as e:
        print(f"    [DEBUG] 스크린샷 저장 실패: {e}")

    # Page Source XML 저장
    try:
        xml_path = DEBUG_DIR / f"{timestamp}_{safe_step_name}.xml"
        page_source = driver.page_source
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(page_source)
        saved_files["xml"] = xml_path
        print(f"    [DEBUG] Page Source 저장: {xml_path}")
    except Exception as e:
        print(f"    [DEBUG] Page Source 저장 실패: {e}")

    return saved_files


def run_standalone_test():
    """pytest 없이 직접 실행하는 테스트 (디버깅 기능 포함)."""
    import time

    print("=" * 60)
    print("언어 변경 모듈 단독 테스트 (디버그 모드)")
    print("=" * 60)
    print(f"디버그 파일 저장 위치: {DEBUG_DIR}")

    # 드라이버 설정
    options = UiAutomator2Options()
    options.load_capabilities(ANDROID_CAPS)

    print(f"\nAppium 서버: {get_appium_server_url()}")
    print("드라이버 연결 중...")

    driver = webdriver.Remote(
        get_appium_server_url(),
        options=options
    )

    try:
        print("앱 시작 완료\n")

        # 앱 시작 후 잠시 대기
        time.sleep(2)

        # 0. 초기 화면 상태 저장
        print("[0] 초기 화면 상태 저장...")
        save_debug_files(driver, "00_initial_screen")

        # 1. 메인 화면에서 언어 선택 버튼 감지
        print("\n[1] 메인 화면 언어 선택 버튼 감지...")
        has_lang_button = is_main_screen_with_language_button(driver, timeout=10)
        print(f"    결과: {'있음' if has_lang_button else '없음'} (언어 선택 버튼)")

        # 감지 후 상태 저장
        save_debug_files(driver, "01_after_detection")

        if not has_lang_button:
            print("\n    [!] 언어 선택 버튼이 있는 메인 화면이 아닙니다.")
            print("    가능한 원인:")
            print("    - 이미 다른 화면으로 이동됨")
            print("    - 앱 로딩 시간이 더 필요함")
            print("\n    저장된 debug_output 폴더의 XML 파일을 확인하세요.")
            return

        # 2. 언어 목록 열기
        print("\n[2] 언어 목록 열기...")
        save_debug_files(driver, "02_before_open_list")

        opened = open_language_list(driver)
        print(f"    결과: {'성공' if opened else '실패'}")

        if opened:
            save_debug_files(driver, "03_language_list_opened")
        else:
            print("    [!] 언어 목록 열기 실패")
            save_debug_files(driver, "03_open_list_failed")
            return

        # 3. English 선택
        print("\n[3] English 선택 테스트...")
        result = set_language_to_english(driver)
        print(f"    결과: {'성공' if result else '실패'}")

        # English 선택 후 상태 저장
        time.sleep(1)
        save_debug_files(driver, "04_after_english_select")

        if result:
            print("\n[OK] 테스트 완료: 언어가 English로 변경되었습니다.")
        else:
            print("\n[FAIL] 테스트 실패: English 선택에 실패했습니다.")
            print("    저장된 debug_output 폴더의 XML 파일을 확인하세요.")

        # 4. 화면 전환 확인 (메인 화면으로 복귀)
        time.sleep(2)
        print("\n[4] 화면 전환 확인...")
        save_debug_files(driver, "05_final_screen")

        # 메인 화면으로 돌아왔는지 확인
        back_to_main = is_main_screen_with_language_button(driver, timeout=3)
        if back_to_main:
            print("    [OK] 메인 화면으로 복귀됨")
        else:
            print("    [!] 메인 화면으로 복귀되지 않음 - 다른 화면일 수 있음")

    except Exception as e:
        print(f"\n[ERROR] 예외 발생: {e}")
        try:
            save_debug_files(driver, "99_error_state")
        except:
            pass
        raise

    finally:
        print("\n드라이버 종료 중...")
        driver.quit()
        print("완료")
        print(f"\n디버그 파일 확인: {DEBUG_DIR}")


if __name__ == "__main__":
    run_standalone_test()
