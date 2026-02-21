"""Allure 테스트 결과를 Next.js 대시보드 API로 업로드합니다.

사용법:
  # 단일 타임스탬프 업로드
  python tools/upload_to_dashboard.py 20260216_024413

  # 모든 기존 리포트 일괄 업로드 (마이그레이션)
  python tools/upload_to_dashboard.py --all

  # 커스텀 대시보드 URL
  python tools/upload_to_dashboard.py --dashboard-url https://my-dashboard.vercel.app 20260216_024413
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

# update_dashboard.py의 로직을 재사용
sys.path.insert(0, str(Path(__file__).resolve().parent))
from update_dashboard import (
    _load_run_summary,
    _extract_branch_commit,
    _duration_ms_to_hms,
    _safe_git_message,
    _TIMESTAMP_DIR_RE,
)

DEFAULT_DASHBOARD_URL = "http://localhost:3000"


def _build_payload(report_dir: Path, repo_root: Path) -> dict | None:
    """report_dir에서 메타데이터를 읽어 API POST 페이로드를 생성합니다."""
    run = _load_run_summary(report_dir)
    if not run:
        print(f"  [skip] {report_dir.name}: summary.json 없음")
        return None

    env = dict(run.environment or {})
    build_name = run.executor.get("buildName", "")
    branch = str(env.get("gitBranch") or "").strip()
    commit = str(env.get("gitCommit") or "").strip()
    message = str(env.get("gitMessage") or "").strip()

    if not branch or not commit:
        parsed_branch, parsed_commit = _extract_branch_commit(build_name)
        branch = branch or parsed_branch
        commit = commit or parsed_commit

    if not message and commit:
        message = _safe_git_message(repo_root, commit)

    env.update({
        "gitBranch": branch or None,
        "gitCommit": commit or None,
        "gitMessage": message or None,
    })

    return {
        "timestamp": run.timestamp,
        "stats": run.stats,
        "time": run.time,
        "durationText": _duration_ms_to_hms(run.time.get("duration", 0)),
        "executor": {
            "name": run.executor.get("name", ""),
            "type": run.executor.get("type", ""),
            "buildName": run.executor.get("buildName", ""),
            "buildUrl": run.executor.get("buildUrl", ""),
        },
        "environment": env,
        "suites": run.suites,
        "behaviors": run.behaviors,
        "packages": run.packages,
    }


def upload_run(payload: dict, dashboard_url: str) -> bool:
    """페이로드를 대시보드 API에 POST합니다."""
    url = f"{dashboard_url.rstrip('/')}/api/runs"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            if status in (200, 201):
                print(f"  [ok] {payload['timestamp']} → {status}")
                return True
            else:
                print(f"  [warn] {payload['timestamp']} → HTTP {status}")
                return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"  [error] {payload['timestamp']} → HTTP {e.code}: {body}")
        return False
    except Exception as e:
        print(f"  [error] {payload['timestamp']} → {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Allure 테스트 결과를 Next.js 대시보드 API로 업로드합니다."
    )
    parser.add_argument(
        "timestamps",
        nargs="*",
        help="업로드할 타임스탬프 (예: 20260216_024413)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="모든 기존 리포트를 일괄 업로드 (마이그레이션용)",
    )
    parser.add_argument(
        "--reports-root",
        default="allure-reports",
        help="Allure reports 루트 디렉토리 (기본: allure-reports)",
    )
    parser.add_argument(
        "--dashboard-url",
        default=DEFAULT_DASHBOARD_URL,
        help=f"대시보드 API URL (기본: {DEFAULT_DASHBOARD_URL})",
    )
    args = parser.parse_args()

    reports_root = Path(args.reports_root)
    repo_root = reports_root.resolve().parent

    if not reports_root.exists():
        print(f"[error] reports-root 경로가 존재하지 않습니다: {reports_root}")
        return 1

    # 업로드 대상 결정
    if args.all:
        targets = sorted(
            [d for d in reports_root.iterdir() if d.is_dir() and _TIMESTAMP_DIR_RE.match(d.name)],
            key=lambda p: p.name,
        )
    elif args.timestamps:
        targets = []
        for ts in args.timestamps:
            d = reports_root / ts
            if d.is_dir():
                targets.append(d)
            else:
                print(f"  [skip] {ts}: 디렉토리 없음")
    else:
        print("[error] 타임스탬프를 지정하거나 --all 옵션을 사용하세요.")
        return 2

    if not targets:
        print("[info] 업로드할 리포트가 없습니다.")
        return 0

    print(f"[upload] {len(targets)}개 리포트 → {args.dashboard_url}")
    ok = 0
    fail = 0

    for report_dir in targets:
        payload = _build_payload(report_dir, repo_root)
        if payload is None:
            fail += 1
            continue
        if upload_run(payload, args.dashboard_url):
            ok += 1
        else:
            fail += 1

    print(f"[done] 성공: {ok}, 실패: {fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
