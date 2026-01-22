"""
UI 요소 덤프 스크립트
현재 화면의 UI 요소를 XML 파일로 저장합니다.

사용법:
    python tools/dump_ui.py [이름]

예시:
    python tools/dump_ui.py login_screen
    python tools/dump_ui.py home
"""

import os
import sys
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options

# 프로젝트 루트 경로
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config.capabilities import ANDROID_CAPS, get_appium_server_url


def dump_ui(name: str = None):
    """
    현재 화면의 UI 요소를 XML 파일로 저장합니다.

    Args:
        name: 저장할 파일의 이름 (선택사항)
    """
    # 출력 폴더 생성
    output_dir = os.path.join(PROJECT_ROOT, "ui_dumps")
    os.makedirs(output_dir, exist_ok=True)

    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 파일명 생성
    if name:
        filename = f"{timestamp}_{name}.xml"
    else:
        filename = f"{timestamp}.xml"

    filepath = os.path.join(output_dir, filename)

    print("=" * 50)
    print("  UI 요소 덤프 스크립트")
    print("=" * 50)
    print()

    # 기존 세션에 연결 시도 (noReset 모드)
    caps = ANDROID_CAPS.copy()
    caps["noReset"] = True
    caps.pop("app", None)  # 앱 재설치 방지

    options = UiAutomator2Options()
    for key, value in caps.items():
        options.set_capability(key, value)

    print(f"[1/3] Appium 서버 연결 중... ({get_appium_server_url()})")

    try:
        driver = webdriver.Remote(
            command_executor=get_appium_server_url(),
            options=options
        )
        print("      연결 성공!")
    except Exception as e:
        print(f"      연결 실패: {e}")
        print()
        print("확인사항:")
        print("  1. Appium 서버가 실행 중인지 확인 (npx appium)")
        print("  2. 에뮬레이터/디바이스가 연결되어 있는지 확인 (adb devices)")
        return None

    try:
        print(f"[2/3] 화면 요소 추출 중...")
        page_source = driver.page_source

        print(f"[3/3] XML 파일 저장 중... ({filepath})")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(page_source)

        print()
        print("=" * 50)
        print(f"  저장 완료: {filepath}")
        print("=" * 50)
        print()

        # 간단한 요소 통계
        import xml.etree.ElementTree as ET
        root = ET.fromstring(page_source)
        element_count = len(list(root.iter()))
        clickable_count = len([e for e in root.iter() if e.get("clickable") == "true"])

        print(f"요소 통계:")
        print(f"  - 전체 요소: {element_count}개")
        print(f"  - 클릭 가능: {clickable_count}개")
        print()

        return filepath

    except Exception as e:
        print(f"오류 발생: {e}")
        return None
    finally:
        driver.quit()


def list_dumps():
    """저장된 UI 덤프 파일 목록을 표시합니다."""
    output_dir = os.path.join(PROJECT_ROOT, "ui_dumps")

    if not os.path.exists(output_dir):
        print("저장된 덤프 파일이 없습니다.")
        return

    files = sorted([f for f in os.listdir(output_dir) if f.endswith(".xml")])

    if not files:
        print("저장된 덤프 파일이 없습니다.")
        return

    print("저장된 UI 덤프 파일:")
    print("-" * 50)
    for f in files:
        filepath = os.path.join(output_dir, f)
        size = os.path.getsize(filepath)
        print(f"  {f} ({size:,} bytes)")
    print("-" * 50)
    print(f"총 {len(files)}개 파일")


def interactive_mode():
    """
    인터랙티브 모드: Enter 키로 캡처, q로 종료
    """
    print("=" * 50)
    print("  UI 요소 덤프 - 인터랙티브 모드")
    print("=" * 50)
    print()
    print("  [Enter]  현재 화면 캡처")
    print("  [q]      종료")
    print()

    # 출력 폴더 생성
    output_dir = os.path.join(PROJECT_ROOT, "ui_dumps")
    os.makedirs(output_dir, exist_ok=True)

    # Appium 연결
    caps = ANDROID_CAPS.copy()
    caps["noReset"] = True
    caps.pop("app", None)

    options = UiAutomator2Options()
    for key, value in caps.items():
        options.set_capability(key, value)

    print(f"Appium 서버 연결 중... ({get_appium_server_url()})")

    try:
        driver = webdriver.Remote(
            command_executor=get_appium_server_url(),
            options=options
        )
        print("연결 성공!")
        print()
    except Exception as e:
        print(f"연결 실패: {e}")
        print()
        print("확인사항:")
        print("  1. Appium 서버가 실행 중인지 확인 (npx appium)")
        print("  2. 에뮬레이터/디바이스가 연결되어 있는지 확인 (adb devices)")
        return

    capture_count = 0
    print("-" * 50)
    print("준비 완료! 원하는 화면에서 Enter를 누르세요.")
    print("-" * 50)

    try:
        while True:
            user_input = input("\n[Enter=캡처, q=종료]: ").strip().lower()

            if user_input == 'q':
                print("\n종료합니다.")
                break

            # 캡처 실행
            capture_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{capture_count:03d}.xml"
            filepath = os.path.join(output_dir, filename)

            try:
                page_source = driver.page_source

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(page_source)

                # 요소 통계
                import xml.etree.ElementTree as ET
                root = ET.fromstring(page_source)
                element_count = len(list(root.iter()))
                clickable_count = len([e for e in root.iter() if e.get("clickable") == "true"])

                print(f"  [{capture_count}] 저장: {filename}")
                print(f"      요소: {element_count}개 / 클릭 가능: {clickable_count}개")

            except Exception as e:
                print(f"  캡처 실패: {e}")

    except KeyboardInterrupt:
        print("\n\n강제 종료됨.")
    finally:
        driver.quit()
        print()
        print("=" * 50)
        print(f"  총 {capture_count}개 화면 캡처 완료")
        print(f"  저장 위치: {output_dir}")
        print("=" * 50)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_dumps()
        elif sys.argv[1] == "-i" or sys.argv[1] == "--interactive":
            interactive_mode()
        elif sys.argv[1] == "--help":
            print("사용법:")
            print("  python tools/dump_ui.py [옵션] [이름]")
            print()
            print("옵션:")
            print("  -i, --interactive  인터랙티브 모드 (Enter로 캡처, q로 종료)")
            print("  --list             저장된 덤프 파일 목록 표시")
            print("  --help             도움말 표시")
            print()
            print("예시:")
            print("  python tools/dump_ui.py                  # 현재 화면 1회 캡처")
            print("  python tools/dump_ui.py login_screen     # 이름 지정하여 캡처")
            print("  python tools/dump_ui.py -i               # 인터랙티브 모드")
        else:
            dump_ui(sys.argv[1])
    else:
        dump_ui()