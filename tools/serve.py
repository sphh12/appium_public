"""Allure 리포트 서버 실행 스크립트

프로젝트 루트에서 HTTP 서버를 띄워 대시보드와 리포트를 브라우저에서 볼 수 있게 합니다.

사용법:
    python tools/serve.py              # 대시보드 열기 (기본)
    python tools/serve.py --latest     # 최신 리포트 열기
    python tools/serve.py --port 9000  # 포트 변경
"""

import argparse
import http.server
import socketserver
import webbrowser
from pathlib import Path
import threading
import time
import signal
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Allure 리포트 서버를 실행합니다."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="서버 포트 (기본: 8000)",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="대시보드 대신 최신 리포트 열기",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="브라우저 자동 열기 비활성화",
    )
    parser.add_argument(
        "--reports-root",
        default="allure-reports",
        help="리포트 루트 폴더 (기본: allure-reports)",
    )

    args = parser.parse_args()

    # 프로젝트 루트로 이동 (tools/ 폴더 기준)
    project_root = Path(__file__).resolve().parent.parent
    reports_root = project_root / args.reports_root

    if not reports_root.exists():
        print(f"[ERROR] 리포트 폴더가 없습니다: {reports_root}")
        print("먼저 테스트를 실행하세요: python tools/run_allure.py -- tests/...")
        return 1

    # 열 URL 결정
    if args.latest:
        url_path = f"{args.reports_root}/LATEST/index.html"
    else:
        url_path = f"{args.reports_root}/dashboard/index.html"

    url = f"http://localhost:{args.port}/{url_path}"

    # 브라우저 열기 (서버 시작 직후)
    if not args.no_open:
        def open_browser():
            time.sleep(0.5)  # 서버가 뜰 때까지 잠깐 대기
            webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()

    # HTTP 서버 시작 (프로젝트 루트에서)
    import os
    os.chdir(project_root)

    handler = http.server.SimpleHTTPRequestHandler

    print(f"[serve] 프로젝트 루트: {project_root}")
    print(f"[serve] 서버 시작: http://localhost:{args.port}")
    print(f"[serve] 열기: {url}")
    print("[serve] 종료하려면 Enter 또는 Ctrl+C")
    print()

    try:
        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("", args.port), handler)

        # 서버를 별도 스레드에서 실행
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        # 메인 스레드에서 Enter 키 대기
        try:
            input("[serve] Enter를 누르면 서버가 종료됩니다...\n")
        except (KeyboardInterrupt, EOFError):
            pass

        print("[serve] 서버 종료 중...")
        httpd.shutdown()

    except OSError as e:
        if "Address already in use" in str(e) or "10048" in str(e):
            print(f"[ERROR] 포트 {args.port}이 이미 사용 중입니다.")
            print(f"다른 포트를 사용하세요: python tools/serve.py --port 9000")
            return 1
        raise

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
