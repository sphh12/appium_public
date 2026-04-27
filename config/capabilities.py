"""
Appium Desired Capabilities 설정
Android 및 iOS 디바이스/에뮬레이터 설정

환경변수 설정:
  - APP_ENV: APK 환경 선택 (stage/live/livetest, 기본: stage)
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

# APK 폴더 기반 자동 탐색
# apk/stage/, apk/live/, apk/livetest/ 폴더 내 .apk 파일을 자동으로 찾음
# --app 옵션으로 런타임에 변경 가능
def _find_apk_in_folder(env_type="stage"):
    """환경별 폴더에서 .apk 파일을 자동 탐색"""
    apk_dir = os.path.join(PROJECT_ROOT, "apk", env_type)
    if os.path.isdir(apk_dir):
        apk_files = [f for f in os.listdir(apk_dir) if f.endswith(".apk")]
        if apk_files:
            # 파일이 여러 개면 최신(이름순 마지막) 파일 사용
            return os.path.join(apk_dir, sorted(apk_files)[-1])
    return ""

ENV_TYPE = os.getenv("APP_ENV", "stage")
APK_PATH = _find_apk_in_folder(ENV_TYPE)

# ── 환경별 설정 (APP_ENV에 따라 자동 전환) ──
# resource-id 접두사: staging 앱은 '.stag:id', live/livetest 앱은 ':id'
_ENV_CONFIG = {
    "stage": {
        "resource_id_prefix": os.getenv(
            "STG_RESOURCE_ID_PREFIX",
            "com.gmeremit.online.gmeremittance_native.stag:id",
        ),
        "username": os.getenv("STG_ID", ""),
        "password": os.getenv("STG_PW", ""),
    },
    "live": {
        "resource_id_prefix": os.getenv(
            "LIVE_RESOURCE_ID_PREFIX",
            "com.gmeremit.online.gmeremittance_native:id",
        ),
        "username": os.getenv("LIVE_ID", ""),
        "password": os.getenv("LIVE_PW", ""),
    },
    "livetest": {
        "resource_id_prefix": os.getenv(
            "LIVETEST_RESOURCE_ID_PREFIX",
            "com.gmeremit.online.gmeremittance_native.livetest:id",
        ),
        "username": os.getenv("LIVE_ID", ""),  # livetest는 live 계정 사용
        "password": os.getenv("LIVE_PW", ""),
    },
}

def get_env_config(env_type=None):
    """현재 APP_ENV에 맞는 설정을 반환합니다.

    Returns:
        dict with keys: resource_id_prefix, username, password
    """
    env = env_type or ENV_TYPE
    return _ENV_CONFIG.get(env, _ENV_CONFIG["stage"])

# Android 설정
ANDROID_CAPS = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": ANDROID_DEVICE_NAME,
    "app": APK_PATH,
    # "appPackage": "com.example.app",  # 앱 패키지명
    # "appActivity": ".MainActivity",  # 시작 액티비티
    "noReset": False,
    "fullReset": False,
    "newCommandTimeout": 300,
    "autoGrantPermissions": True,
    "adbExecTimeout": 60000,  # ADB 명령 타임아웃 60초 (기본 20초)
    "appWaitDuration": 60000,  # 앱 시작 대기 60초 (기본 20초, 에뮬레이터 느린 경우 대비)
    "uiautomator2ServerLaunchTimeout": 60000,  # UiAutomator2 서버 시작 대기 60초
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
    "deviceName": os.getenv("IOS_DEVICE_NAME", "iPhone 17"),  # 시뮬레이터 이름
    "platformVersion": os.getenv("IOS_PLATFORM_VERSION", "26.4"),  # iOS 버전
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
