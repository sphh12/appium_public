"""Authentication and session helpers.

This module centralizes repeatable flows like navigating to the login screen and
performing login so that new tests can start from a logged-in state.

환경변수 설정:
  - STG_ID / STG_PW: Staging 테스트 계정 (기본)
  - LIVE_ID / LIVE_PW: Live 테스트 계정
  - SIMPLE_PIN: 간편비밀번호 4자리 (기본값: "1234")
  - GME_RESOURCE_ID_PREFIX: 앱의 resource-id 접두사

.env 파일 또는 환경변수로 설정하세요.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager

from appium.webdriver.common.appiumby import AppiumBy  # type: ignore
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv

from utils.language import ensure_english_language

# 환경변수 로드 (.env 파일)
load_dotenv()

try:
    import allure  # type: ignore
except Exception:  # pragma: no cover
    allure = None


# 환경변수에서 설정 로드
DEFAULT_RESOURCE_ID_PREFIX = os.getenv(
    "GME_RESOURCE_ID_PREFIX",
    "com.gmeremit.online.gmeremittance_native.stag:id",
)

# 민감정보는 반드시 환경변수로 설정 (기본값 없음)
# STG (Staging) 계정이 기본값, LIVE 계정은 별도 함수로 사용
DEFAULT_USERNAME = os.getenv("STG_ID", "")
DEFAULT_PIN = os.getenv("STG_PW", "")

# Live 계정 정보
LIVE_USERNAME = os.getenv("LIVE_ID", "")
LIVE_PIN = os.getenv("LIVE_PW", "")

# 간편비밀번호 (Simple Password) - 4자리 숫자
DEFAULT_SIMPLE_PIN = os.getenv("SIMPLE_PIN", "1212")


def _id(resource_id_prefix: str, suffix: str) -> str:
    return f"{resource_id_prefix}/{suffix}"


@contextmanager
def _step(name: str):
    if allure is None:
        yield
        return

    with allure.step(name):
        yield


def _is_staging_app(resource_id_prefix: str) -> bool:
    """resource-id 접두사로 Staging 앱 여부를 판단합니다.

    - Staging: 'com.gmeremit.online.gmeremittance_native.stag:id' → 숫자 전용 보안 키보드
    - Live: 'com.gmeremit.online.gmeremittance_native:id' → QWERTY 보안 키보드
    """
    return "stag" in resource_id_prefix


# ---------------------------------------------------------------------------
# 화면 판별 함수
# ---------------------------------------------------------------------------

def is_login_screen(driver, resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX) -> bool:
    """Login screen is defined as the one containing the username input."""
    try:
        driver.find_element(by=AppiumBy.ID, value=_id(resource_id_prefix, "usernameId"))
        return True
    except NoSuchElementException:
        return False


# ---------------------------------------------------------------------------
# 커스텀 보안 키보드 - Live 앱 (QWERTY + 숫자 + 특수문자)
# ---------------------------------------------------------------------------

def _type_on_live_security_keyboard(
    driver,
    text: str,
    resource_id_prefix: str,
    timeout: float = 10,
) -> None:
    """Live 앱의 커스텀 보안 키보드(transKeypad)로 텍스트를 입력합니다.

    키보드 구조 (keypadContainer → transKeypad_main):
    - Row1: 숫자 0-9 (content-desc: "0"~"9")
    - Row2: qwertyuiop (content-desc: "q 비읍", "w 지읃", ...)
    - Row3: asdfghjkl (content-desc: "a 미음", "s 니은", ...)
    - Row4: Shift + zxcvbnm + Delete
    - Row5: 재배열 | 특수문자변경 | 공백 | 입력취소 | 입력완료

    동작 방식:
    - 숫자: content-desc = "숫자" (exact match)
    - 소문자: content-desc starts-with "letter " (e.g., "s 니은")
    - 대문자: Shift 클릭 후 content-desc starts-with "LETTER " (e.g., "S ")
    - 특수문자: 특수문자변경 클릭 후 content-desc로 찾기
    """
    keypad_id = _id(resource_id_prefix, "keypadContainer")

    # 키보드가 나타날 때까지 대기
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((AppiumBy.ID, keypad_id))
    )
    print(f"  [auth] Live 커스텀 보안 키보드 감지 (입력 길이: {len(text)})")

    is_shift_active = False
    is_special_mode = False

    for i, char in enumerate(text):
        need_uppercase = char.isupper()
        need_special = not char.isalnum() and char != " "

        # --- 모드 전환: 특수문자 ↔ 영문/숫자 ---
        if need_special and not is_special_mode:
            print(f"  [auth]   특수문자 모드 전환 (입력할 문자: '{char}')")
            _click_keypad_button_by_desc(
                driver, keypad_id, "특수문자변경", timeout,
                fallback_descs=["특수문자 변경", "특수문자"],
            )
            is_special_mode = True
            is_shift_active = False
            time.sleep(0.5)
        elif not need_special and is_special_mode:
            # 특수문자 모드에서 영문 모드로 복귀
            print(f"  [auth]   영문/숫자 모드 복귀 (입력할 문자: '{char}')")
            _click_keypad_button_by_desc(
                driver, keypad_id, "영문자변경", timeout,
                fallback_descs=["영문변경", "abc", "ABC"],
            )
            is_special_mode = False
            is_shift_active = False
            time.sleep(0.5)

        # --- 모드 전환: 대소문자 ---
        if char.isalpha() and not is_special_mode:
            if need_uppercase and not is_shift_active:
                print(f"  [auth]   Shift 활성화 (대문자 입력 '{char}')")
                _click_keypad_button_by_desc(
                    driver, keypad_id, "대문자 키보드 변경", timeout,
                    fallback_descs=["대문자 키보드 고정 변경"],
                )
                is_shift_active = True
                time.sleep(0.3)
            elif not need_uppercase and is_shift_active:
                # Shift가 1회용이면 자동 해제되므로 수동 해제 불필요할 수 있음
                # 하지만 확실하게 처리
                print(f"  [auth]   Shift 비활성화 시도 (소문자 입력 '{char}')")
                try:
                    _click_keypad_button_by_desc(
                        driver, keypad_id, "대문자 키보드 고정 변경", min(timeout, 2),
                        fallback_descs=["대문자 키보드 변경"],
                    )
                except (NoSuchElementException, TimeoutException):
                    # Shift가 자동 해제된 경우 (1회용 Shift)
                    print("  [auth]   Shift 이미 자동 해제됨")
                is_shift_active = False
                time.sleep(0.2)

        # --- 실제 키 클릭 ---
        if char == " ":
            _click_keypad_button_by_desc(driver, keypad_id, "공백", timeout)
        elif char.isdigit():
            # 숫자: content-desc가 정확히 해당 숫자
            _click_keypad_digit(driver, keypad_id, char, timeout)
        elif char.isalpha():
            # 영문자: 소문자 "s 니은" / 대문자 "Capital S 니은" 형식
            _click_keypad_letter(driver, keypad_id, char, timeout, is_shifted=is_shift_active)
            # Shift는 1회용 (한 글자 입력 후 자동 해제)
            if is_shift_active:
                is_shift_active = False
        else:
            # 특수문자: 한국어 설명으로 매핑하여 클릭
            desc = SPECIAL_CHAR_DESC_MAP.get(char, char)
            _click_keypad_button_by_desc(driver, keypad_id, desc, timeout)

        time.sleep(0.2)
        print(f"  [auth]   키 입력 [{i+1}/{len(text)}]: {'*'}")

    # 입력완료 클릭
    time.sleep(0.3)
    _click_keypad_button_by_desc(driver, keypad_id, "입력완료", timeout)
    print("  [auth] 입력완료 클릭")


def _click_keypad_digit(
    driver, keypad_id: str, digit: str, timeout: float = 5,
) -> None:
    """키패드에서 숫자 키를 클릭합니다. content-desc가 정확히 해당 숫자인 키."""
    xpath = (
        f'//android.widget.FrameLayout[@resource-id="{keypad_id}"]'
        f'//android.widget.ImageView[@content-desc="{digit}" and @clickable="true"]'
    )
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
    ).click()


def _click_keypad_letter(
    driver, keypad_id: str, char: str, timeout: float = 5,
    is_shifted: bool = False,
) -> None:
    """키패드에서 영문자 키를 클릭합니다.

    content-desc 형식:
    - 소문자: "s 니은", "q 비읍" 등 (소문자 + 한글)
    - 대문자 (Shift 후): "Capital S 니은", "Capital Q 쌍비읍" 등
    """
    base = f'//android.widget.FrameLayout[@resource-id="{keypad_id}"]//android.widget.ImageView'

    if is_shifted or char.isupper():
        # Shift 모드: "Capital X " 형식으로 찾기
        upper_char = char.upper()
        xpath = f'{base}[starts-with(@content-desc, "Capital {upper_char} ") and @clickable="true"]'
        try:
            WebDriverWait(driver, min(timeout, 3)).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
            ).click()
            return
        except (NoSuchElementException, TimeoutException):
            pass

        # Fallback: 소문자 형식으로도 시도
        lower_char = char.lower()
        xpath_lower = f'{base}[starts-with(@content-desc, "{lower_char} ") and @clickable="true"]'
        print(f"  [auth]   'Capital {upper_char}' 못 찾음 → '{lower_char}' fallback 시도")
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, xpath_lower))
        ).click()
    else:
        # 일반 소문자 모드: "x 한글" 형식
        lower_char = char.lower()
        xpath = f'{base}[starts-with(@content-desc, "{lower_char} ") and @clickable="true"]'
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
        ).click()


def _click_keypad_button_by_desc(
    driver,
    keypad_id: str,
    desc: str,
    timeout: float = 5,
    fallback_descs: list[str] | None = None,
) -> None:
    """키패드에서 content-desc가 일치하는 버튼을 클릭합니다.

    exact match → fallback_descs → contains match 순서로 시도합니다.
    """
    descs_to_try = [desc] + (fallback_descs or [])

    last_error: Exception | None = None
    for d in descs_to_try:
        try:
            xpath = (
                f'//android.widget.FrameLayout[@resource-id="{keypad_id}"]'
                f'//android.widget.ImageView[@content-desc="{d}"]'
            )
            WebDriverWait(driver, min(timeout, 3)).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
            ).click()
            return
        except (NoSuchElementException, TimeoutException) as e:
            last_error = e

    # fallback: contains match (단일 문자 특수문자 등)
    if len(desc) <= 2:
        try:
            xpath = (
                f'//android.widget.FrameLayout[@resource-id="{keypad_id}"]'
                f'//android.widget.ImageView[contains(@content-desc, "{desc}") and @clickable="true"]'
            )
            WebDriverWait(driver, min(timeout, 3)).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
            ).click()
            print(f"  [auth]   '{desc}' contains match로 클릭")
            return
        except (NoSuchElementException, TimeoutException) as e:
            last_error = e

    if last_error is not None:
        raise last_error


# 특수문자 → 한국어 content-desc 매핑 (Live 앱 보안 키보드)
SPECIAL_CHAR_DESC_MAP = {
    "!": "느낌표",
    "@": "골뱅이",
    "#": "샵",
    "$": "달러",
    "%": "퍼센트",
    "^": "캐럿",
    "&": "앰퍼샌드",
    "*": "별표",
    "(": "왼쪽 괄호",
    ")": "오른쪽 괄호",
    "'": "아포스트로피",
    "-": "대시",
    "=": "이퀄",
    "\\": "백슬래시",
    "[": "왼쪽 대괄호",
    "]": "오른쪽 대괄호",
    ";": "세미콜론",
    "'": "작은 따옴표",
    ",": "쉼표",
    ".": "마침표",
    "/": "슬래시",
    "~": "물결 기호",
    "_": "밑줄",
    "+": "플러스",
    "|": "수직 막대",
    "{": "왼쪽 중괄호",
    "}": "오른쪽 중괄호",
    ":": "콜론",
    '"': "큰 따옴표",
    "<": "왼쪽 꺾쇠 괄호",
    ">": "오른쪽 꺾쇠 괄호",
    "?": "물음표",
}


# ---------------------------------------------------------------------------
# 커스텀 보안 키보드 - Staging 앱 (숫자 전용)
# ---------------------------------------------------------------------------

def _tap_security_keyboard_complete(driver, timeout: float = 10) -> None:
    """보안 키보드의 '입력완료' 버튼을 클릭합니다."""
    candidates = ["입력완료", "COMPLETE", "Complete", "완료"]
    last_error: Exception | None = None

    for label in candidates:
        try:
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, label))
            ).click()
            return
        except Exception as e:
            last_error = e

    if last_error is not None:
        raise last_error


# ---------------------------------------------------------------------------
# 비밀번호 입력 통합 함수
# ---------------------------------------------------------------------------

def enter_pin_via_security_keyboard(
    driver,
    pin: str,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 10,
) -> None:
    """보안 키보드로 비밀번호를 입력합니다.

    두 가지 앱 타입을 자동 구분:
    - Staging 앱: 숫자 전용 커스텀 키보드 (ACCESSIBILITY_ID로 숫자 클릭 + 입력완료)
    - Live 앱: QWERTY 커스텀 키보드 (영문+숫자+특수문자 지원 + 입력완료)

    두 앱 모두 커스텀 보안 키보드를 사용하며, send_keys는 차단됩니다.
    """
    with _step("비밀번호 입력"):
        pw_field = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, _id(resource_id_prefix, "securityKeyboardEditText"))
            )
        )
        pw_field.click()
        time.sleep(1)

        if _is_staging_app(resource_id_prefix):
            # Staging: 숫자 전용 키보드
            print("  [auth] Staging 앱 → 숫자 보안 키보드로 PIN 입력")
            for digit in pin:
                WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable(
                        (AppiumBy.ACCESSIBILITY_ID, str(digit))
                    )
                ).click()
            _tap_security_keyboard_complete(driver, timeout=timeout)
        else:
            # Live: QWERTY 커스텀 보안 키보드
            print("  [auth] Live 앱 → QWERTY 보안 키보드로 비밀번호 입력")
            _type_on_live_security_keyboard(
                driver, pin, resource_id_prefix, timeout=timeout,
            )


# ---------------------------------------------------------------------------
# 간편비밀번호 (Simple Password) 설정
# ---------------------------------------------------------------------------

def _enter_simple_password_pin(
    driver,
    pin: str,
    resource_id_prefix: str,
    timeout: float = 10,
) -> None:
    """간편비밀번호 숫자 키패드로 4자리 PIN을 입력합니다.

    키패드 구조 (keypadContainer → transKeypad_main):
    - 숫자 0-9가 랜덤 배치 (content-desc: 단일 숫자 "0"~"9")
    - 특수 버튼: "재배열", "삭제", "닫기"
    - 4자리 입력 후 자동 제출 (입력완료 불필요)
    """
    keypad_id = _id(resource_id_prefix, "keypadContainer")

    # 키패드 대기
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((AppiumBy.ID, keypad_id))
    )

    for i, digit in enumerate(pin):
        # 랜덤 배치된 키패드에서 숫자를 content-desc로 찾기
        xpath = (
            f'//android.widget.FrameLayout[@resource-id="{keypad_id}"]'
            f'//android.widget.ImageView[@content-desc="{digit}" and @clickable="true"]'
        )
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
        ).click()
        print(f"  [auth]   간편비밀번호 [{i+1}/4]: *")
        time.sleep(0.3)


def _handle_simple_password_setup(
    driver,
    simple_pin: str,
    resource_id_prefix: str,
    timeout: float = 15,
) -> bool:
    """로그인 후 간편비밀번호 설정 화면을 처리합니다.

    흐름:
    1. "Please create new simple Password" 화면 → 4자리 입력
    2. "Re-enter simple password for confirm" 화면 → 동일 4자리 재입력
    3. "Success" 팝업 → OK 클릭

    Returns:
        bool: 간편비밀번호 설정을 처리했으면 True
    """
    # 간편비밀번호 설정 화면 감지: input_dot_1 존재 + "simple" 또는 "Password" 텍스트
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, _id(resource_id_prefix, "input_dot_1"))
            )
        )
    except (NoSuchElementException, TimeoutException):
        print("  [auth] 간편비밀번호 설정 화면 없음 → 건너뜀")
        return False

    print(f"  [auth] 간편비밀번호 설정 시작 (PIN: {'*' * len(simple_pin)})")

    # Step 1: 첫 번째 입력 (생성)
    with _step("간편비밀번호 입력 (1/2)"):
        print("  [auth] [1/2] 간편비밀번호 생성 입력")
        _enter_simple_password_pin(driver, simple_pin, resource_id_prefix, timeout)
        time.sleep(2)

    # Step 2: 두 번째 입력 (확인)
    with _step("간편비밀번호 입력 (2/2)"):

        # "Re-enter simple password for confirm" 화면 대기
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(
                    (AppiumBy.XPATH,
                     "//*[contains(@text, 'Re-enter') or contains(@text, 're-enter')"
                     " or contains(@text, '재입력') or contains(@text, 'confirm')]")
                )
            )
        except (NoSuchElementException, TimeoutException):
            # 텍스트를 못 찾아도 input_dot_1이 있으면 진행
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (AppiumBy.ID, _id(resource_id_prefix, "input_dot_1"))
                    )
                )
            except (NoSuchElementException, TimeoutException):
                print("  [auth] 간편비밀번호 재입력 화면 감지 실패")
                return False

        print("  [auth] [2/2] 간편비밀번호 확인 입력")
        _enter_simple_password_pin(driver, simple_pin, resource_id_prefix, timeout)
        time.sleep(2)

    # Step 3: 성공 팝업 처리
    with _step("간편비밀번호 성공 팝업 확인"):
        _dismiss_success_popup(driver, resource_id_prefix, timeout=10)

    # Step 4: 설정 후 상태 확인
    time.sleep(2)

    # 잠금화면이 나타나면 방금 설정한 PIN으로 잠금 해제
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, _id(resource_id_prefix, "input_dot_1"))
            )
        )
        activity = driver.current_activity
        print(f"  [auth] 잠금화면 감지 (Activity: {activity}) → PIN 입력으로 해제")
        _enter_simple_password_pin(driver, simple_pin, resource_id_prefix, timeout)
        time.sleep(3)
    except (NoSuchElementException, TimeoutException):
        pass

    print("  [auth] 간편비밀번호 설정 완료")
    return True


def _dismiss_success_popup(
    driver,
    resource_id_prefix: str,
    timeout: float = 10,
) -> None:
    """성공 팝업의 OK 버튼을 클릭합니다. 여러 가지 형태 지원."""
    # 1차: btnOk (resource-id)
    try:
        ok_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (AppiumBy.ID, _id(resource_id_prefix, "btnOk"))
            )
        )
        print("  [auth] 성공 팝업 → btnOk 클릭")
        ok_btn.click()
        time.sleep(1)
        return
    except (NoSuchElementException, TimeoutException):
        pass

    # 2차: "OK" 텍스트 버튼
    try:
        ok_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//*[@text='OK' or @text='ok' or @text='Ok' or @text='확인']")
            )
        )
        print("  [auth] 성공 팝업 → OK 텍스트 클릭")
        ok_btn.click()
        time.sleep(1)
        return
    except (NoSuchElementException, TimeoutException):
        pass

    # 3차: 아무 Button 클릭 (성공 팝업이 다른 형태일 수 있음)
    try:
        btn = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//android.widget.Button[@enabled='true']")
            )
        )
        print(f"  [auth] 성공 팝업 → 버튼 클릭 (text: {btn.text})")
        btn.click()
        time.sleep(1)
        return
    except (NoSuchElementException, TimeoutException):
        pass

    print("  [auth] 성공 팝업 감지되지 않음 (자동 닫힘 가능성)")


# ---------------------------------------------------------------------------
# Simple Password 잠금 화면 처리 (이미 설정된 경우)
# ---------------------------------------------------------------------------

def _handle_simple_password_screen(driver, timeout: float = 5) -> bool:
    """Simple Password 잠금 화면이 있으면 'Login with ID/Password'를 탭합니다.

    이전에 로그인한 기록이 있으면 Simple Password 화면이 먼저 뜹니다.
    Simple Password를 모르는 경우 'Login with ID/Password' 버튼으로 우회합니다.

    흐름:
    1. 'Login with ID/Password' 버튼 클릭
    2. 확인 팝업 ("your simple password will be removed") → YES 클릭
    3. Complex Password 로그인 화면으로 이동

    Returns:
        bool: Simple Password 화면을 처리했으면 True
    """
    try:
        login_with_id_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//*[contains(@text, 'Login with ID/Password')]")
            )
        )
        print("  [auth] Simple Password 화면 감지 → 'Login with ID/Password' 클릭")
        login_with_id_btn.click()
        time.sleep(1)

        # 확인 팝업 처리: "your simple password will be removed" → YES 클릭
        try:
            yes_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH, "//*[@text='YES']")
                )
            )
            print("  [auth] 확인 팝업 → 'YES' 클릭")
            yes_btn.click()
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            time.sleep(1)

        return True
    except (NoSuchElementException, TimeoutException):
        return False


def _handle_password_lock_screen(
    driver,
    pin: str,
    resource_id_prefix: str,
    timeout: float = 5,
) -> bool:
    """'Enter password to unlock' 잠금화면을 처리합니다.

    이전 로그인 세션이 유효하지만 앱이 재시작된 경우 나타남.
    QWERTY 보안 키보드로 비밀번호를 다시 입력해야 합니다.

    Returns:
        bool: 잠금화면을 처리했으면 True
    """
    try:
        # "Enter password to unlock" 또는 "비밀번호를 입력" 텍스트 감지
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.XPATH,
                 "//*[contains(@text, 'Enter password') or contains(@text, 'unlock')"
                 " or contains(@text, '비밀번호를 입력')]")
            )
        )
    except (NoSuchElementException, TimeoutException):
        return False

    print("  [auth] 비밀번호 잠금화면 감지 → 비밀번호 입력으로 해제")

    # QWERTY 보안 키보드가 이미 열려 있으므로 바로 입력
    keypad_id = _id(resource_id_prefix, "keypadContainer")
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((AppiumBy.ID, keypad_id))
        )
        # 보안 키보드로 비밀번호 입력 (입력완료 포함)
        _type_on_live_security_keyboard(driver, pin, resource_id_prefix, timeout=10)
        time.sleep(3)
        print("  [auth] 잠금화면 비밀번호 입력 완료")
        return True
    except (NoSuchElementException, TimeoutException):
        print("  [auth] 잠금화면 키보드 감지 실패")
        return False


# ---------------------------------------------------------------------------
# 로그인 화면 네비게이션
# ---------------------------------------------------------------------------

def _handle_permission_screen(driver, timeout: float = 5) -> bool:
    """앱 최초 실행 시 나타나는 권한 동의 화면을 처리합니다.

    "Guide for using the service" / "서비스 이용 안내" 화면에서 "Agree" 클릭.
    앱 데이터 클리어 후 첫 실행 시 나타남.
    """
    try:
        agree_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (AppiumBy.XPATH,
                 "//*[@text='Agree' or @text='agree' or @text='동의' or @text='확인']")
            )
        )
        print("  [auth] 권한 동의 화면 → 'Agree' 클릭")
        agree_btn.click()
        time.sleep(2)
        return True
    except (NoSuchElementException, TimeoutException):
        return False


def navigate_to_login_screen(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 15,
    pin: str | None = None,
) -> bool:
    """Navigate from main screen to login screen if needed.

    지원하는 진입 경로:
    0. 권한 동의 화면 (앱 데이터 클리어 후) → "Agree" 클릭
    1. 이미 로그인 화면 (usernameId 존재) → 바로 진행
    2. 비밀번호 잠금화면 ("Enter password to unlock") → 비밀번호 입력 → 홈으로 직행
    3. Simple Password 잠금 화면 → 'Login with ID/Password' 클릭 → 로그인 화면
    4. 메인 화면 (btn_lgn 존재) → Login 버튼 클릭 → 로그인 화면

    Returns:
        bool: True이면 잠금화면 해제로 이미 로그인됨 (로그인 불필요).
              False이면 일반 로그인 화면에 도착 (로그인 필요).
    """
    # 권한 동의 화면 (pm clear 후 첫 실행)
    _handle_permission_screen(driver, timeout=5)

    if is_login_screen(driver, resource_id_prefix):
        return False

    # 비밀번호 잠금화면 처리: "Enter password to unlock" (이전 세션 유효)
    if pin and _handle_password_lock_screen(driver, pin, resource_id_prefix, timeout=5):
        # 잠금 해제 → 홈 화면으로 직행 (로그인 불필요)
        return True

    # Simple Password 화면 처리 (이전 로그인 기록이 있는 경우)
    if _handle_simple_password_screen(driver, timeout=5):
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id(resource_id_prefix, "usernameId"))
                )
            )
            return False
        except TimeoutException:
            print("  [auth] Login with ID/Password 후 usernameId 대기 실패, btn_lgn 시도")

    with _step("로그인 화면 진입"):
        # btn_lgn은 환율 데이터 로딩 후 나타남 → 먼저 직접 대기
        try:
            login_btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(
                    (AppiumBy.ID, _id(resource_id_prefix, "btn_lgn"))
                )
            )
            login_btn.click()
        except (NoSuchElementException, TimeoutException):
            # btn_lgn이 안 보이면 스크롤 후 재시도
            print("  [auth] btn_lgn 미발견 → 스크롤 후 재시도")
            _scroll_down(driver)
            time.sleep(2)
            login_btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(
                    (AppiumBy.ID, _id(resource_id_prefix, "btn_lgn"))
                )
            )
            login_btn.click()

        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, _id(resource_id_prefix, "usernameId"))
            )
        )
        return False


def _scroll_down(driver, scroll_ratio: float = 0.5) -> None:
    """화면을 아래로 스크롤합니다."""
    size = driver.get_window_size()
    start_x = size["width"] // 2
    start_y = int(size["height"] * 0.7)
    end_y = int(size["height"] * (0.7 - scroll_ratio * 0.4))
    driver.swipe(start_x, start_y, start_x, end_y, duration=300)


# ---------------------------------------------------------------------------
# 로그인 에러 확인
# ---------------------------------------------------------------------------

def _check_login_error(driver, timeout: float = 3) -> None:
    """로그인 후 에러 팝업이 있으면 RuntimeError를 발생시킵니다.

    에러 팝업 예시: "Login Failed - You have N attempts left"
    """
    try:
        error_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.XPATH,
                 "//*[contains(@text, 'Login Failed') or contains(@text, 'login failed')"
                 " or contains(@text, 'cannot be empty') or contains(@text, 'Cannot be empty')]")
            )
        )
        error_msg = error_element.text
        print(f"  [auth] 로그인 실패 감지: {error_msg}")

        # OK 버튼 클릭하여 팝업 닫기
        try:
            ok_btn = driver.find_element(
                AppiumBy.XPATH, "//*[@text='OK' or @text='ok' or @text='Ok']"
            )
            ok_btn.click()
            time.sleep(0.5)
        except NoSuchElementException:
            pass

        raise RuntimeError(f"로그인 실패: {error_msg}")

    except TimeoutException:
        # 에러 팝업 없음 → 정상
        pass


# ---------------------------------------------------------------------------
# 로그인 후 팝업 처리
# ---------------------------------------------------------------------------

def _handle_post_login_popups(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    max_attempts: int = 3,
) -> None:
    """로그인 후 발생할 수 있는 팝업들을 순차적으로 처리합니다.

    - 지문 인증 설정 화면
    - 보이스피싱 경고 팝업
    """
    for _ in range(max_attempts):
        fingerprint_handled = _handle_fingerprint_setup_if_present(
            driver, resource_id_prefix=resource_id_prefix
        )
        phishing_handled = _handle_voice_phishing_popup_if_present(
            driver, resource_id_prefix=resource_id_prefix
        )

        if not fingerprint_handled and not phishing_handled:
            break


def _handle_voice_phishing_popup_if_present(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 3,
) -> bool:
    """로그인 후 보이스피싱 경고 팝업이 있으면 처리합니다."""
    try:
        checkbox = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ID, _id(resource_id_prefix, "check_customer"))
            )
        )

        with _step("보이스피싱 경고 팝업 처리"):
            checkbox.click()
            time.sleep(0.5)

            confirm_button_texts = ["확인", "OK", "ok", "Ok"]
            button_clicked = False

            for text in confirm_button_texts:
                try:
                    confirm_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (AppiumBy.XPATH, f"//android.widget.Button[@text='{text}']")
                        )
                    )
                    confirm_button.click()
                    button_clicked = True
                    break
                except (NoSuchElementException, TimeoutException):
                    continue

            if not button_clicked:
                try:
                    any_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (AppiumBy.XPATH, "//android.widget.Button[@enabled='true']")
                        )
                    )
                    any_button.click()
                except (NoSuchElementException, TimeoutException):
                    pass

            time.sleep(1)

        return True

    except (NoSuchElementException, TimeoutException):
        return False


def _handle_fingerprint_setup_if_present(
    driver,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 2,
) -> bool:
    """로그인 후 지문 인증 설정 화면이 있으면 [나중에] 버튼을 탭합니다."""
    try:
        later_element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (AppiumBy.ID, _id(resource_id_prefix, "txt_pennytest_msg"))
            )
        )

        with _step("지문 인증 설정 화면 - 나중에 선택"):
            later_element.click()
            time.sleep(1)

        return True

    except (NoSuchElementException, TimeoutException):
        pass

    later_button_texts = ["나중에", "Later", "LATER", "다음에", "취소", "Cancel"]
    xpath_conditions = " or ".join([f"@text='{t}'" for t in later_button_texts])
    xpath = f"//*[{xpath_conditions}]"

    try:
        later_element = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
        )

        with _step("지문 인증 설정 화면 - 나중에 선택"):
            later_element.click()
            time.sleep(1)

        return True

    except (NoSuchElementException, TimeoutException):
        return False


# ---------------------------------------------------------------------------
# 메인 로그인 함수
# ---------------------------------------------------------------------------

def login(
    driver,
    username: str = DEFAULT_USERNAME,
    pin: str = DEFAULT_PIN,
    resource_id_prefix: str = DEFAULT_RESOURCE_ID_PREFIX,
    timeout: float = 15,
    post_login_sleep: float = 2.0,
    set_english: bool = True,
    simple_pin: str | None = None,
) -> None:
    """로그인 전체 흐름을 수행합니다.

    Args:
        driver: Appium WebDriver 인스턴스
        username: 로그인 아이디 (기본값: 환경변수 STG_ID)
        pin: 로그인 비밀번호 (기본값: 환경변수 STG_PW)
        resource_id_prefix: 앱의 resource-id 접두사
        timeout: 대기 시간 (초)
        post_login_sleep: 로그인 후 대기 시간 (초)
        set_english: True이면 언어 선택 화면에서 English 자동 선택
        simple_pin: 간편비밀번호 4자리. 지정하면 로그인 후 간편비밀번호 설정 처리.
                    None이면 간편비밀번호 설정을 건너뜀.

    전체 흐름:
    1. 언어 선택 (English)
    2. 로그인 화면 진입 (btn_lgn 또는 Simple Password 우회)
    3. 아이디 입력 (usernameId)
    4. 비밀번호 입력 (커스텀 보안 키보드)
    5. 로그인 버튼 클릭 (btn_submit)
    6. 로그인 결과 확인 (에러 팝업 체크)
    7. 후속 팝업 처리 (지문 인증, 보이스피싱)
    8. 간편비밀번호 설정 (simple_pin 지정 시)
    """
    if not username or not pin:
        raise ValueError(
            "username과 pin이 필요합니다. "
            "환경변수 STG_ID/STG_PW 또는 LIVE_ID/LIVE_PW를 설정하거나 "
            ".env 파일에 추가하세요."
        )

    # 언어 선택 화면이 나타나면 English 선택
    if set_english:
        ensure_english_language(
            driver, resource_id_prefix=resource_id_prefix, timeout=timeout,
        )

    already_logged_in = navigate_to_login_screen(
        driver, resource_id_prefix=resource_id_prefix, timeout=timeout,
        pin=pin,
    )

    if already_logged_in:
        # 잠금화면 해제로 이미 로그인됨 → 로그인 스텝 건너뜀
        print("  [auth] 잠금화면 해제 → 이미 로그인 상태")
        _handle_post_login_popups(driver, resource_id_prefix=resource_id_prefix)
    else:
        # 일반 로그인 흐름
        with _step("아이디 입력"):
            username_field = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(
                    (AppiumBy.ID, _id(resource_id_prefix, "usernameId"))
                )
            )
            try:
                username_field.clear()
            except Exception:
                pass
            username_field.send_keys(username)
            print(f"  [auth] 아이디 입력: {username[:3]}***")

        enter_pin_via_security_keyboard(
            driver,
            pin=pin,
            resource_id_prefix=resource_id_prefix,
            timeout=timeout,
        )

        # Login 버튼 클릭
        with _step("로그인 버튼 클릭"):
            try:
                submit_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (AppiumBy.ID, _id(resource_id_prefix, "btn_submit"))
                    )
                )
                submit_btn.click()
                print("  [auth] btn_submit 클릭")
            except (NoSuchElementException, TimeoutException):
                print("  [auth] btn_submit 없음 (자동 제출됨)")

        with _step("로그인 완료 대기"):
            time.sleep(post_login_sleep)

        # 로그인 실패 에러 팝업 확인
        _check_login_error(driver)
        print("  [auth] 로그인 성공 (에러 없음)")

        # 로그인 후 팝업 처리 (지문 인증, 보이스피싱)
        _handle_post_login_popups(driver, resource_id_prefix=resource_id_prefix)

    # 간편비밀번호 설정 처리
    if simple_pin:
        # 간편비밀번호 설정 화면이 나타날 때까지 잠시 대기
        time.sleep(2)
        _handle_simple_password_setup(
            driver,
            simple_pin=simple_pin,
            resource_id_prefix=resource_id_prefix,
            timeout=timeout,
        )

    # 간편비밀번호 설정 후에도 팝업이 나타날 수 있음 (보이스피싱 경고 등)
    _handle_post_login_popups(driver, resource_id_prefix=resource_id_prefix)
