"""
Appium Desired Capabilities 설정
Android 및 iOS 디바이스/에뮬레이터 설정

환경변수 설정:
  - GME_APK_FILENAME: APK 파일명 (기본: app.apk)
  - APPIUM_HOST: Appium 서버 호스트 (기본: 127.0.0.1)
  - APPIUM_PORT: Appium 서버 포트 (기본: 4723)
  - ANDROID_UDID: 실물 디바이스 시리얼 (선택)
  - ANDROID_DEVICE_NAME: 디바이스 이름 (선택)
  - ANDROID_PLATFORM_VERSION: OS 버전 (선택)

.env 파일 또는 환경변수로 설정하세요.
"""
import os
from dotenv import load_dotenv

# 환경변수 로드 (.env 파일)
load_dotenv()

# 프로젝트 루트 경로 자동 계산
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Android 환경변수
# - ANDROID_UDID: 실물 디바이스 시리얼 (adb devices로 확인)
# - ANDROID_DEVICE_NAME: 디바이스 이름 (Allure 리포트 표시용)
# - ANDROID_PLATFORM_VERSION: OS 버전 (선택)
ANDROID_UDID = os.getenv("ANDROID_UDID")
ANDROID_DEVICE_NAME = os.getenv("ANDROID_DEVICE_NAME", "Android Emulator")
ANDROID_PLATFORM_VERSION = os.getenv("ANDROID_PLATFORM_VERSION")

# APK 파일명 (환경변수로 설정)
APK_FILENAME = os.getenv("GME_APK_FILENAME", "app.apk")

# Android 설정
ANDROID_CAPS = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": ANDROID_DEVICE_NAME,
    "app": os.path.join(PROJECT_ROOT, "apk", APK_FILENAME),
    # "appPackage": "com.example.app",  # 앱 패키지명
    # "appActivity": ".MainActivity",  # 시작 액티비티
    "noReset": False,
    "fullReset": False,
    "newCommandTimeout": 300,
    "autoGrantPermissions": True,
    "adbExecTimeout": 60000,  # ADB 명령 타임아웃 60초 (기본 20초)
}

# 실물 디바이스 연결 시 udid 추가
if ANDROID_UDID:
    ANDROID_CAPS["udid"] = ANDROID_UDID

if ANDROID_PLATFORM_VERSION:
    ANDROID_CAPS["platformVersion"] = ANDROID_PLATFORM_VERSION

# iOS 시뮬레이터 설정 (Mac에서만 동작)
IOS_CAPS = {
    "platformName": "iOS",
    "automationName": "XCUITest",
    "deviceName": "iPhone 15",  # 시뮬레이터 이름
    "platformVersion": "17.0",  # iOS 버전
    "app": "",  # .app 또는 .ipa 파일 경로
    # "bundleId": "com.example.app",  # 앱 번들 ID
    "noReset": False,
    "fullReset": False,
    "newCommandTimeout": 300,
}

# Appium 서버 설정 (환경변수로 설정 가능)
APPIUM_HOST = os.getenv("APPIUM_HOST", "127.0.0.1")
APPIUM_PORT = int(os.getenv("APPIUM_PORT", "4723"))

APPIUM_SERVER = {
    "host": APPIUM_HOST,
    "port": APPIUM_PORT,
}

def get_appium_server_url():
    return f"http://{APPIUM_SERVER['host']}:{APPIUM_SERVER['port']}"
