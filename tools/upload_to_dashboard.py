"""Allure 테스트 결과를 Next.js 대시보드 API로 업로드합니다.

사용법:
  # 단일 타임스탬프 업로드 (메타데이터 + 첨부파일)
  python tools/upload_to_dashboard.py 20260216_024413

  # 모든 기존 리포트 일괄 업로드 (마이그레이션)
  python tools/upload_to_dashboard.py --all

  # 메타데이터만 업로드 (첨부파일 제외)
  python tools/upload_to_dashboard.py --no-attachments 20260216_024413

  # 커스텀 대시보드 URL
  python tools/upload_to_dashboard.py --dashboard-url https://my-dashboard.vercel.app 20260216_024413
"""

import argparse
import json
import os
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
    _read_json,
)

DEFAULT_DASHBOARD_URL = "https://allure-dashboard-three.vercel.app"
BLOB_API_URL = "https://blob.vercel-storage.com"


# ─── 첨부파일 관련 함수 ─────────────────────────────────────────────

def _collect_attachments(report_dir: Path) -> list[dict]:
    """test-cases JSON에서 첨부파일 메타데이터를 수집합니다.

    첨부파일은 testStage, beforeStages, afterStages 안에 중첩되어 있습니다.
    """
    test_cases_dir = report_dir / "data" / "test-cases"
    attachments_dir = report_dir / "data" / "attachments"

    if not test_cases_dir.exists() or not attachments_dir.exists():
        return []

    seen_sources: set[str] = set()
    result: list[dict] = []

    def _extract_from(obj):
        """dict 또는 list[dict]에서 attachments를 재귀적으로 추출합니다."""
        if isinstance(obj, dict):
            for att in obj.get("attachments") or []:
                source = att.get("source", "")
                if not source or source in seen_sources:
                    continue
                file_path = attachments_dir / source
                if not file_path.exists():
                    continue
                seen_sources.add(source)
                result.append({
                    "name": att.get("name", source),
                    "source": source,
                    "type": att.get("type", "application/octet-stream"),
                    "size": att.get("size") or file_path.stat().st_size,
                    "file_path": str(file_path),
                })
            # steps 안에도 첨부파일이 있을 수 있음
            for step in obj.get("steps") or []:
                _extract_from(step)
        elif isinstance(obj, list):
            for item in obj:
                _extract_from(item)

    for tc_file in test_cases_dir.glob("*.json"):
        tc = _read_json(tc_file)
        if not tc:
            continue
        # testStage, beforeStages, afterStages에서 첨부파일 추출
        for stage_key in ("testStage", "beforeStages", "afterStages"):
            _extract_from(tc.get(stage_key))

    return result


def _upload_to_blob(file_path: str, blob_path: str, content_type: str, token: str) -> str | None:
    """Vercel Blob REST API로 파일을 직접 업로드합니다. 성공 시 URL을 반환합니다."""
    with open(file_path, "rb") as f:
        data = f.read()

    req = urllib.request.Request(
        f"{BLOB_API_URL}/{blob_path}",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "x-content-type": content_type,
            "x-api-version": "7",
        },
        method="PUT",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("url", "")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"    [blob-error] {blob_path} → HTTP {e.code}: {body}")
        return None
    except Exception as e:
        print(f"    [blob-error] {blob_path} → {e}")
        return None


def _save_artifact_metadata(
    timestamp: str,
    artifacts: list[dict],
    dashboard_url: str,
) -> bool:
    """첨부파일 메타데이터를 대시보드 API에 POST합니다."""
    url = f"{dashboard_url.rstrip('/')}/api/runs/{timestamp}/artifacts"
    payload = [
        {
            "type": a["type"],
            "name": a["name"],
            "source": a["source"],
            "url": a["url"],
            "contentType": a["type"],
            "sizeBytes": a.get("size"),
        }
        for a in artifacts
    ]

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status in (200, 201):
                result = json.loads(resp.read().decode("utf-8"))
                print(f"    [artifacts] {result.get('saved', 0)}개 메타데이터 저장")
                return True
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"    [artifacts-error] HTTP {e.code}: {body}")
        return False
    except Exception as e:
        print(f"    [artifacts-error] {e}")
        return False


def upload_attachments(
    report_dir: Path,
    timestamp: str,
    dashboard_url: str,
    blob_token: str,
) -> bool:
    """첨부파일을 Vercel Blob에 업로드하고 메타데이터를 대시보드에 저장합니다."""
    attachments = _collect_attachments(report_dir)
    if not attachments:
        print(f"    [info] {timestamp}: 첨부파일 없음")
        return True

    print(f"    [blob] {len(attachments)}개 첨부파일 업로드 중...")
    uploaded: list[dict] = []

    for att in attachments:
        blob_path = f"attachments/{timestamp}/{att['source']}"
        url = _upload_to_blob(att["file_path"], blob_path, att["type"], blob_token)
        if url:
            att["url"] = url
            uploaded.append(att)
            size_kb = att["size"] / 1024
            print(f"      ✓ {att['source']} ({size_kb:.0f}KB)")
        else:
            print(f"      ✗ {att['source']} (업로드 실패)")

    if not uploaded:
        print(f"    [warn] {timestamp}: 업로드된 첨부파일 없음")
        return False

    return _save_artifact_metadata(timestamp, uploaded, dashboard_url)


# ─── 기존 함수 ────────────────────────────────────────────────────

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
        "--no-attachments",
        action="store_true",
        help="첨부파일 업로드 건너뛰기 (메타데이터만 업로드)",
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

    # Blob 토큰 확인
    blob_token = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
    if not args.no_attachments and not blob_token:
        print("[warn] BLOB_READ_WRITE_TOKEN 미설정 → 첨부파일 업로드 건너뜀")
        print("       .env 파일에 BLOB_READ_WRITE_TOKEN을 추가하거나 --no-attachments 옵션을 사용하세요.")
        args.no_attachments = True

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

    attachment_mode = "포함" if not args.no_attachments else "제외"
    print(f"[upload] {len(targets)}개 리포트 → {args.dashboard_url} (첨부파일: {attachment_mode})")
    ok = 0
    fail = 0

    for report_dir in targets:
        payload = _build_payload(report_dir, repo_root)
        if payload is None:
            fail += 1
            continue
        if upload_run(payload, args.dashboard_url):
            ok += 1
            # 첨부파일 업로드
            if not args.no_attachments:
                upload_attachments(
                    report_dir,
                    payload["timestamp"],
                    args.dashboard_url,
                    blob_token,
                )
        else:
            fail += 1

    print(f"[done] 성공: {ok}, 실패: {fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
