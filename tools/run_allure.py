import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _find_latest_timestamp_dir(root: Path) -> Path | None:
    if not root.exists():
        return None
    dirs = [p for p in root.iterdir() if p.is_dir()]
    if not dirs:
        return None
    # Timestamp folder names sort lexicographically in chronological order (YYYYMMDD_HHMMSS)
    return sorted(dirs, key=lambda p: p.name)[-1]


def _copy_history(previous_report_dir: Path, results_dir: Path) -> None:
    src = previous_report_dir / "history"
    dst = results_dir / "history"
    if not src.exists() or not src.is_dir():
        return
    if dst.exists():
        shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "pytest 실행 결과를 날짜/시간별 Allure 결과/리포트로 저장합니다. "
            "예) allure-results/20260119_153012, allure-reports/20260119_153012"
        )
    )
    parser.add_argument(
        "--results-root",
        default="allure-results",
        help="Allure results 루트 폴더(하위에 timestamp 폴더 생성)",
    )
    parser.add_argument(
        "--reports-root",
        default="allure-reports",
        help="Allure report 루트 폴더(하위에 timestamp 폴더 생성)",
    )
    parser.add_argument(
        "--keep-history",
        action="store_true",
        default=True,
        help="이전 실행의 트렌드(history)를 다음 리포트에 이어붙임 (기본: 켜짐)",
    )
    parser.add_argument(
        "--no-history",
        dest="keep_history",
        action="store_false",
        help="트렌드(history) 이어붙임 끄기",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        default=False,
        help="리포트 생성 후 allure open 실행",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="pytest 인자들 (예: -- tests/test_01.py -v --platform=android)",
    )

    args = parser.parse_args()

    pytest_args = list(args.pytest_args)
    if pytest_args and pytest_args[0] == "--":
        pytest_args = pytest_args[1:]
    if not pytest_args:
        print("pytest 인자가 없습니다. 예: python tools/run_allure.py -- tests/test_01.py -v --platform=android")
        return 2

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(args.results_root) / timestamp
    report_dir = Path(args.reports_root) / timestamp

    results_dir.mkdir(parents=True, exist_ok=False)
    report_dir.parent.mkdir(parents=True, exist_ok=True)

    if args.keep_history:
        previous_report_dir = _find_latest_timestamp_dir(Path(args.reports_root))
        if previous_report_dir is not None and previous_report_dir.name != timestamp:
            _copy_history(previous_report_dir, results_dir)

    env = os.environ.copy()

    pytest_cmd = [sys.executable, "-m", "pytest", *pytest_args, "--alluredir", str(results_dir)]
    print("[run_allure] pytest:", " ".join(pytest_cmd))
    pytest_proc = subprocess.run(pytest_cmd, env=env)

    allure_generate_cmd = [
        "allure",
        "generate",
        str(results_dir),
        "-o",
        str(report_dir),
        "--clean",
    ]
    print("[run_allure] allure generate:", " ".join(allure_generate_cmd))
    subprocess.run(allure_generate_cmd, env=env, check=True)

    latest_file = Path(args.reports_root) / "LATEST.txt"
    latest_file.write_text(f"{timestamp}\n", encoding="utf-8")

    print(f"[run_allure] results: {results_dir}")
    print(f"[run_allure] report  : {report_dir}")

    if args.open:
        allure_open_cmd = ["allure", "open", str(report_dir)]
        print("[run_allure] allure open:", " ".join(allure_open_cmd))
        subprocess.run(allure_open_cmd, env=env, check=False)

    return int(pytest_proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
