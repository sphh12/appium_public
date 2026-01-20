"""
Appium Desired Capabilities 설정
Android 및 iOS 디바이스/에뮬레이터 설정
"""
import os

# 프로젝트 루트 경로 자동 계산
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Android 에뮬레이터 설정
ANDROID_CAPS = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": "Android Emulator",  # 또는 실제 디바이스 이름
    "platformVersion": "14",  # Android 버전
    "app": os.path.join(PROJECT_ROOT, "apk", "[Stg]GME_7.13.0.apk"),  # APK 파일 경로
    # "appPackage": "com.example.app",  # 앱 패키지명
    # "appActivity": ".MainActivity",  # 시작 액티비티
    "noReset": False,
    "fullReset": False,
    "newCommandTimeout": 300,
    "autoGrantPermissions": True,
}

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
