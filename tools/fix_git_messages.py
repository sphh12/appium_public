# -*- coding: utf-8 -*-
"""대시보드 DB의 깨진 gitMessage를 일괄 수정하는 스크립트"""
import json
import urllib.request

BASE = "https://your-dashboard.vercel.app/api/runs"

# commit별 올바른 메시지
COMMIT_MESSAGES = {
    "964c381": "docs: 상태줄 설정 작업 기록 추가",
    "cf2e30b": "chore: .gitignore - .claude/ 디렉토리 Git 추적 제외",
    "3050be6": "feat: upload_to_dashboard.py - Blob 첨부파일 업로드 추가 / run_allure.py - 업로드 기본 활성화",
    "1b27f67": "feat: language.py - 앱 언어 설정 모듈 추가 / auth.py - 로그인 전 영어 설정 통합",
}

# timestamp → commit 매핑
TS_COMMIT = {
    "20260224_045531": "964c381",
    "20260224_042905": "964c381",
    "20260224_042450": "964c381",
    "20260223_111737": "964c381",
    "20260222_012832": "cf2e30b",
    "20260221_230059": "3050be6",
    "20260216_024413": "1b27f67",
    "20260216_024303": "1b27f67",
    "20260216_024155": "1b27f67",
    "20260216_024149": "1b27f67",
    "20260216_023915": "1b27f67",
    "20260216_023835": "1b27f67",
    "20260216_023828": "1b27f67",
    "20260216_023759": "1b27f67",
    "20260216_023702": "1b27f67",
    "20260216_023521": "1b27f67",
    "20260216_023254": "1b27f67",
    "20260216_022901": "1b27f67",
    "20260216_020551": "1b27f67",
    "20260216_015105": "1b27f67",
    "20260214_102239": "1b27f67",
    "20260214_102025": "1b27f67",
    "20260214_101308": "1b27f67",
    "20260214_101243": "1b27f67",
    "20260214_101038": "1b27f67",
}

def patch_run(timestamp, message):
    """PATCH API로 gitMessage 업데이트"""
    url = f"{BASE}/{timestamp}"
    payload = json.dumps({"gitMessage": message}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="PATCH")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("gitMessage", "")
    except Exception as e:
        return f"ERROR: {e}"

if __name__ == "__main__":
    print(f"총 {len(TS_COMMIT)}개 run 수정 시작\n")
    success = 0
    for ts, commit in TS_COMMIT.items():
        msg = COMMIT_MESSAGES[commit]
        result = patch_run(ts, msg)
        status = "OK" if result == msg else "FAIL"
        if status == "OK":
            success += 1
        print(f"[{status}] {ts} | {commit[:7]} | {result[:50]}")
    print(f"\n완료: {success}/{len(TS_COMMIT)} 성공")
