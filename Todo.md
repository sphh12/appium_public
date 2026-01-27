# Todo - 해결 필요 항목

## 2026-01-27

### run-live.sh 실행 실패 (진행 중)

**현상:**
- `./shell/run-live.sh --basic_01_test` 실행 시 테스트가 시작되지만 첫 번째 테스트에서 멈춤
- 에뮬레이터/디바이스에 반응 없음
- APK 설치 또는 앱 실행 단계에서 멈추는 것으로 추정

**로그:**
```
tests/android/basic_01_test.py::TestBasic01::test_01_easy_wallet_account_elements
(여기서 멈춤)
```

**현재 APK 파일 상태:**

| 파일명 | 크기 | 형식 | 사용 가능 |
|--------|------|------|-----------|
| `[Stg]GME_7.13.0.apk` | 169MB | 단일 APK | ✅ |
| `[LiveTest]GME_7.14.0.apk` | 172MB | 단일 APK | ✅ (현재 run-live.sh에 설정) |
| `[Live]GME_7.13.3.apk+` | 137MB | Split APK (App Bundle) | ❌ 사용 불가 |

**Split APK 문제:**
- `[Live]GME_7.13.3.apk+`는 Google Play에서 다운로드된 App Bundle 형식
- 내부에 `base.apk`, `split_config.*.apk` 등 여러 파일로 분리됨
- Appium에서 직접 설치 불가

**확인 필요 사항:**
1. 디바이스/에뮬레이터 화면 상태 (잠금, 팝업 등)
2. APK 설치 권한 팝업 확인
3. USB 디버깅 권한 확인 (실물 디바이스)
4. Appium 서버 로그 확인

**해결 방안:**
1. **단기**: `[LiveTest]GME_7.14.0.apk` 또는 `[Stg]GME_7.13.0.apk`로 테스트
2. **장기**: 빌드 서버에서 Universal APK (단일 APK) 파일 요청
   - `assembleRelease` 또는 `bundletool`로 Universal APK 생성

---

### UiAutomator2 드라이버 설치 경고 (낮은 우선순위)

**현상:**
```
Error: ✖ A driver named "uiautomator2" is already installed.
[FAIL] Could not install UiAutomator2 driver
```

**원인:**
- `run-app.sh`의 드라이버 체크 로직이 "이미 설치됨"을 "설치 안됨"으로 오인

**영향:**
- 실제 동작에는 문제 없음 (이미 설치되어 있음)
- 로그에 불필요한 에러 메시지 출력

**해결 방안:**
- `run-app.sh`의 UiAutomator2 설치 체크 로직 수정 필요

---

### UnicodeDecodeError 경고 (낮은 우선순위)

**현상:**
```
UnicodeDecodeError: 'cp949' codec can't decode byte 0xeb in position 0
```

**원인:**
- Windows 환경에서 한글 등 UTF-8 문자 처리 문제
- subprocess 출력 인코딩 불일치

**영향:**
- 테스트 실행에는 영향 없음
- 로그에 경고 메시지 출력

**해결 방안:**
- 환경변수 `PYTHONIOENCODING=utf-8` 설정
- 또는 subprocess 호출 시 `encoding='utf-8'` 명시
