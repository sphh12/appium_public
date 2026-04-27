# -*- coding: utf-8 -*-
import sys
import os
# Windows cp949 인코딩 문제 방지
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

"""테스트 트리거를 감지하고 pytest를 실행하는 리스너입니다.

사용법:
  # 수동 모드 — 바로 테스트 실행 + Teams 알림
  python tools/trigger_listener.py --manual
  python tools/trigger_listener.py --manual --target local_transfer
  python tools/trigger_listener.py --manual --target local_transfer --marker smoke
  python tools/trigger_listener.py --manual --platform ios

  # 폴링 모드 — Vercel API에서 트리거 대기 (대시보드 API 구축 후)
  python tools/trigger_listener.py
  python tools/trigger_listener.py --interval 15

  # Teams 알림 없이 실행
  python tools/trigger_listener.py --manual --no-notify
"""

import argparse
import json
import re
import subprocess
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# .env 파일 자동 로드
_env_file = PROJECT_ROOT / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_env_file)
except ImportError:
    if _env_file.exists():
        for line in _env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

# teams_notify 모듈 import
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from teams_notify import send_test_result, send_trigger_started, send_error
    TEAMS_AVAILABLE = True
except ImportError:
    TEAMS_AVAILABLE = False
    print("[trigger_listener] teams_notify 모듈을 찾을 수 없습니다. Teams 알림 비활성화.")

# 대시보드 API URL
DASHBOARD_API_URL = os.environ.get(
    "DASHBOARD_API_URL",
    "https://allure-dashboard-three.vercel.app"
)

# 테스트 파일 매핑 (target 이름 → pytest 경로)
TEST_TARGET_MAP = {
    "local_transfer": "tests/android/local_transfer_test.py",
    "basic": "tests/android/basic_01_test.py",
    "gme1": "tests/android/gme1_test.py",
    "ios_contacts": "tests/ios/ios_contacts_test.py",
    "ios_first": "tests/ios/test_ios_first.py",
    # "all" → 전체 실행 (별도 처리)
}

# 타임스탬프 정규식 (Allure 결과 폴더)
_TIMESTAMP_RE = re.compile(r"^\d{8}_\d{6}$")


def _resolve_pytest_args(target: str | None, marker: str | None,
                         platform: str = "android") -> list[str]:
    """트리거 옵션을 pytest 인자로 변환합니다.

    Args:
        target: 테스트 타겟 이름 (예: "local_transfer") 또는 None (전체)
        marker: pytest 마커 (예: "smoke") 또는 None
        platform: "android" 또는 "ios"

    Returns:
        pytest 인자 리스트 (예: ["tests/android/local_transfer_test.py", "-v"])
    """
    args = []

    # 테스트 대상 결정
    if target and target != "all":
        if target in TEST_TARGET_MAP:
            args.append(TEST_TARGET_MAP[target])
        elif target.endswith(".py"):
            # 직접 파일 경로 지정
            args.append(target)
        else:
            print(f"[trigger_listener] 알 수 없는 타겟: {target}")
            print(f"[trigger_listener] 사용 가능: {', '.join(TEST_TARGET_MAP.keys())}, all")
            return []
    else:
        # 전체 실행 — 플랫폼별 디렉토리
        if platform == "ios":
            args.append("tests/ios/")
        else:
            args.append("tests/android/")

    # 플랫폼 옵션
    args.extend(["--platform", platform])

    # 마커 옵션
    if marker:
        args.extend(["-m", marker])

    # 기본 옵션
    args.append("-v")

    return args


def _parse_allure_results(results_dir: Path) -> dict:
    """Allure 결과 디렉토리에서 테스트 통계를 파싱합니다.

    Returns:
        {"passed": int, "failed": int, "broken": int, "skipped": int, "total": int, "duration": str}
    """
    stats = {"passed": 0, "failed": 0, "broken": 0, "skipped": 0}
    total_duration_ms = 0

    if not results_dir.exists():
        return {**stats, "total": 0, "duration": "-"}

    for f in results_dir.glob("*-result.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            status = data.get("status", "unknown")
            if status in stats:
                stats[status] += 1

            # 소요시간 합산
            start = data.get("start", 0)
            stop = data.get("stop", 0)
            if stop > start:
                total_duration_ms += (stop - start)
        except (json.JSONDecodeError, OSError):
            continue

    total = sum(stats.values())

    # 소요시간 포맷
    if total_duration_ms > 0:
        secs = total_duration_ms // 1000
        mins, secs = divmod(secs, 60)
        if mins > 0:
            duration = f"{mins}분 {secs}초"
        else:
            duration = f"{secs}초"
    else:
        duration = "-"

    return {**stats, "total": total, "duration": duration}


def _get_env_info() -> dict:
    """현재 환경 정보를 수집합니다."""
    app_env = os.environ.get("APP_ENV", "stage")
    platform = "Android"  # 기본값

    # APK 버전 추출 시도
    app_version = "-"
    apk_dir = PROJECT_ROOT / "apk" / app_env
    if apk_dir.exists():
        apks = sorted(apk_dir.glob("*.apk"))
        if apks:
            # 파일명에서 버전 추출 (예: 7.15.0_stg.apk → 7.15.0)
            name = apks[-1].stem
            match = re.search(r"(\d+\.\d+\.\d+)", name)
            if match:
                app_version = match.group(1)

    # 디바이스 이름
    device = os.environ.get("ANDROID_DEVICE_NAME", "Emulator")

    return {
        "platform": platform,
        "device": device,
        "app_version": app_version,
    }


def run_tests(target: str | None = None, marker: str | None = None,
              platform: str = "android", notify: bool = True,
              requested_by: str = "") -> dict:
    """pytest를 실행하고 결과를 반환합니다.

    Args:
        target: 테스트 타겟 (예: "local_transfer")
        marker: pytest 마커 (예: "smoke")
        platform: "android" 또는 "ios"
        notify: Teams 알림 여부
        requested_by: 요청자 이름

    Returns:
        실행 결과 dict (teams_notify 형식)
    """
    test_target_display = target or "전체"
    print(f"\n{'='*60}")
    print(f"[trigger_listener] 테스트 실행 시작: {test_target_display}")
    print(f"[trigger_listener] 플랫폼: {platform}, 마커: {marker or '없음'}")
    print(f"{'='*60}\n")

    # Teams 시작 알림
    if notify and TEAMS_AVAILABLE:
        send_trigger_started({
            "test_target": test_target_display,
            "platform": platform.capitalize(),
            "requested_by": requested_by,
        })

    # pytest 인자 구성
    pytest_args = _resolve_pytest_args(target, marker, platform)
    if not pytest_args:
        error_msg = f"테스트 타겟을 찾을 수 없습니다: {target}"
        if notify and TEAMS_AVAILABLE:
            send_error(error_msg, test_target_display)
        return {"error": error_msg}

    # 타임스탬프 & 결과 디렉토리
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = PROJECT_ROOT / "allure-results" / timestamp
    reports_dir = PROJECT_ROOT / "allure-reports"

    # run_allure.py를 통해 실행 (히스토리 + 리포트 생성 + 업로드 포함)
    run_allure_script = Path(__file__).resolve().parent / "run_allure.py"
    cmd = [
        sys.executable, str(run_allure_script),
        "--results-root", str(PROJECT_ROOT / "allure-results"),
        "--reports-root", str(reports_dir),
        "--", *pytest_args,
    ]

    print(f"[trigger_listener] 실행 명령: {' '.join(cmd)}")
    start_time = time.time()

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=os.environ.copy(),
            timeout=600,  # 10분 타임아웃
        )
        returncode = proc.returncode
    except subprocess.TimeoutExpired:
        error_msg = "테스트 실행 타임아웃 (10분 초과)"
        print(f"[trigger_listener] ❌ {error_msg}")
        if notify and TEAMS_AVAILABLE:
            send_error(error_msg, test_target_display)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"테스트 실행 오류: {e}"
        print(f"[trigger_listener] ❌ {error_msg}")
        if notify and TEAMS_AVAILABLE:
            send_error(error_msg, test_target_display)
        return {"error": error_msg}

    elapsed = time.time() - start_time
    mins, secs = divmod(int(elapsed), 60)
    elapsed_str = f"{mins}분 {secs}초" if mins > 0 else f"{secs}초"

    # Allure 결과 파싱
    # run_allure.py가 생성한 타임스탬프 디렉토리 찾기
    actual_results_dir = _find_latest_results_dir(PROJECT_ROOT / "allure-results")
    if actual_results_dir:
        stats = _parse_allure_results(actual_results_dir)
        actual_timestamp = actual_results_dir.name
    else:
        stats = {"passed": 0, "failed": 0, "broken": 0, "skipped": 0, "total": 0}
        actual_timestamp = timestamp

    # 환경 정보
    env_info = _get_env_info()

    # 최종 결과
    result = {
        **stats,
        "duration": stats.get("duration", elapsed_str),
        "platform": platform.capitalize(),
        "device": env_info["device"],
        "app_version": env_info["app_version"],
        "test_target": test_target_display,
        "timestamp": actual_timestamp,
        "requested_by": requested_by,
        "returncode": returncode,
    }

    # 결과 출력
    print(f"\n{'='*60}")
    print(f"[trigger_listener] 테스트 완료: {test_target_display}")
    print(f"[trigger_listener] 결과: ✅{stats['passed']} ❌{stats['failed']} "
          f"⚠️{stats['broken']} ⏭️{stats['skipped']}")
    print(f"[trigger_listener] 소요시간: {elapsed_str}")
    print(f"{'='*60}\n")

    # Teams 결과 알림
    if notify and TEAMS_AVAILABLE:
        send_test_result(result)

    return result


def _find_latest_results_dir(root: Path) -> Path | None:
    """allure-results에서 가장 최근 타임스탬프 디렉토리를 찾습니다."""
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir() and _TIMESTAMP_RE.match(p.name)]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.name)[-1]


# ─── 폴링 모드 (Vercel API) ────────────────────────────────────────

def _fetch_pending_trigger() -> dict | None:
    """Vercel API에서 대기 중인 트리거를 조회합니다.

    Returns:
        트리거 정보 dict 또는 None
    """
    url = f"{DASHBOARD_API_URL}/api/trigger?status=pending"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            triggers = data.get("triggers", [])
            if triggers:
                return triggers[0]  # 가장 오래된 pending 트리거
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        pass  # 폴링 실패는 조용히 무시 (다음 주기에 재시도)
    except Exception:
        pass

    return None


def _update_trigger_status(trigger_id: str, status: str, result: dict | None = None):
    """Vercel API에서 트리거 상태를 업데이트합니다."""
    url = f"{DASHBOARD_API_URL}/api/trigger"
    payload = {
        "id": trigger_id,
        "status": status,
    }
    if result:
        payload["result"] = result

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PATCH")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[trigger_listener] 트리거 상태 업데이트: {status}")
    except Exception as e:
        print(f"[trigger_listener] 트리거 상태 업데이트 실패: {e}")


def polling_loop(interval: int = 10, notify: bool = True):
    """Vercel API를 폴링하며 트리거를 대기합니다.

    Args:
        interval: 폴링 간격 (초)
        notify: Teams 알림 여부
    """
    print(f"[trigger_listener] 폴링 모드 시작 (간격: {interval}초)")
    print(f"[trigger_listener] API: {DASHBOARD_API_URL}/api/trigger")
    print(f"[trigger_listener] Ctrl+C로 종료\n")

    while True:
        try:
            trigger = _fetch_pending_trigger()
            if trigger:
                trigger_id = trigger.get("id", "")
                target = trigger.get("testTarget")
                platform = trigger.get("platform", "android")
                requested_by = trigger.get("requestedBy", "")
                marker = trigger.get("marker")

                print(f"[trigger_listener] 🔔 트리거 감지! ID: {trigger_id}")
                print(f"[trigger_listener]    타겟: {target or '전체'}, 플랫폼: {platform}")

                # 상태 → running
                _update_trigger_status(trigger_id, "running")

                # 테스트 실행
                result = run_tests(
                    target=target,
                    marker=marker,
                    platform=platform,
                    notify=notify,
                    requested_by=requested_by,
                )

                # 상태 → complete 또는 failed
                if "error" in result:
                    _update_trigger_status(trigger_id, "failed", result)
                else:
                    _update_trigger_status(trigger_id, "complete", result)

            time.sleep(interval)

        except KeyboardInterrupt:
            print("\n[trigger_listener] 폴링 중지.")
            break


# ─── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="테스트 트리거 리스너 (수동/폴링 모드)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 수동 실행 (전체 Android 테스트)
  python tools/trigger_listener.py --manual

  # 특정 테스트만 수동 실행
  python tools/trigger_listener.py --manual --target local_transfer

  # iOS 테스트 실행
  python tools/trigger_listener.py --manual --platform ios --target ios_first

  # 폴링 모드 (대시보드 API 트리거 대기)
  python tools/trigger_listener.py --interval 15

사용 가능한 테스트 타겟:
  """ + "\n  ".join(f"{k:20s} → {v}" for k, v in TEST_TARGET_MAP.items()) + """
  all                  → 플랫폼 전체 테스트
        """,
    )

    # 모드 선택
    parser.add_argument("--manual", action="store_true",
                        help="수동 모드: 바로 테스트 실행")

    # 테스트 옵션
    parser.add_argument("--target", type=str, default=None,
                        help="테스트 타겟 (예: local_transfer, basic, all)")
    parser.add_argument("--marker", "-m", type=str, default=None,
                        help="pytest 마커 (예: smoke)")
    parser.add_argument("--platform", type=str, default="android",
                        choices=["android", "ios"],
                        help="테스트 플랫폼 (기본: android)")

    # 폴링 옵션
    parser.add_argument("--interval", type=int, default=10,
                        help="폴링 간격 초 (기본: 10)")

    # 알림 옵션
    parser.add_argument("--no-notify", action="store_true",
                        help="Teams 알림 비활성화")
    parser.add_argument("--requested-by", type=str, default="",
                        help="요청자 이름 (Teams 카드에 표시)")

    args = parser.parse_args()
    notify = not args.no_notify

    if args.manual:
        # 수동 모드 — 바로 실행
        result = run_tests(
            target=args.target,
            marker=args.marker,
            platform=args.platform,
            notify=notify,
            requested_by=args.requested_by,
        )
        # 종료 코드 반환
        if "error" in result:
            sys.exit(1)
        sys.exit(result.get("returncode", 0))
    else:
        # 폴링 모드
        polling_loop(interval=args.interval, notify=notify)


if __name__ == "__main__":
    main()
