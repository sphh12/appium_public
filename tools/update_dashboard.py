import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


_TIMESTAMP_DIR_RE = re.compile(r"^\d{8}_\d{6}$")


@dataclass(frozen=True)
class RunSummary:
    timestamp: str
    report_name: str
    stats: dict[str, int]
    time: dict[str, int]
    executor: dict[str, Any]
    environment: dict[str, Any]


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _duration_ms_to_hms(duration_ms: int) -> str:
    seconds = max(0, duration_ms // 1000)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def _pick_first_list_item(data: dict[str, Any] | None) -> dict[str, Any]:
    if not data:
        return {}
    # widgets/environment.json and widgets/executors.json are usually arrays
    if isinstance(data, list):  # type: ignore[unreachable]
        return data[0] if data else {}
    return data


def _load_run_summary(report_dir: Path) -> RunSummary | None:
    summary = _read_json(report_dir / "widgets" / "summary.json")
    if not summary:
        return None

    report_name = str(summary.get("reportName") or report_dir.name)

    stats_raw = summary.get("statistic") or {}
    time_raw = summary.get("time") or {}

    stats = {
        "total": _safe_int(stats_raw.get("total"), 0),
        "passed": _safe_int(stats_raw.get("passed"), 0),
        "failed": _safe_int(stats_raw.get("failed"), 0),
        "broken": _safe_int(stats_raw.get("broken"), 0),
        "skipped": _safe_int(stats_raw.get("skipped"), 0),
        "unknown": _safe_int(stats_raw.get("unknown"), 0),
    }

    time = {
        "start": _safe_int(time_raw.get("start"), 0),
        "stop": _safe_int(time_raw.get("stop"), 0),
        "duration": _safe_int(time_raw.get("duration"), 0),
        "minDuration": _safe_int(time_raw.get("minDuration"), 0),
        "maxDuration": _safe_int(time_raw.get("maxDuration"), 0),
        "sumDuration": _safe_int(time_raw.get("sumDuration"), 0),
    }

    executors = _read_json(report_dir / "widgets" / "executors.json")
    environment = _read_json(report_dir / "widgets" / "environment.json")

    executor_first = {}
    if isinstance(executors, list):
        executor_first = executors[0] if executors else {}

    env_map: dict[str, Any] = {}
    if isinstance(environment, list):
        for item in environment:
            try:
                name = str(item.get("name"))
                value = item.get("value")
                if name:
                    env_map[name] = value
            except Exception:
                continue

    return RunSummary(
        timestamp=report_dir.name,
        report_name=report_name,
        stats=stats,
        time=time,
        executor=executor_first,
        environment=env_map,
    )


def update_dashboard(reports_root: Path) -> Path:
    dashboard_dir = reports_root / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    runs: list[RunSummary] = []
    for child in reports_root.iterdir():
        if not child.is_dir():
            continue
        if not _TIMESTAMP_DIR_RE.match(child.name):
            continue
        run = _load_run_summary(child)
        if run:
            runs.append(run)

    # Latest first
    runs.sort(key=lambda r: r.timestamp, reverse=True)

    # Build runs.json
    payload: list[dict[str, Any]] = []
    for r in runs:
        payload.append(
            {
                "timestamp": r.timestamp,
                "href": f"../{r.timestamp}/index.html",
                "reportName": r.report_name,
                "stats": r.stats,
                "time": r.time,
                "durationText": _duration_ms_to_hms(r.time.get("duration", 0)),
                "executor": {
                    "name": r.executor.get("name", ""),
                    "type": r.executor.get("type", ""),
                    "buildName": r.executor.get("buildName", ""),
                    "buildUrl": r.executor.get("buildUrl", ""),
                },
                "environment": r.environment,
            }
        )

    (dashboard_dir / "runs.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Static dashboard HTML/CSS
    (dashboard_dir / "styles.css").write_text(
        """/* Dashboard styles (local) */
:root{
  --bg:#0b1220;
  --panel:#0f1b33;
  --text:#e6edf7;
  --muted:#9bb0d0;
  --border:rgba(255,255,255,.08);
  --passed:#2fb344;
  --failed:#fa5252;
  --broken:#f08c00;
  --skipped:#868e96;
}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:linear-gradient(180deg,var(--bg),#070b14);color:var(--text)}
a{color:inherit}
.container{max-width:1200px;margin:0 auto;padding:24px}
.header{display:flex;gap:16px;align-items:flex-end;justify-content:space-between;margin-bottom:16px}
.h1{font-size:22px;font-weight:700;letter-spacing:.2px}
.sub{font-size:12px;color:var(--muted)}
.controls{display:flex;gap:10px;align-items:center}
input[type=search]{width:340px;max-width:60vw;padding:10px 12px;border-radius:10px;border:1px solid var(--border);background:rgba(255,255,255,.06);color:var(--text)}
.card{background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:14px;overflow:hidden}
.table{width:100%;border-collapse:separate;border-spacing:0}
th,td{padding:10px 12px;border-bottom:1px solid var(--border);font-size:13px;vertical-align:middle}
th{color:var(--muted);font-weight:600;text-align:left;background:rgba(255,255,255,.02)}
tr:hover td{background:rgba(255,255,255,.03)}
.badge{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;border:1px solid var(--border);font-size:12px}
.dot{width:8px;height:8px;border-radius:999px}
.dot.passed{background:var(--passed)}
.dot.failed{background:var(--failed)}
.dot.broken{background:var(--broken)}
.dot.skipped{background:var(--skipped)}
.kv{display:flex;gap:10px;flex-wrap:wrap;color:var(--muted);font-size:12px;margin:10px 0 0}
.kv span{padding:6px 10px;border:1px solid var(--border);border-radius:10px;background:rgba(255,255,255,.03)}
.small{color:var(--muted);font-size:12px}
.footer{margin-top:12px;color:var(--muted);font-size:12px}
""",
        encoding="utf-8",
    )

    (dashboard_dir / "index.html").write_text(
        """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Allure Reports Dashboard</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <div class="h1">Allure Reports Dashboard</div>
        <div class="sub">저장된 전체 실행 이력 목록. 항목 클릭 시 해당 Allure 리포트를 엽니다.</div>
        <div class="kv">
          <span>열기 팁: <code>python -m http.server 8000</code> 후 <code>/allure-reports/dashboard/</code></span>
          <span>runs.json 기반(디렉토리 자동 나열은 브라우저에서 불가)</span>
        </div>
      </div>
      <div class="controls">
        <input id="q" type="search" placeholder="검색: timestamp / buildName / 플랫폼 / git" />
      </div>
    </div>

    <div class="card">
      <table class="table" id="tbl">
        <thead>
          <tr>
            <th style="width:180px">Timestamp</th>
            <th>Build / Env</th>
            <th style="width:110px">Duration</th>
            <th style="width:90px">Total</th>
            <th style="width:90px">Failed</th>
            <th style="width:90px">Broken</th>
            <th style="width:90px">Skipped</th>
            <th style="width:90px">Passed</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>

    <div class="footer" id="meta"></div>
  </div>

<script>
  const fmt = (v) => (v === undefined || v === null) ? '' : String(v);

  function buildEnvLine(run) {
    const env = run.environment || {};
    const parts = [];
    if (env.platform) parts.push(`platform=${env.platform}`);
    if (env.deviceName) parts.push(`device=${env.deviceName}`);
    if (env.gitBranch || env.gitCommit) parts.push(`git=${fmt(env.gitBranch)}@${fmt(env.gitCommit)}`);
    return parts.join('  ·  ');
  }

  function row(run) {
    const stats = run.stats || {};
    const exe = run.executor || {};
    const build = fmt(exe.buildName) || '(no buildName)';
    const envLine = buildEnvLine(run);

    return `
      <tr>
        <td><a href="${run.href}">${run.timestamp}</a></td>
        <td>
          <div class="badge"><span class="dot ${stats.failed ? 'failed' : stats.broken ? 'broken' : stats.skipped ? 'skipped' : 'passed'}"></span>
            <span>${build}</span>
          </div>
          <div class="small">${envLine}</div>
        </td>
        <td>${fmt(run.durationText)}</td>
        <td>${fmt(stats.total)}</td>
        <td style="color:var(--failed)">${fmt(stats.failed)}</td>
        <td style="color:var(--broken)">${fmt(stats.broken)}</td>
        <td style="color:var(--skipped)">${fmt(stats.skipped)}</td>
        <td style="color:var(--passed)">${fmt(stats.passed)}</td>
      </tr>
    `;
  }

  async function main() {
    const res = await fetch('runs.json', { cache: 'no-store' });
    const runs = await res.json();

    const tbody = document.querySelector('#tbl tbody');
    const meta = document.getElementById('meta');
    const input = document.getElementById('q');

    const render = (q) => {
      const qq = (q || '').trim().toLowerCase();
      const filtered = runs.filter(r => {
        if (!qq) return true;
        const hay = [
          r.timestamp,
          (r.executor && r.executor.buildName) || '',
          (r.environment && r.environment.platform) || '',
          (r.environment && r.environment.gitBranch) || '',
          (r.environment && r.environment.gitCommit) || '',
          (r.environment && r.environment.deviceName) || ''
        ].join(' ').toLowerCase();
        return hay.includes(qq);
      });
      tbody.innerHTML = filtered.map(row).join('');
      meta.textContent = `총 ${runs.length}건 중 ${filtered.length}건 표시 · 업데이트: ${new Date().toLocaleString()}`;
    };

    input.addEventListener('input', () => render(input.value));
    render('');
  }

  main().catch(err => {
    const meta = document.getElementById('meta');
    meta.textContent = 'runs.json 로딩 실패: ' + err;
  });
</script>
</body>
</html>
""",
        encoding="utf-8",
    )

    return dashboard_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a simple dashboard for allure-reports history.")
    parser.add_argument("--reports-root", default="allure-reports", help="Allure reports root directory")
    args = parser.parse_args()

    reports_root = Path(args.reports_root)
    dashboard_dir = update_dashboard(reports_root)
    print(f"[update_dashboard] dashboard: {dashboard_dir}")
    print(f"[update_dashboard] open     : {dashboard_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
