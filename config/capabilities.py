"""
Appium Desired Capabilities 설정
Android 및 iOS 디바이스/에뮬레이터 설정

환경변수로 디바이스 선택:
  - 에뮬레이터 (기본): 환경변수 없이 실행
  - 실물 디바이스: ANDROID_UDID 설정
    예) PowerShell: $env:ANDROID_UDID = "XXXXXXXX"
        삭제: Remove-Item Env:ANDROID_UDID
"""
import os

# 프로젝트 루트 경로 자동 계산
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Android 환경변수
# - ANDROID_UDID: 실물 디바이스 시리얼 (adb devices로 확인)
# - ANDROID_DEVICE_NAME: 디바이스 이름 (Allure 리포트 표시용)
# - ANDROID_PLATFORM_VERSION: OS 버전 (선택)
ANDROID_UDID = os.getenv("ANDROID_UDID")
ANDROID_DEVICE_NAME = os.getenv("ANDROID_DEVICE_NAME", "Android Emulator")
ANDROID_PLATFORM_VERSION = os.getenv("ANDROID_PLATFORM_VERSION")

# Android 설정
ANDROID_CAPS = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": ANDROID_DEVICE_NAME,
    "app": os.path.join(PROJECT_ROOT, "apk", "[Stg]GME_7.13.0.apk"),
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

# Appium 서버 설정
APPIUM_SERVER = {
    "host": "127.0.0.1",
    "port": 4723,
}

def get_appium_server_url():
    return f"http://{APPIUM_SERVER['host']}:{APPIUM_SERVER['port']}"
