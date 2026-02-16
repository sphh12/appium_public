# GME Remittance App - 기능 구조 리스트

> 이 문서는 자동화 테스트 코드 생성의 기준 문서입니다.
> `[미확인]` 항목은 UI 덤프 추가 캡처 후 업데이트 필요합니다.
> `[제외]` 항목은 인증/송금 등의 장벽으로 자동화 대상에서 제외합니다.

## 앱 기본 정보

- Package: `com.gmeremit.online.gmeremittance_native.stag`
- Resource ID Prefix: `com.gmeremit.online.gmeremittance_native.stag:id`
- 테스트 전제조건: 로그인 완료 상태 (Home 화면 진입)
- 앱 버전: 7.13.0 (1025) stag

---

## 하단 탭 네비게이션 (Bottom Navigation Bar)

| 순서 | 탭 이름 | Resource ID | Content-Desc |
|------|---------|-------------|--------------|
| 1 | Home | `bottom_item_home` | "Home" |
| 2 | History | `bottom_item_history` | "History" |
| 3 | Card | `bottom_item_pay` | "Card" |
| 4 | Event | `bottom_item_event` | "Event" |
| 5 | Profile | `bottom_item_profile` | "Profile" |

---

## 1. HOME 탭

### 1.1 상단 영역
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 햄버거 메뉴 | `iv_nav` | 사이드 드로어 열기 |
| 알림 | `noticeView` | Notice Board 화면 이동 |
| 알림 카운트 이미지 | `notice_count` | 알림 개수 표시 |

### 1.2 상단 알림 배너
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 알림 배너 | `rlTopNotificationView` | 알림 상세 화면 이동 |
| 왼쪽 아이콘 | `imgvLeftView` | 표시만 |
| 메시지 텍스트 | `txvMessage` | "Citibank Korea" 등 표시 |
| 카운터 | `txvCounter` | "1" 등 표시 |
| 화살표 | `imgvArrowRightTop` | 표시만 |

### 1.3 퀵 액션 (Quick Actions)
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| Wallet 아이콘 | `imgWallteIcon` | 지갑 상세 화면 이동 |
| Bank 로고 | `llBankLogo` | 은행 연결 화면 이동 |
| 원화 표시 | `txvWon` | llBankLogo 내부 |
| Bank 텍스트 | `txvBankLogoTexture` | "Bank" 표시 |
| QR 스캔 | `qrScan` | QR 코드 스캐너 열기 |
| QR 아이콘 | `qricon` | qrScan 내부 |
| QR 텍스트 | `qrtext` | "QR" 표시 |
| Reward Points | `llRewardPoints` | 리워드 포인트 화면 이동 |
| 포인트 라벨 | `txvRewardPoint` | "Reward Points: " |
| 포인트 값 | `txvRewardPointValue` | "0" 등 표시 |

### 1.4 잔액 표시 (Balance ViewPager)
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 잔액 카드 (스와이프) | `homeScreenBalancePager` | 계좌별 잔액 확인 |
| 잔액 타입 | `txvBalanceType` | "Total GME Balance" 등 표시 |
| 지갑 번호 타이틀 | `txvWalletNumberTitle` | "GME Wallet Number" |
| 지갑 번호 | `txvWalletNumber` | 지갑 번호 표시 |
| 클립보드 복사 | `txvCopyToClipBoard` | 지갑 번호 복사 |
| 잔액 | `txvBalanceValue` | 잔액 표시 |
| 잔액 표시/숨김 | `imgViewEye` | 잔액 visibility 토글 |
| Transfer 버튼 | `btnTransfer` | [제외] 송금 화면 이동 |
| Deposit 버튼 | `txvDepositOrViewStatement` | [제외] 입금 화면 이동 |

### 1.5 Easy Wallet 카드
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| Easy Wallet 카드 | `ll_easywallet_account` | Easy Wallet 가이드 화면 이동 |

### 1.6 환율 카드
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 환율 카드 | `rlExchangeRateView` | 환율 상세/송금 화면 이동 |
| 송금 통화 이미지 | `collImage` | 송금 통화 국기 |
| 송금 통화 | `collCurrency` | "KRW" |
| 송금 금액 | `txvCollAmount` | "1,000,000 KRW" |
| 환율 아이콘 | `imgvExRateImgv` | 화살표 아이콘 |
| 수취 통화 이미지 | `pImage` | 수취 통화 국기 |
| 수취 통화 | `txvPCurrency` | "CNY" |
| 수취 금액 | `txvPAmount` | "4,527 CNY" |

### 1.7 다이나믹 메뉴 (3x2 그리드)
| 순서 | 메뉴 | Resource ID | 동작 |
|------|------|-------------|------|
| 1 | Overseas Transfer | `menuRecyclerViewDynamic` 내 항목 | [제외] 해외 송금 |
| 2 | Local Transfer | `menuRecyclerViewDynamic` 내 항목 | [제외] 국내 송금 |
| 3 | Today's Rate | `menuRecyclerViewDynamic` 내 항목 | 환율 조회 화면 이동 |
| 4 | Mobile Topup & Bill Payment | `menuRecyclerViewDynamic` 내 항목 | 모바일 충전/결제 |
| 5 | Receive Overseas Funds | `menuRecyclerViewDynamic` 내 항목 | 해외 자금 수신 |
| 6 | Deposit | `menuRecyclerViewDynamic` 내 항목 | [제외] 입금 |

> 각 항목은 `image` (이미지)와 `title` (제목) 하위 요소를 포함합니다.

### 1.8 기타
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 이미지 슬라이더 (배너) | `gmeImageSlider` | 프로모션 배너 스와이프 |
| 채팅 지원 버튼 | `llChatCardView` | 고객 지원 채팅 열기 |
| 채팅 아이콘 | `imgvChat` | 채팅 아이콘 (llChatCardView 내부) |
| 메인 스크롤뷰 | `scrollViewHomeFragment` | 전체 콘텐츠 스크롤 |
| 새로고침 | `swiperefresh` | Pull-to-refresh |
| 페이지 인디케이터 | `dotsIndicator` | 잔액 페이저 페이지 표시 (3개) |

---

## 2. HISTORY 탭

> [미확인] 팝업 오버레이로 인해 실제 화면 캡처 실패. 아래 구조는 이전 분석 기반 추정.

### 2.1 상단 영역
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 화면 제목 | `txvTitle` | "History" 표시 |
| My Usage 버튼 | `usages` | [미확인] 사용 통계 화면 이동 |

### 2.2 거래 카테고리 탭 (HorizontalScrollView)
| 탭 | Content-Desc | 동작 |
|----|--------------|------|
| Overseas | "Overseas" | 해외 송금 이력 |
| Schedule History | "Schedule History" | 예약 송금 이력 |
| Domestic | "Domestic" | 국내 송금 이력 |
| Inbound | "Inbound" | 수신 이력 |

### 2.3 거래 목록
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 거래 목록 (RecyclerView) | `rvMainHistory` | 스크롤 가능한 거래 내역 |
| 날짜 필터 | `rlDate` | 기간 필터 열기 |
| 필터 아이콘 | `imgvFilter` | 필터 옵션 |
| 인쇄 버튼 | `fb_printHistory` | 거래 내역 인쇄/내보내기 |

### 2.4 거래 목록 내 카테고리 항목
| 항목 | 설명 | 동작 |
|------|------|------|
| Remittance | "Overseas / Schedule Transfer / Domestic / Inbound" | 송금 상세 화면 |
| Account | "Wallet Statement / Bank Statement" | 계좌 내역 화면 |
| GMEPay | "Statement / Purchase History" | GMEPay 내역 화면 |
| Top-up | "Domestic / International" | 충전 내역 화면 |
| Coupon Box | "Available / Used / Expired" | 쿠폰함 화면 |

---

## 3. CARD 탭

> [미확인] 팝업 오버레이로 인해 실제 화면 캡처 실패. UI 덤프 추가 캡처 필요.

| 기능 | Resource ID | 동작 |
|------|-------------|------|
| [미확인] 카드 목록 | - | 카드 관리 화면 |
| [미확인] 카드 신청 | - | 카드 신청 화면 |
| [미확인] 결제 내역 | - | 결제 이력 확인 |

---

## 4. EVENT 탭

> [미확인] 팝업 오버레이로 인해 실제 화면 캡처 실패. UI 덤프 추가 캡처 필요.

| 기능 | Resource ID | 동작 |
|------|-------------|------|
| [미확인] 이벤트 목록 | - | 진행 중인 이벤트 |
| [미확인] 이벤트 상세 | - | 이벤트 상세 정보 |

---

## 5. PROFILE 탭

> [미확인] 팝업 오버레이로 인해 프로필 메인 화면 캡처 실패. UI 덤프 추가 캡처 필요.

### 5.1 프로필 메인 화면
> [미확인] 프로필 메인 화면의 전체 구성 UI 덤프 필요

### 5.2 Edit Info 화면
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 뒤로가기 | `iv_back` | 이전 화면으로 복귀 |
| 화면 제목 | `toolbar_title` | "Edit Info" |
| 프로필 이미지 | `editProfileView` | 프로필 사진 변경 |
| 이미지 수정 버튼 | `editimage` | 이미지 편집 |
| 이름 | `fullname` | 표시만 (수정 불가 추정) |
| 전화번호 | `phoneLayout` | [미확인] 수정 화면 이동 |
| 이메일 | `emailLayout` | [미확인] 수정 화면 이동 |
| 주소 | `addressLayout` | [미확인] 수정 화면 이동 |
| 직업 | `occupationLayout` | [미확인] 수정 화면 이동 |
| 여권 | `passportLayout` | [미확인] 수정 화면 이동 |
| ARC (외국인등록증) | `arcLayout` | [미확인] 수정 화면 이동 |
| 로그인 비밀번호 변경 | `loginPasswordLayout` | [제외] 비밀번호 변경 |
| 간편 비밀번호 변경 | `simplePasswordLayout` | [제외] 간편비밀번호 변경 |

---

## 6. 햄버거 메뉴 (Side Drawer)

> 열기: Home 화면의 `iv_nav` 클릭
> Drawer Layout: `drawer_home`
> Navigation Drawer: `nav_drawer`

### 6.1 헤더 영역
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 닫기 버튼 | `iv_close` | 드로어 닫기 |
| 프로필 이미지 | `text_profile_image` | 프로필 화면 이동 |
| 사용자 이름 | `txt_user_name` | 표시만 |
| 연락처 | `txt_contact` | 표시만 |
| 이메일 | `txt_user_email` | 표시만 |

### 6.2 메뉴 항목
| 순서 | 메뉴 | Resource ID | 동작 |
|------|------|-------------|------|
| 1 | Link Bank Account | `manageAccountsViewGroup` | 연결 계좌 관리 화면 이동 |
| 2 | Inbound Account | `manageInboundAccountsViewGroup` | 수신 계좌 관리 화면 이동 |
| 3 | History | `manageHistoryViewGroup` | 거래 내역 화면 이동 |
| 4 | Branch | `view_branch` | 지점 찾기 화면 이동 |
| 5 | About GME | `view_about_gme` | 앱 정보/회사 소개 화면 이동 |
| 6 | Settings | `view_setting` | 설정 화면 이동 |
| 7 | Privacy Policy | `privacypolicy` | 개인정보 처리방침 화면 이동 |
| 8 | Terms and Conditions | `termsconditions` | 이용 약관 화면 이동 |
| 9 | Logout | `view_logout` | [제외] 로그아웃 |

### 6.3 구분선 (Dividers)
| Resource ID | 위치 |
|-------------|------|
| `manageInboundAccountsDivider` | Link Bank Account ↔ Inbound Account 사이 |
| `manageTransactionReportDivider` | Inbound Account ↔ History 사이 |
| `manageHistoryReportDivider` | History ↔ Branch 사이 |
| `branchDivider` | Branch ↔ About GME 사이 |

---

## 7. 서브 화면 (Sub-screens)

### 7.1 Notice Board (알림 화면)
> 진입: Home `noticeView` 클릭

| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 화면 제목 | - | "Notice Board" (텍스트) |
| 뒤로가기 | - | 상단 좌측 이미지 클릭 |
| Notification 탭 | - | 알림 목록 보기 (텍스트 탭) |
| Notice 탭 | - | 공지사항 목록 보기 (텍스트 탭) |
| 검색 타입 | `notice_search_type` | "Title" 등 검색 유형 선택 (Spinner) |
| 검색 입력 | `search` | 검색어 입력 (EditText) |
| 공지 목록 | `noticeViewPager` | 공지사항 목록 (ViewPager + RecyclerView) |

### 7.2 Manage Linked Bank Accounts (연결 계좌 관리)
> 진입: 햄버거 메뉴 `manageAccountsViewGroup` (Link Bank Account) 클릭

| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 화면 제목 | `toolbar_title` | "Manage Linked Bank Accounts" |
| 뒤로가기 | `iv_back` | 이전 화면 복귀 |
| 계좌 목록 | `accountListRv` | 연결된 계좌 RecyclerView |
| 은행명 | `bankNameTxtView` | 은행 이름 표시 (예: "Citibank Korea") |
| 계좌번호 | `accNo` | 마스킹된 계좌번호 표시 |
| 만료일 | `expiryDateTxtView` | 계좌 만료일 표시 |
| 갱신 상태 | `tv_verificationStatus` | "Renew" 등 상태/액션 버튼 |
| 계좌 삭제 | `iv_remove_acc` | 연결 계좌 제거 |
| 계좌 추가 | `accAddImageView` | 새 계좌 연결 화면 이동 |
| 고객센터 | `csButton` | 고객 지원 채팅 |

### 7.3 About GME (앱 정보)
> 진입: 햄버거 메뉴 `view_about_gme` 클릭

| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 뒤로가기 | - | 상단 좌측 버튼 |
| GME 로고 | - | 표시만 |
| 회사 소개 | `txvAboutUs` | 회사 설명 텍스트 |
| 앱 버전 | `txvAppversion` | "7.13.0 (1025) stag" |
| 업데이트 확인 | `btn_check_update` | "Check for Update" 버튼 |
| Facebook 링크 | `iv_fb` | Facebook 소셜 링크 |

### 7.4 Terms and Conditions (이용 약관)
> 진입: 햄버거 메뉴 `termsconditions` 클릭

| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 화면 제목 | `toolbar_title` | "Terms And Condition" |
| 뒤로가기 | `iv_back` | 이전 화면 복귀 |
| 개인정보 이용 | `personal_info_usesage` | 개인정보 이용 약관 상세 |
| 법적 동의 | `agreement_legal` | 법적 동의 약관 상세 |
| 소액 금액 | `small_scale_amount` | 소액 거래 약관 상세 |
| 오픈뱅킹 서비스 | `openbanking_service` | 오픈뱅킹 약관 상세 |
| 전자금융 | `eletronic_finance` | 전자금융 약관 상세 |
| GME Pay 약관 | `gme_pay_term` | GME Pay 약관 상세 |
| GME Card 약관 | `gme_card_term` | GME Card 약관 상세 |

### 7.5 Send Money (송금 화면)
> 진입: Home `btnTransfer` 또는 잔액 영역 Transfer 버튼
> [제외] 실제 송금 위험

| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 결제 방법 목록 | `paymentModeRV` | 결제 방법 RecyclerView (AliPay, Bank Deposit 등) |
| 보내는 금액 입력 | `sendAmountEdTxt` | "You Send" 입력 필드 |
| 받는 금액 표시 | `receiveAmountEdTxt` | "Recipient Gets" 표시 |
| 환율 표시 | `exchangeRateTxtView` | 현재 환율 |
| 수취 국가 선택 | `countrySelectionSpinner` | 수취 국가/통화 선택 |
| 수취 국기 | `recepientFlagImageView` | 국기 이미지 |
| 수취 통화 | `recepientCurrencyTextView` | 통화 코드 (CNY, USD 등) |
| 환율 상세 | `gmeExratePC` | "1 CNY = 219.76 KRW" |
| 송금 수수료 | `transferFeeTxtView` | "5,000 KRW (Transfer Fee Included)" |
| 연간 한도 | `tv_year_limit` | "Yearly Remaining Limit: 49,950 USD" |
| 보내기 버튼 | `exRateCalculateButton` | [제외] "Send" 버튼 |

### 7.6 Today's Rate (환율 조회)
> 진입: [미확인] 정확한 진입 경로 확인 필요

| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 화면 제목 | `toolbar_title` | "Today's Rate" |
| 결제 방법 | `paymentModeRV` | 결제 방법 선택 |
| 보내는 금액 | `sendAmountEdTxt` | 금액 입력 |
| 받는 금액 | `receiveAmountEdTxt` | 환산 금액 표시 |
| 환율 정보 | `ll_exchange_rate_section` | 환율 정보 섹션 |
| 환율 상세 | `ll_exRate` | 환율 상세 표시 |
| 수수료 섹션 | `ll_transfer_fee_section` | 수수료 표시 |
| 상세 컨테이너 | `ll_detailContainer` | 한도 등 상세 정보 |

### 7.7 Easy Wallet 가이드
> 진입: Home `ll_easywallet_account` 클릭

| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 화면 제목 | `screenTitle` | GMEPay/Wallet 가이드 |
| 뒤로가기 | `btnBack` | 이전 화면 복귀 |
| 입금 방법 안내 | `llHowToDeposit` | 섹션 표시 |
| 지갑 입금 가이드 | `llWalletDepositGuide` | 섹션 표시 |
| 1회 입금 한도 | `txvOneTimeLimitNote` | "500,000" |
| 최소 거래 금액 | `txvMinLimitNote` | "1,000" |
| 확인 및 신청 버튼 | `btn_submit1` | [제외] Easy Wallet 신청 |

### 7.8 송금 상세 (Remittance)
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 뒤로가기 | `iv_back` | 이전 화면 복귀 |
| 화면 제목 | `toolbar_title` | "Remittance" |
| 검색 아이콘 | `imgvSearchIcon` | 거래 검색 |
| 거래 탭 | `transactionTabLayout` | Overseas/Schedule/Domestic/Inbound 전환 |
| 거래 내역 뷰페이저 | `transactionHistoryViewPager` | 거래 목록 |

---

## 8. 팝업/모달 (앱 실행 중 발생)

> 자동화 시 팝업 처리 로직이 필요합니다.

### 8.1 In-App Banner (프로모션 팝업)
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 배너 이미지 | `bannerImageView` | 프로모션 배너 이미지 |
| 닫기 (X) | `imgvCross` | content-desc="close", 팝업 닫기 |
| 페이지 번호 | `txvPaginationView` | "1/3" 등 페이지 표시 |
| 캡션 | `txvCaption` | 프로모션 텍스트 |
| 메인 버튼 | `btnOne` | "Renew Now" 등 액션 |
| 취소 버튼 | `btnTwo` | "Cancel" 닫기 |
| 버튼 그룹 | `llButtonGroup3` | 버튼 컨테이너 |

### 8.2 Renew Auto Debit (계좌 갱신 팝업)
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 제목 | `title` | "Renew Auto Debit" |
| 설명 | `renew_desc` | 갱신 안내 텍스트 |
| 은행 로고 | `logo` | 은행 이미지 |
| 은행명 | `name` | "Citibank Korea" |
| 계좌번호 | `account` | 마스킹된 계좌번호 |
| 갱신 버튼 | `btn_okay` | "Renew Account" |
| Auto Debit 컨테이너 | `autodebit` | 메인 콘텐츠 영역 |
| 캐러셀 | `carousel` | 은행 카드 ViewPager |

### 8.3 공통 팝업 요소
| 기능 | Resource ID | 동작 |
|------|-------------|------|
| 배경 터치 | `touch_outside` | 팝업 외부 영역 클릭으로 닫기 |
| 바텀시트 | `design_bottom_sheet` | 바텀시트 컨테이너 |
| 닫기 (X) | `imgvCross` | 팝업 닫기 |
| 취소 | `btnTwo` | "Cancel" 버튼 |
| 확인 | `btnCancel` | 취소/확인 버튼 |
| 닫기 | `btn_close` | 닫기 버튼 |

---

## 제외 항목 요약 (자동화 대상에서 제외)

| 항목 | 사유 |
|------|------|
| Transfer / Send Money (`btnTransfer`, `exRateCalculateButton`) | 실제 금액 전송 위험 |
| Deposit (`txvDepositOrViewStatement`) | 실제 금액 관련 |
| Easy Wallet 신청 (`btn_submit1`) | 실제 계좌 개설 |
| 로그인/간편 비밀번호 변경 | 인증 정보 변경 위험 |
| 로그아웃 (`view_logout`) | 테스트 세션 종료 |
| Renew Account (`btn_okay`) | 실제 계좌 갱신 |

---

## 미확인 항목 요약 (UI 덤프 추가 필요)

> 원인: 로그인 후 팝업(Easy Wallet Banner, Renew Auto Debit)이 반복 발생하여
> History/Card/Event/Profile 탭의 실제 화면 캡처에 실패했습니다.
> 팝업을 완전히 닫은 후 재캡처가 필요합니다.

| 영역 | 상태 | 필요한 작업 |
|------|------|------------|
| History 탭 메인 화면 | 팝업으로 캡처 실패 | 팝업 닫기 후 재캡처 |
| Card 탭 메인 화면 | 팝업으로 캡처 실패 | 팝업 닫기 후 재캡처 |
| Event 탭 메인 화면 | 팝업으로 캡처 실패 | 팝업 닫기 후 재캡처 |
| Profile 메인 화면 | 팝업으로 캡처 실패 | 팝업 닫기 후 재캡처 |
| My Usage 화면 | 미탐색 | History `usages` 클릭 후 캡처 |
| 다이나믹 메뉴 항목 | 미탐색 | `menuRecyclerViewDynamic` 내 항목 확인 |
| Branch 화면 | 미탐색 | `view_branch` 클릭 후 캡처 |
| Settings 화면 | 미탐색 | `view_setting` 클릭 후 캡처 |
| Privacy Policy 화면 | 미탐색 | `privacypolicy` 클릭 후 캡처 |
| Inbound Account 화면 | 미탐색 | `manageInboundAccountsViewGroup` 클릭 후 캡처 |

---

## 데이터 소스

| 화면 | 캡처 파일 | 크기 |
|------|----------|------|
| Home (로그인 후) | `explore_20260216_0427/001_home_main.xml` | 105KB |
| Home (스크롤) | `explore_20260216_0427/002_home_scrolled.xml` | 90KB |
| 햄버거 메뉴 | `explore_20260216_0432/003_hamburger_menu.xml` | 142KB |
| Notice Board | `explore_20260216_0325/003_home_notice_board.xml` | 26KB |
| 연결 계좌 관리 | `explore_20260216_0325/007_menu_Citibank_Korea.xml` | 18KB |
| About GME | `explore_20260216_0325/008_menu_Apply_your_Easy_wallet_account.xml` | 17KB |
| Terms & Conditions | `explore_20260216_0325/011_menu_Total_GME_Balance.xml` | 18KB |
| Transfer | `explore_20260216_0325/012_menu_Transfer.xml` | 62KB |
| Deposit | `explore_20260216_0325/013_menu_Deposit.xml` | 62KB |
| Today's Rate | `explore_20260216_0325/015_menu_CNY.xml` | 39KB |
