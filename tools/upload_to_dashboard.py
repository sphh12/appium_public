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

# .env 파일 자동 로드 (python-dotenv가 있으면 사용, 없으면 수동 파싱)
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

DEFAULT_DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "https://your-dashboard.vercel.app")

# ─── AI 분석 ─────────────────────────────────────────────

def _analyze_failed_case(test_name: str, error_message: str, status_trace: str,
                         screenshot_path: str | None, page_source_path: str | None) -> str:
    """AI API로 실패한 테스트 케이스를 분석합니다.

    Returns:
        분석 결과 텍스트. API 키 미설정이나 오류 시 빈 문자열.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    gateway_key = os.environ.get("AI_GATEWAY_API_KEY", "")

    if not api_key and not gateway_key:
        return ""

    try:
        import base64

        # API 설정 (AI Gateway 우선)
        if gateway_key:
            headers = {
                "x-api-key": gateway_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            }
            url = os.environ.get("AI_GATEWAY_URL", "https://ai-gateway.vercel.sh/v1/messages")
            model = os.environ.get("AI_MODEL_GATEWAY", "anthropic/claude-sonnet-4-6")
        else:
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            }
            url = os.environ.get("AI_API_URL", "https://api.anthropic.com/v1/messages")
            model = os.environ.get("AI_MODEL", "claude-sonnet-4-6")

        # 프롬프트 구성
        prompt = f"""당신은 모바일 앱 QA 자동화 테스트 분석 전문가입니다.
아래 실패한 테스트 케이스를 분석하고, **이슈 발생 사유**와 **수정 방향**을 간결하게 한국어로 설명해주세요.

## 테스트 정보
- **테스트명**: {test_name}
- **에러 메시지**: {error_message}
"""
        if status_trace:
            prompt += f"\n## 스택 트레이스 (앞부분)\n```\n{status_trace[:1500]}\n```\n"

        # page_source 일부
        if page_source_path and os.path.isfile(page_source_path):
            try:
                with open(page_source_path, "r", encoding="utf-8") as f:
                    snippet = f.read(1000)
                prompt += f"\n## Page Source (일부)\n```xml\n{snippet}\n```\n"
            except Exception:
                pass

        prompt += """
## 요청사항
1. **이슈 발생 사유**: 왜 이 테스트가 실패했는지 (1~2문장)
2. **수정 방향**: 어떻게 수정하면 되는지 (구체적 액션, 1~3줄)

간결하게 답변해주세요."""

        content = [{"type": "text", "text": prompt}]

        # 스크린샷 이미지 추가
        if screenshot_path and os.path.isfile(screenshot_path):
            try:
                with open(screenshot_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode("utf-8")
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": img_data,
                    },
                })
                content.append({
                    "type": "text",
                    "text": "위 스크린샷은 테스트 실패 시점의 앱 화면입니다. 화면 상태도 참고하여 분석해주세요.",
                })
            except Exception:
                pass

        payload = json.dumps({
            "model": model,
            "max_tokens": 500,
            "messages": [{"role": "user", "content": content}],
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            blocks = result.get("content", [])
            texts = [b["text"] for b in blocks if b.get("type") == "text"]
            return "\n".join(texts) if texts else ""

    except Exception as e:
        print(f"    [ai] 분석 실패: {e}")
        return ""


def _find_attachment_path(results_dir: Path, result_json: dict, suffix: str) -> str | None:
    """allure result.json의 attachments에서 특정 확장자 파일 경로를 찾습니다."""
    for att in result_json.get("attachments", []):
        source = att.get("source", "")
        if source.endswith(suffix):
            path = results_dir / source
            if path.is_file():
                return str(path)
    # steps 내부 attachments도 탐색
    for step in result_json.get("steps", []):
        found = _find_attachment_path(results_dir, step, suffix)
        if found:
            return found
    return None
BLOB_API_URL = "https://blob.vercel-storage.com"
BLOB_STORAGE_LIMIT_MB = 500  # Vercel Hobby 플랜 한도
BLOB_CLEANUP_THRESHOLD = 0.8  # 80% 초과 시 정리 시작


# ─── Blob 용량 관리 함수 ─────────────────────────────────────────────

def _get_blob_usage(token: str) -> tuple[float, list[dict]]:
    """Vercel Blob의 현재 사용량(MB)과 파일 목록을 반환합니다."""
    url = f"{BLOB_API_URL}?limit=1000"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            blobs = result.get("blobs", [])
            total_bytes = sum(b.get("size", 0) for b in blobs)
            return total_bytes / (1024 * 1024), blobs
    except Exception as e:
        print(f"    [warn] Blob 사용량 조회 실패: {e}")
        return 0.0, []


def _extract_timestamp_from_blob(pathname: str) -> str:
    """Blob 경로에서 타임스탬프를 추출합니다. (예: attachments/20260221_153012/xxx → 20260221_153012)"""
    parts = pathname.strip("/").split("/")
    if len(parts) >= 2:
        candidate = parts[1]
        if _TIMESTAMP_DIR_RE.match(candidate):
            return candidate
    return ""


def _delete_blob(url: str, token: str) -> bool:
    """Vercel Blob 파일을 삭제합니다."""
    data = json.dumps({"urls": [url]}).encode("utf-8")
    req = urllib.request.Request(
        f"{BLOB_API_URL}/delete",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "x-api-version": "7",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30):
            return True
    except Exception:
        return False


def _cleanup_old_blobs(token: str, needed_mb: float = 0) -> None:
    """용량이 80%를 초과하면 가장 오래된 리포트의 첨부파일부터 삭제합니다."""
    usage_mb, blobs = _get_blob_usage(token)
    threshold_mb = BLOB_STORAGE_LIMIT_MB * BLOB_CLEANUP_THRESHOLD

    if usage_mb + needed_mb <= threshold_mb:
        return

    print(f"    [cleanup] Blob 사용량: {usage_mb:.1f}MB / {BLOB_STORAGE_LIMIT_MB}MB ({usage_mb/BLOB_STORAGE_LIMIT_MB*100:.0f}%)")

    # 타임스탬프별로 그룹화
    ts_groups: dict[str, list[dict]] = {}
    for blob in blobs:
        ts = _extract_timestamp_from_blob(blob.get("pathname", ""))
        if ts:
            ts_groups.setdefault(ts, []).append(blob)

    if not ts_groups:
        return

    # 오래된 타임스탬프 순으로 정렬
    sorted_timestamps = sorted(ts_groups.keys())

    freed_mb = 0.0
    target_mb = (usage_mb + needed_mb) - threshold_mb + 50  # 50MB 여유 확보

    for ts in sorted_timestamps:
        if freed_mb >= target_mb:
            break

        group_blobs = ts_groups[ts]
        group_size = sum(b.get("size", 0) for b in group_blobs) / (1024 * 1024)
        deleted = 0

        for blob in group_blobs:
            if _delete_blob(blob["url"], token):
                deleted += 1

        if deleted > 0:
            freed_mb += group_size
            print(f"    [cleanup] {ts}: {deleted}개 파일 삭제 ({group_size:.1f}MB 확보)")

    print(f"    [cleanup] 총 {freed_mb:.1f}MB 확보 완료")


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
    # 동일 이름 + 동일 사이즈 조합으로 내용 중복 제거 (stdout 등)
    seen_content: set[str] = set()
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
                # 동일 이름 + 동일 사이즈 중복 제거
                name = att.get("name", source)
                size = att.get("size") or file_path.stat().st_size
                content_key = f"{name}::{size}"
                if content_key in seen_content:
                    print(f"  [skip] 중복 첨부파일: {name} ({size}B)")
                    continue
                seen_sources.add(source)
                seen_content.add(content_key)
                result.append({
                    "name": name,
                    "source": source,
                    "type": att.get("type", "application/octet-stream"),
                    "size": size,
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
        # 테스트 케이스명 (stdout 파일명에 사용)
        tc_name = tc.get("name", "")
        # stdout 첨부파일에 테스트명 추가하는 래퍼
        _orig_len = len(result)
        # testStage, beforeStages, afterStages에서 첨부파일 추출
        for stage_key in ("testStage", "beforeStages", "afterStages"):
            _extract_from(tc.get(stage_key))
        # 이번 TC에서 추가된 항목 중 stdout → "stdout — 테스트명" 으로 변경
        if tc_name:
            for item in result[_orig_len:]:
                if item["name"] == "stdout":
                    item["name"] = f"stdout — {tc_name}"

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

    # 업로드 전 용량 체크 + 필요 시 오래된 파일 정리
    needed_mb = sum(a.get("size", 0) for a in attachments) / (1024 * 1024)
    _cleanup_old_blobs(blob_token, needed_mb)

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

def _extract_test_cases(report_dir: Path, analyze: bool = True) -> list[dict]:
    """allure-results의 *-result.json에서 개별 테스트 케이스 목록을 추출합니다.

    Args:
        report_dir: allure-reports/<timestamp> 경로
        analyze: True이면 failed/broken 케이스에 AI 분석 수행
    """
    # allure-results 폴더 경로 계산 (allure-reports/<ts> → allure-results/<ts>)
    results_dir = report_dir.parent.parent / "allure-results" / report_dir.name
    if not results_dir.is_dir():
        return []

    cases = []
    for f in results_dir.glob("*-result.json"):
        data = _read_json(f)
        if not data:
            continue

        # labels에서 feature, story, severity, suite 추출
        labels = {}
        for label in data.get("labels", []):
            name = label.get("name", "")
            if name in ("feature", "story", "severity", "suite", "subSuite"):
                labels[name] = label.get("value", "")

        duration_ms = 0
        start = data.get("start", 0)
        stop = data.get("stop", 0)
        if start and stop:
            duration_ms = stop - start

        status = data.get("status", "unknown")
        error_msg = (data.get("statusDetails") or {}).get("message", "")
        status_trace = (data.get("statusDetails") or {}).get("trace", "")

        # failed/broken 케이스 AI 분석
        ai_analysis = ""
        if analyze and status in ("failed", "broken") and error_msg:
            screenshot_path = _find_attachment_path(results_dir, data, ".png")
            page_source_path = _find_attachment_path(results_dir, data, ".xml")
            print(f"    [ai] {data.get('name', '')} 분석 중...")
            ai_analysis = _analyze_failed_case(
                test_name=data.get("name", ""),
                error_message=error_msg,
                status_trace=status_trace,
                screenshot_path=screenshot_path,
                page_source_path=page_source_path,
            )
            if ai_analysis:
                print(f"    [ai] 분석 완료 ({len(ai_analysis)}자)")

        cases.append({
            "uid": data.get("testCaseId") or data.get("historyId") or data.get("fullName", ""),
            "name": data.get("name", ""),
            "fullName": data.get("fullName", ""),
            "status": status,
            "durationMs": duration_ms,
            "feature": labels.get("feature", ""),
            "story": labels.get("story", ""),
            "severity": labels.get("severity", ""),
            "suite": labels.get("suite", ""),
            "statusMessage": error_msg,
            "statusTrace": status_trace,
            "description": ai_analysis,
        })

    # fullName 기준 정렬
    cases.sort(key=lambda c: c.get("fullName", ""))
    return cases


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

    # 개별 테스트 케이스 목록 추출
    test_cases = _extract_test_cases(report_dir)

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
        "testCases": test_cases,
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
