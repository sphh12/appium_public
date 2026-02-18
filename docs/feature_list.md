# GME Remittance 앱 기능 리스트

> **분석 일자**: 2026-02-18
> **분석 대상**: `ui_dumps/explore_20260218_2105/` (23개 XML) + 수동 캡처 8개 (`/tmp/b*.xml`)
> **앱 패키지**: `com.gmeremit.online.gmeremittance_native`
> **테스트 계정**: qa test_260205_1135 (ID: sphh)

---

## 메뉴 구조 개요

앱의 최상위 네비게이션은 **2가지**로 구분됩니다:

```
├── A. Bottom Navigation (하단 탭 5개)
│   ├── Home
│   ├── History
│   ├── Card
│   ├── Event
│   └── Profile
│
└── B. Hamburger Menu (사이드 메뉴 9개)
    ├── Link Bank Account
    ├── Inbound Account
    ├── History
    ├── Branch
    ├── About GME
    ├── Settings
    ├── Privacy Policy
    ├── Terms and Conditions
    └── Logout
```

---

# A. Bottom Navigation (하단 네비게이션)

하단 고정 탭 5개. 각 탭은 `content-desc`로 식별합니다.

| 탭 | content-desc | resource-id | UI 파일 |
|----|-------------|-------------|---------|
| Home | `Home` | `bottom_item_home` | 001~002 |
| History | `History` | `bottom_item_history` | 012~016 |
| Card | `Card` | `bottom_item_pay` | 017~019 |
| Event | `Event` | `bottom_item_event` | 020~021 |
| Profile | `Profile` | `bottom_item_profile` | 022~023 |

---

## A-1. Home (홈 화면)

**Activity**: `.homeV2.view.HomeActivityV2`
**UI 파일**: 001_home_main.xml, 002_home_scrolled.xml

### 상단 정보 영역
| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| A1-1 | GME Wallet 잔액 | 잔액 표시 (예: 11,182 KRW) | `tv_wallet_amount` |
| A1-2 | Wallet 계좌번호 | GME Wallet 번호 (9424014433185) | `tv_wallet_id` |
| A1-3 | Transfer 버튼 | 송금 화면 이동 | `btn_gme_wallet_transfer` |
| A1-4 | Deposit 버튼 | 입금 화면 이동 | `btn_gme_wallet_deposit` |

### 빠른 메뉴 (Dynamic Menu Grid)
| # | 메뉴 | 영문명 | 스크롤 |
|---|------|--------|--------|
| A1-5 | 해외 송금 | Overseas Transfer | 상단 |
| A1-6 | 국내 송금 | Local Transfer | 상단 |
| A1-7 | 오늘의 환율 | Today's Rate | 상단 |
| A1-8 | 모바일 충전 | Mobile Topup | 상단 |
| A1-9 | 해외 수금 | Receive Overseas Funds | 스크롤 |
| A1-10 | 입금 | Deposit | 스크롤 |
| A1-11 | ATM 출금 | ATM Withdrawal | 스크롤 |
| A1-12 | 월렛 내역 | GME Wallet Statement | 스크롤 |
| A1-13 | 통신 서비스 | Telecom Services | 스크롤 |
| A1-14 | 증명서 발급 | Issue Certificate | 스크롤 |
| A1-15 | 예약 | Booking | 스크롤 |

---

## A-2. History (거래 내역)

**Activity**: `.homeV2.view.HomeActivityV2` (탭 전환)
**UI 파일**: h1~h6 (수동 캡처)

> **참고**: 자동 탐색 파일(012~016)은 잘못 캡처됨. 수동 캡처 파일(h1~h6)이 정확한 데이터입니다.

### 카테고리 목록
| # | 카테고리 | 서브탭 | UI 파일 |
|---|----------|--------|---------|
| A2-1 | Remittance (송금) | Overseas / Schedule History / Domestic / Inbound | h1_remittance.xml |
| A2-2 | Account (계좌) | Wallet Statement / Bank Statement | h2_account.xml |
| A2-3 | GME Pay | All / Card Expenses / Purchase History | h3_gmepay.xml |
| A2-4 | Top-up (충전) | Domestic / International | h4_topup.xml |
| A2-5 | Coupon Box (쿠폰) | Available / Used / Expired | h5_coupon.xml |
| A2-6 | Reward Point (리워드) | All / Issued / Used | h6_reward.xml |

### A2-1. Remittance (송금 내역)
**화면 타이틀**: Remittance

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| A2-1-1 | 뒤로가기 | 이전 화면 복귀 | `iv_back` |
| A2-1-2 | 검색 | 거래 내역 검색 | `imgvSearchIcon` |
| A2-1-3 | 날짜 필터 | 기간 선택 (기본: 3개월) | `filterView` |
| A2-1-4 | 필터 버튼 | 상세 필터 | `imgvFilter` |
| A2-1-5 | 거래 목록 | 송금 내역 리스트 (스크롤) | `transactionHistoryRv` |
| A2-1-6 | 인쇄 | 내역 인쇄 버튼 | `fb_printHistory` |

### A2-2. Account (계좌 내역)
**화면 타이틀**: Account

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| A2-2-1 | Wallet 번호 | 월렛 계좌번호 표시 | 정보 영역 |
| A2-2-2 | Balance | 잔액 표시 (예: 0 KRW) | 잔액 영역 |
| A2-2-3 | 날짜/카테고리 필터 | 기간 + 카테고리 선택 (기본: 6개월/ALL) | `filterView`, `imgvFilter` |
| A2-2-4 | 거래 목록 | 입출금 내역 리스트 | `walletStatementHistoryRv` |
| A2-2-5 | 다운로드 | 내역 다운로드 버튼 | `download` |

### A2-3. GME Pay (GMEPay 내역)
**화면 타이틀**: GME Pay

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| A2-3-1 | Balance | 잔액 표시 (예: 11,182 KRW) | 잔액 영역 |
| A2-3-2 | 날짜 필터 | 기간 선택 (기본: 3개월) | `rlDate`, `imgvFilter` |
| A2-3-3 | 거래 목록 | GMEPay 내역 리스트 | `rvGmePayStatement` |

### A2-4. Top-up (충전 내역)
**화면 타이틀**: Top-up

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| A2-4-1 | 날짜 필터 | 기간 선택 (기본: 3개월) | `filterView`, `imgvFilter` |
| A2-4-2 | 거래 목록 | 충전 내역 리스트 | RecyclerView |

### A2-5. Coupon Box (쿠폰함)
**화면 타이틀**: Coupon Box

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| A2-5-1 | 쿠폰 카테고리 | Gift Coupon / Service Coupon 분류 | RecyclerView |
| A2-5-2 | 카테고리 이미지 | 쿠폰 종류 아이콘 | `imgvCategoryImage` |
| A2-5-3 | 보유 개수 | 각 카테고리별 쿠폰 수 | `txvItemCount` |

### A2-6. Reward Point (리워드 포인트)
**화면 타이틀**: Reward Point

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| A2-6-1 | My Reward Points | 보유 포인트 표시 (예: 0 P) | 포인트 영역 |
| A2-6-2 | 만료 예정 포인트 | 30일 내 만료 포인트 표시 | 만료 영역 |
| A2-6-3 | 날짜 필터 | 기간 선택 (기본: 3개월) | `rlDate` |
| A2-6-4 | 거래 목록 | 포인트 적립/사용 내역 | RecyclerView |
| A2-6-5 | Go to GME Shop | GME 쇼핑몰 이동 버튼 | `llGoToShop` |
| A2-6-6 | CS 버튼 | 고객지원 플로팅 버튼 | `fab_cs` |

---

## A-3. Card (GME 카드)

**Activity**: `.homeV2.view.GMECardOwnerActivity`
**UI 파일**: 017~019

### 카드 메인
| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| A3-1 | 카드 잔액 표시 | GME Card 잔액 (예: 11,182 KRW) | `tv_wallet_amount` |
| A3-2 | Transfer | 카드 송금 | `btn_gme_wallet_transfer` |
| A3-3 | Deposit | 카드 입금 | `btn_gme_wallet_deposit` |

### Card Management (카드 관리)
| # | 기능 | 설명 | UI 파일 |
|---|------|------|---------|
| A3-4 | View Benefits | 카드 혜택 보기 | 018, 019 |
| A3-5 | Card Number Details | 카드 번호 상세 | 019 |
| A3-6 | Change PIN | 카드 PIN 변경 | 019 |
| A3-7 | Pause | 카드 일시정지 | 019 |
| A3-8 | Automatic Recharge | 자동 충전 설정 | 019 |

---

## A-4. Event (이벤트)

**Activity**: `.homeV2.view.HomeActivityV2` (탭 전환)
**UI 파일**: 020~021

| # | 기능 | 설명 | UI 파일 |
|---|------|------|---------|
| A4-1 | Ongoing 탭 | 진행 중인 이벤트 목록 | 020 |
| A4-2 | Past Events 탭 | 종료된 이벤트 목록 | 020 |
| A4-3 | Affordable Plan! | 요금 프로모션 (2025-06-06 ~ 2026-12-31) | 020 |
| A4-4 | Spin & Win | 포인트 룰렛 (최대 30,000pt) | 021 |

---

## A-5. Profile (프로필)

**Activity**: `.homeV2.view.HomeActivityV2` (탭 전환)
**UI 파일**: 022~023

### 사용자 정보
| # | 기능 | 설명 | UI 파일 |
|---|------|------|---------|
| A5-1 | 사용자 이름/ID | 이름, ID 표시 | 022 |
| A5-2 | 누적 송금 금액 | Total Amount (예: 110,298 KRW) | 022 |
| A5-3 | 누적 송금 횟수 | Total Count (예: 35회) | 022 |

### 프로필 메뉴
| # | 메뉴 | 설명 | UI 파일 |
|---|------|------|---------|
| A5-4 | Reward Points | 리워드 포인트 | 022 |
| A5-5 | Auto Debit Account | 자동이체 계좌 | 022 |
| A5-6 | Saved Receivers | 저장된 수취인 관리 | 022 |
| A5-7 | My Documents | 내 서류 관리 | 023 |
| A5-8 | Invite Friend | 친구 초대 | 023 |
| A5-9 | Customer Support | 고객 지원 | 023 |

---

# B. Hamburger Menu (햄버거 사이드 메뉴)

좌측 상단 메뉴 버튼(`iv_nav`)으로 열리는 네비게이션 드로어.
**UI 파일**: 003_hamburger_menu.xml, 004_hamburger_menu_scrolled.xml

### 드로어 상단 - 사용자 정보
| 항목 | 예시 값 | Resource ID |
|------|---------|-------------|
| 사용자 이름 | qa test_260205_1135 | `tv_user_name` |
| 이메일 | philiph@gmeremit.com | `tv_user_email` |
| Wallet 번호 | 9424014433185 | `txvWalletNumber` |
| Total Balance | 1,457,010 KRW / 1,000 USD | `txvBalanceValue` |
| Reward Points | 11,182 | `txvRewardPointValue` |

### 드로어 메뉴 항목 (9개)

| # | 메뉴 | Resource ID | UI 파일 |
|---|------|-------------|---------|
| B-1 | Link Bank Account | `manageAccountsViewGroup` | b1_link_bank.xml |
| B-2 | Inbound Account | `manageInboundAccountsViewGroup` | b2_inbound.xml |
| B-3 | History | `manageHistoryViewGroup` | 006 |
| B-4 | Branch | `view_branch` | b4_branch.xml |
| B-5 | About GME | `view_about_gme` | b5_about.xml |
| B-6 | Settings | `view_setting` | b6_settings.xml |
| B-7 | Privacy Policy | `privacypolicy` | b7_privacy.xml |
| B-8 | Terms and Conditions | `termsconditions` | b8_terms.xml |
| B-9 | Logout | `view_logout` | b9_logout.xml |

---

## B-1. Link Bank Account (연결 은행 계좌 관리)

**화면 타이틀**: Manage Linked Bank Accounts
**UI 파일**: b1_link_bank.xml

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| B1-1 | 뒤로가기 | 이전 화면 복귀 | `iv_back` |
| B1-2 | 연결 계좌 목록 | 등록된 은행 계좌 리스트 | `accountListRv` |
| B1-3 | 계좌 상태 표시 | Main Account / Confirmation Pending / Enter Verification Number | 각 계좌 항목 |
| B1-4 | 계좌 제거 | 계좌 삭제 버튼 (X) | `iv_remove_acc` |
| B1-5 | 계좌 추가 | Register Bank Account 버튼 | `accAddImageView` |
| B1-6 | 고객 서비스 | CS 버튼 (우측 하단) | `csButton` |

### 등록된 계좌 예시
| 은행 | 계좌번호 | 상태 | 만료일 |
|------|----------|------|--------|
| Industrial Bank of Korea (IBK) | 2220*****0 | Main Account | 2031-01-20 |
| Nonghyup Bank (NH) | 3120*****1 | Confirmation Pending | 2031-02-05 |
| Woori Bank | 1002*****8 | Enter Verification Number | - |
| Toss Bank | 1000*****9 | Enter Verification Number | - |

---

## B-2. Inbound Account (수금 계좌 관리)

**화면 타이틀**: Manage Inbound Account
**UI 파일**: b2_inbound.xml

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| B2-1 | 뒤로가기 | 이전 화면 복귀 | `iv_back` |
| B2-2 | GME Wallet | 월렛 정보 (수금 한도: 100만원) | `gmewallet` |
| B2-3 | Primary Account | 주계좌 표시 (IBK) | `primary` |
| B2-4 | Inbound 계좌 목록 | 수금 계좌 리스트 | `accountListRv` |
| B2-5 | 계좌 삭제 | 수금 계좌 제거 버튼 | `iv_delete_inbound` |
| B2-6 | 계좌 추가 | 수금 계좌 등록 버튼 | `accAddImageView` |

### 등록된 수금 계좌
| 구분 | 은행 | 계좌번호 |
|------|------|----------|
| Primary | Industrial Bank of Korea (IBK) | 22208803201010 |
| Inbound | Nonghyup Bank (NH) | 3120188942501 |
| Inbound | Woori Bank | 1002648819368 |

---

## B-3. History (거래 내역 메뉴)

**캡처 상태**: 캡처 완료
**UI 파일**: 006_menu_History_Menu.xml

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| B3-1 | MY USAGE 탭 | 사용 내역 탭 | `usages` |
| B3-2 | 카테고리 리스트 | 거래 내역 RecyclerView | `rvMainHistory` |

### 카테고리 목록 (7개)
| # | 카테고리 | 서브 항목 |
|---|----------|-----------|
| B3-3 | Remittance | Overseas / Schedule Transfer / Domestic / Inbound |
| B3-4 | Account | Wallet Statement / Bank Statement |
| B3-5 | Reward Point | - |
| B3-6 | Card | Statement / Purchase History |
| B3-7 | GMEPay | - |
| B3-8 | Top-up | Domestic / International |
| B3-9 | Coupon Box | Available / Used / Expired |

> **참고**: Bottom Nav의 History(A-2)와 진입 방식이 다름. 햄버거 History는 카테고리 선택 메뉴 형태이고,
> 각 카테고리를 클릭하면 A-2의 각 서브 화면(h1~h6)과 동일한 화면으로 이동합니다.

---

## B-4. Branch (지점 안내)

**화면 타이틀**: Branch
**UI 파일**: b4_branch.xml

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| B4-1 | 뒤로가기 | 이전 화면 복귀 | `iv_back` |
| B4-2 | 지점 목록 | 지점 리스트 (스크롤) | `agentListRv` |
| B4-3 | 지점명 | 지점 이름 표시 | `branch_name` |
| B4-4 | 영업 상태 | OPEN / CLOSED 표시 | 상태 텍스트 |
| B4-5 | 주소 (영문) | 영문 주소 + COPY 버튼 | `branch_address` |
| B4-6 | 주소 (한글) | 한글 주소 | 한글 주소 텍스트 |
| B4-7 | 전화번호 | 지점 전화 (클릭 시 전화) | `tv_phone_number` |
| B4-8 | 영업 시간 | 운영 시간 표시 | `tv_time` |
| B4-9 | Naver Map | 네이버 지도 링크 | `naver_map_link` |
| B4-10 | Kakao Map | 카카오 지도 링크 | `kakao_map_link` |
| B4-11 | Google Map | 구글 지도 링크 | `google_map_link` |
| B4-12 | iOS Map | iOS 지도 링크 | `ios_map_link` |

### 지점 예시
| 지점명 | 주소 | 전화 | 상태 |
|--------|------|------|------|
| ANSAN | 6 Damunhwa-gil, Danwon-gu, Ansan-si | 031-492-1247 | CLOSED |
| BUPYEONG | 16 Gwangjang-ro, Bupyeong-gu, Incheon | 032-361-0875 | CLOSED |

---

## B-5. About GME (회사 소개)

**화면 타이틀**: About GME
**UI 파일**: b5_about.xml

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| B5-1 | 뒤로가기 | 이전 화면 복귀 (content-desc: "GME Remit") | `iv_back` |
| B5-2 | 회사 소개 텍스트 | Non-Bank Remittance Service Provider 설명 | `txvAboutUs` |
| B5-3 | 앱 버전 | 현재 버전 표시 (예: 7.14.0 (1030)) | `txvAppversion` |
| B5-4 | 업데이트 확인 | Check for Update 버튼 | `btn_check_update` |
| B5-5 | Facebook 링크 | 소셜 미디어 링크 | `iv_fb` |

---

## B-6. Settings (설정)

**화면 타이틀**: Settings
**UI 파일**: b6_settings.xml

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| B6-1 | Change Login Password | 로그인 비밀번호 변경 | `view_change_password` |
| B6-2 | Change Simple Password | 간편 비밀번호(PIN) 변경 | `view_change_pin_code` |
| B6-3 | Receive Marketing Push | 마케팅 푸시 수신 동의 (토글, 기본: OFF) | `view_marketing` |
| B6-4 | Language | 앱 언어 설정 | `view_language` |
| B6-5 | Delete GME Account | GME 계정 삭제 | `delete_gme_account` |

---

## B-7. Privacy Policy (개인정보 처리방침)

**화면 타이틀**: Personal Information Treatment Policy
**UI 파일**: b7_privacy.xml
**형태**: Native ScrollView (WebView 아님)

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| B7-1 | 약관 본문 | 개인정보 처리방침 전문 (스크롤) | 본문 텍스트 |
| B7-2 | More 버튼 | 추가 내용 보기 | `more` |

---

## B-8. Terms and Conditions (이용약관)

**화면 타이틀**: Terms and Condition
**UI 파일**: b8_terms.xml
**형태**: Native ScrollView (약관 항목 리스트)

| # | 약관 항목 | Resource ID |
|---|-----------|-------------|
| B8-1 | Personal Information Collection and Usage Agreement | `personal_info_usesage` |
| B8-2 | Agreement of Legal Name Confirmation | `agreement_legal` |
| B8-3 | Terms of Use for Small Amount Overseas Remittance | `small_scale_amount` |
| B8-4 | Terms of Use for Open-Banking Service | `openbanking_service` |
| B8-5 | Terms of Use for Electronic Finance Transaction | `eletronic_finance` |
| B8-6 | Terms and Condition for GMEPAY | `gme_pay_term` |
| B8-7 | Terms and Condition for GME CARD | `gme_card_term` |

---

## B-9. Logout (로그아웃)

**화면 타이틀**: Logout (확인 팝업)
**UI 파일**: b9_logout.xml

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| B9-1 | 팝업 타이틀 | "Logout" | `txt_dialog_title` |
| B9-2 | 팝업 메시지 | "Would you like to logout?" | `messageBodyTxtView` |
| B9-3 | No 버튼 | 로그아웃 취소 | `btnLater` |
| B9-4 | Yes 버튼 | 로그아웃 확인 | `btnRenew` |

---

# C. 공통 요소

| # | 기능 | 설명 | Resource ID |
|---|------|------|-------------|
| C-1 | Simple Password 잠금 | 4자리 PIN 잠금화면 (앱 시작 시) | `input_dot_1`~`input_dot_4` |
| C-2 | Connection Failed 팝업 | 인터넷 연결 실패 에러 팝업 | `btn_diaog_ok` |
| C-3 | 알림 버튼 | 상단 알림 아이콘 | `noticeView` |
| C-4 | 햄버거 메뉴 버튼 | 좌측 상단 사이드 메뉴 열기 | `iv_nav` |
| C-5 | QR 스캔 | QR 코드 스캔 | `qrScan` |
| C-6 | 환율 카드 | 오늘의 환율 정보 | `rlExchangeRateView` |

---

# D. 화면 구조 매핑 (Activity)

| 화면 | Activity 클래스 | 비고 |
|------|-----------------|------|
| Home | `.homeV2.view.HomeActivityV2` | 메인 Activity |
| History | `.homeV2.view.HomeActivityV2` | 탭 전환 |
| Card | `.homeV2.view.GMECardOwnerActivity` | 별도 Activity |
| Event | `.homeV2.view.HomeActivityV2` | 탭 전환 |
| Profile | `.homeV2.view.HomeActivityV2` | 탭 전환 |

---

# E. UI 덤프 파일 목록

### 자동 탐색 (`ui_dumps/explore_20260218_2105/`)
| 파일 | 설명 | 캡처 상태 |
|------|------|-----------|
| 001_home_main.xml | Home 화면 (상단) | 정상 |
| 002_home_scrolled.xml | Home 화면 (스크롤) | 정상 |
| 003_hamburger_menu.xml | 햄버거 메뉴 (상단) | 정상 |
| 004_hamburger_menu_scrolled.xml | 햄버거 메뉴 (스크롤) | 정상 |
| 005_menu_Inbound_Account.xml | ~~Inbound Account~~ | 잘못 캡처 (홈 화면) |
| 006_menu_History_Menu.xml | History 메뉴 | 정상 |
| 007_menu_Branch.xml | ~~Branch~~ | 잘못 캡처 (홈 화면) |
| 008_menu_About_GME.xml | ~~About GME~~ | 잘못 캡처 (홈 화면) |
| 009_menu_Settings.xml | ~~Settings~~ | 잘못 캡처 (홈 화면) |
| 010_menu_Privacy_Policy.xml | ~~Privacy Policy~~ | 잘못 캡처 (드로어 상태) |
| 011_menu_Terms_and_Conditions.xml | ~~Terms and Conditions~~ | 잘못 캡처 (드로어 상태) |
| 012_history_main.xml | ~~History - Remittance~~ | 잘못 캡처 (홈 화면) |
| 013_history_cat_Account.xml | ~~History - Account~~ | 잘못 캡처 (홈 화면) |
| 014_history_cat_GMEPay.xml | ~~History - GMEPay~~ | 잘못 캡처 (History 메뉴) |
| 015_history_cat_Top_up.xml | ~~History - Top-up~~ | 잘못 캡처 (History 메뉴) |
| 016_history_cat_Coupon_Box.xml | ~~History - Coupon Box~~ | 잘못 캡처 (History 메뉴) |
| 017_card_main.xml | Card 화면 (상단) | 정상 |
| 018_card_scrolled.xml | Card 화면 (스크롤) | 정상 |
| 019_card_Card_Management.xml | Card Management | 정상 |
| 020_event_main.xml | Event 화면 (상단) | 정상 |
| 021_event_scrolled.xml | Event 화면 (스크롤) | 정상 |
| 022_profile_main.xml | Profile 화면 (상단) | 정상 |
| 023_profile_scrolled.xml | Profile 화면 (스크롤) | 정상 |

### 수동 캡처 (`/tmp/`)
| 파일 | 설명 | 캡처 상태 |
|------|------|-----------|
| b1_link_bank.xml | Manage Linked Bank Accounts | 정상 |
| b2_inbound.xml | Manage Inbound Account | 정상 |
| b4_branch.xml | Branch 지점 안내 | 정상 |
| b5_about.xml | About GME 회사 소개 | 정상 |
| b6_settings.xml | Settings 설정 | 정상 |
| b7_privacy.xml | Privacy Policy 개인정보 처리방침 | 정상 |
| b8_terms.xml | Terms and Conditions 이용약관 | 정상 |
| b9_logout.xml | Logout 확인 팝업 | 정상 |
| h1_remittance.xml | History - Remittance 송금 내역 | 정상 |
| h2_account.xml | History - Account 계좌 내역 | 정상 |
| h3_gmepay.xml | History - GME Pay 내역 | 정상 |
| h4_topup.xml | History - Top-up 충전 내역 | 정상 |
| h5_coupon.xml | History - Coupon Box 쿠폰함 | 정상 |
| h6_reward.xml | History - Reward Point 리워드 | 정상 |
