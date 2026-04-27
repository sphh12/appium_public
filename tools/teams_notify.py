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

"""Teams Incoming Webhook으로 테스트 결과를 전송합니다.

사용법:
  # 테스트 메시지 전송 (Webhook URL 연결 확인)
  python tools/teams_notify.py --test

  # 테스트 결과 전송 (직접 호출)
  python tools/teams_notify.py --result '{"passed":8,"failed":1,"broken":1,"skipped":0}'

  # 다른 스크립트에서 import하여 사용
  from teams_notify import send_test_result
"""

import argparse
import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# .env 파일 자동 로드
_env_file = Path(__file__).resolve().parent.parent / ".env"
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

# 대시보드 URL (결과 링크용)
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "https://allure-dashboard-three.vercel.app")


def _get_webhook_url() -> str:
    """환경변수에서 Teams Webhook URL을 가져옵니다."""
    url = os.environ.get("TEAMS_WEBHOOK_URL", "")
    if not url:
        print("[teams_notify] TEAMS_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
        print("[teams_notify] .env 파일에 TEAMS_WEBHOOK_URL=https://... 을 추가하세요.")
        sys.exit(1)
    return url


def _status_emoji(status: str) -> str:
    """테스트 상태에 따른 이모지를 반환합니다."""
    return {
        "passed": "✅",
        "failed": "❌",
        "broken": "⚠️",
        "skipped": "⏭️",
        "error": "🔴",
    }.get(status, "ℹ️")


def _overall_status(result: dict) -> tuple[str, str]:
    """전체 결과 상태와 색상을 반환합니다.

    Returns:
        (상태 텍스트, Adaptive Card 색상)
    """
    failed = result.get("failed", 0)
    broken = result.get("broken", 0)
    passed = result.get("passed", 0)
    total = passed + failed + broken + result.get("skipped", 0)

    if failed > 0 or broken > 0:
        return f"실패 ({failed + broken}/{total})", "attention"  # 빨간색
    if total == 0:
        return "결과 없음", "default"
    return f"전체 통과 ({passed}/{total})", "good"  # 초록색


def build_result_card(result: dict) -> dict:
    """테스트 결과를 Teams Adaptive Card로 변환합니다.

    Args:
        result: {
            "passed": int,
            "failed": int,
            "broken": int,
            "skipped": int,
            "total": int (선택),
            "duration": str (선택, 예: "3분 42초"),
            "platform": str (선택, 예: "Android"),
            "device": str (선택, 예: "Pixel_6"),
            "app_version": str (선택, 예: "7.15.0"),
            "test_target": str (선택, 예: "local_transfer"),
            "timestamp": str (선택, 예: "20260407_153000"),
            "trigger_id": str (선택, 트리거 ID),
            "requested_by": str (선택, 요청자),
        }

    Returns:
        Adaptive Card JSON (Teams Webhook 전송용)
    """
    passed = result.get("passed", 0)
    failed = result.get("failed", 0)
    broken = result.get("broken", 0)
    skipped = result.get("skipped", 0)
    total = result.get("total", passed + failed + broken + skipped)
    duration = result.get("duration", "-")
    platform = result.get("platform", "Android")
    device = result.get("device", "-")
    app_version = result.get("app_version", "-")
    test_target = result.get("test_target", "전체")
    timestamp = result.get("timestamp", "")
    requested_by = result.get("requested_by", "")

    status_text, status_color = _overall_status(result)

    # 통과율 계산
    pass_rate = f"{(passed / total * 100):.0f}%" if total > 0 else "-"

    # 헤더 아이콘
    header_icon = "🟢" if status_color == "good" else "🔴"

    # 결과 요약 텍스트
    stats_line = (
        f"✅ Passed: **{passed}**  ·  "
        f"❌ Failed: **{failed}**  ·  "
        f"⚠️ Broken: **{broken}**  ·  "
        f"⏭️ Skipped: **{skipped}**"
    )

    # 환경 정보 텍스트
    env_line = f"📱 {platform}"
    if device and device != "-":
        env_line += f" / {device}"
    if app_version and app_version != "-":
        env_line += f" / v{app_version}"

    # 카드 body 구성
    body = [
        # 헤더
        {
            "type": "TextBlock",
            "size": "large",
            "weight": "bolder",
            "text": f"{header_icon} 테스트 완료 — {test_target}",
            "wrap": True,
        },
        # 구분선
        {
            "type": "TextBlock",
            "text": f"**{status_text}** · Pass Rate: **{pass_rate}**",
            "wrap": True,
            "spacing": "small",
        },
        # 결과 수치
        {
            "type": "TextBlock",
            "text": stats_line,
            "wrap": True,
            "spacing": "medium",
        },
        # 소요시간
        {
            "type": "FactSet",
            "facts": [
                {"title": "⏱️ 소요시간", "value": duration},
                {"title": "📱 환경", "value": env_line.replace("📱 ", "")},
            ],
            "spacing": "medium",
        },
    ]

    # 요청자 정보 (있으면 추가)
    if requested_by:
        body[3]["facts"].append({"title": "👤 요청자", "value": requested_by})

    # 실행 시각
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    body[3]["facts"].append({"title": "🕐 실행 시각", "value": now_str})

    # 대시보드 링크 버튼
    actions = []
    if timestamp:
        actions.append({
            "type": "Action.OpenUrl",
            "title": "📊 대시보드에서 보기",
            "url": f"{DASHBOARD_URL}/runs/{timestamp}",
        })
    actions.append({
        "type": "Action.OpenUrl",
        "title": "📋 전체 대시보드",
        "url": DASHBOARD_URL,
    })

    # Adaptive Card 최종 구조
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": body,
                    "actions": actions,
                },
            }
        ],
    }

    return card


def build_trigger_started_card(trigger_info: dict) -> dict:
    """테스트 실행 시작 알림 카드를 생성합니다.

    Args:
        trigger_info: {
            "test_target": str,
            "platform": str,
            "requested_by": str (선택),
            "trigger_id": str (선택),
        }
    """
    test_target = trigger_info.get("test_target", "전체")
    platform = trigger_info.get("platform", "Android")
    requested_by = trigger_info.get("requested_by", "")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    body = [
        {
            "type": "TextBlock",
            "size": "large",
            "weight": "bolder",
            "text": f"🚀 테스트 실행 시작 — {test_target}",
            "wrap": True,
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "📱 플랫폼", "value": platform},
                {"title": "🕐 시작 시각", "value": now_str},
            ],
            "spacing": "medium",
        },
    ]

    if requested_by:
        body[1]["facts"].append({"title": "👤 요청자", "value": requested_by})

    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": body,
                },
            }
        ],
    }

    return card


def build_error_card(error_msg: str, test_target: str = "알 수 없음") -> dict:
    """에러 발생 시 알림 카드를 생성합니다."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "large",
                            "weight": "bolder",
                            "text": f"🔴 테스트 실행 실패 — {test_target}",
                            "wrap": True,
                        },
                        {
                            "type": "TextBlock",
                            "text": f"```\n{error_msg[:500]}\n```",
                            "wrap": True,
                            "spacing": "medium",
                        },
                        {
                            "type": "TextBlock",
                            "text": f"🕐 {now_str}",
                            "spacing": "small",
                            "isSubtle": True,
                        },
                    ],
                },
            }
        ],
    }

    return card


def send_to_teams(card: dict, webhook_url: str | None = None) -> bool:
    """Adaptive Card를 Teams Webhook으로 전송합니다.

    Args:
        card: build_result_card() 등으로 생성한 카드 JSON
        webhook_url: Webhook URL (None이면 환경변수에서 가져옴)

    Returns:
        전송 성공 여부
    """
    url = webhook_url or _get_webhook_url()

    data = json.dumps(card).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.getcode()
            print(f"[teams_notify] Teams 전송 완료 (HTTP {status})")
            return True
    except urllib.error.HTTPError as e:
        print(f"[teams_notify] Teams 전송 실패: HTTP {e.code}")
        try:
            body = e.read().decode("utf-8", errors="replace")
            print(f"[teams_notify] 응답: {body[:300]}")
        except Exception:
            pass
        return False
    except urllib.error.URLError as e:
        print(f"[teams_notify] Teams 연결 실패: {e.reason}")
        return False
    except Exception as e:
        print(f"[teams_notify] 알 수 없는 오류: {e}")
        return False


def send_test_result(result: dict, webhook_url: str | None = None) -> bool:
    """테스트 결과를 Teams로 전송하는 간편 함수.

    다른 스크립트에서 import하여 사용:
        from teams_notify import send_test_result
        send_test_result({"passed": 10, "failed": 0, "broken": 0, "skipped": 0})
    """
    card = build_result_card(result)
    return send_to_teams(card, webhook_url)


def send_trigger_started(trigger_info: dict, webhook_url: str | None = None) -> bool:
    """테스트 실행 시작 알림을 Teams로 전송합니다."""
    card = build_trigger_started_card(trigger_info)
    return send_to_teams(card, webhook_url)


def send_error(error_msg: str, test_target: str = "알 수 없음",
               webhook_url: str | None = None) -> bool:
    """에러 알림을 Teams로 전송합니다."""
    card = build_error_card(error_msg, test_target)
    return send_to_teams(card, webhook_url)


# ─── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Teams Incoming Webhook 알림 도구")
    parser.add_argument("--test", action="store_true",
                        help="테스트 메시지를 Teams에 전송하여 연결 확인")
    parser.add_argument("--result", type=str,
                        help='JSON 형식 테스트 결과 (예: \'{"passed":8,"failed":1}\')')
    parser.add_argument("--webhook-url", type=str,
                        help="Teams Webhook URL (미지정 시 환경변수 사용)")
    args = parser.parse_args()

    webhook_url = args.webhook_url

    if args.test:
        # 테스트 메시지 전송
        print("[teams_notify] 테스트 메시지를 Teams에 전송합니다...")
        test_result = {
            "passed": 8,
            "failed": 1,
            "broken": 1,
            "skipped": 0,
            "duration": "3분 42초",
            "platform": "Android",
            "device": "Pixel_6",
            "app_version": "7.15.0",
            "test_target": "테스트 메시지",
            "timestamp": "",
        }
        card = build_result_card(test_result)
        ok = send_to_teams(card, webhook_url)
        if ok:
            print("[teams_notify] ✅ 테스트 메시지 전송 성공! Teams 채널을 확인하세요.")
        else:
            print("[teams_notify] ❌ 테스트 메시지 전송 실패. Webhook URL을 확인하세요.")
        return

    if args.result:
        # JSON 결과 전송
        try:
            result = json.loads(args.result)
        except json.JSONDecodeError as e:
            print(f"[teams_notify] JSON 파싱 오류: {e}")
            sys.exit(1)
        ok = send_test_result(result, webhook_url)
        sys.exit(0 if ok else 1)

    # 인자 없으면 도움말 표시
    parser.print_help()


if __name__ == "__main__":
    main()
