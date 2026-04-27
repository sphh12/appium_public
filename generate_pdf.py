# -*- coding: utf-8 -*-
"""
Appium 환경 구성 가이드 PDF 생성
"""
from fpdf import FPDF
import os

# 프로젝트 루트 경로 자동 계산
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        font_path = "C:/Windows/Fonts/malgun.ttf"
        font_bold_path = "C:/Windows/Fonts/malgunbd.ttf"
        if os.path.exists(font_path):
            self.add_font("Malgun", "", font_path)
            self.add_font("Malgun", "B", font_bold_path)
            self.korean_font = "Malgun"
        else:
            self.korean_font = "Helvetica"

    def header(self):
        self.set_font(self.korean_font, "B", 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "Appium 모바일 자동화 테스트 환경 구성 가이드", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.korean_font, "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"- {self.page_no()} -", align="C")

    def chapter_title(self, title):
        self.set_font(self.korean_font, "B", 14)
        self.set_text_color(30, 80, 150)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def section_title(self, title):
        self.set_font(self.korean_font, "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font(self.korean_font, "", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def code_block(self, code):
        self.set_font(self.korean_font, "", 9)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, code, fill=True)
        self.ln(3)

    def bullet_point(self, text):
        self.set_font(self.korean_font, "", 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, f"    - {text}", new_x="LMARGIN", new_y="NEXT")

    def numbered_item(self, number, text):
        self.set_font(self.korean_font, "", 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, f"    {number}. {text}", new_x="LMARGIN", new_y="NEXT")

    def tip_box(self, text):
        self.set_font(self.korean_font, "", 9)
        self.set_fill_color(255, 250, 230)
        self.set_text_color(100, 80, 0)
        self.multi_cell(0, 6, f"[TIP] {text}", fill=True)
        self.ln(2)

    def warning_box(self, text):
        self.set_font(self.korean_font, "", 9)
        self.set_fill_color(255, 235, 235)
        self.set_text_color(150, 50, 50)
        self.multi_cell(0, 6, f"[주의] {text}", fill=True)
        self.ln(2)

    def table_row(self, col1, col2, header=False):
        if header:
            self.set_font(self.korean_font, "B", 10)
            self.set_fill_color(220, 230, 240)
        else:
            self.set_font(self.korean_font, "", 10)
            self.set_fill_color(250, 250, 250)
        self.set_text_color(0, 0, 0)
        self.cell(60, 8, col1, border=1, fill=True)
        self.cell(0, 8, col2, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    def table_row3(self, col1, col2, col3, header=False):
        if header:
            self.set_font(self.korean_font, "B", 9)
            self.set_fill_color(220, 230, 240)
        else:
            self.set_font(self.korean_font, "", 9)
            self.set_fill_color(250, 250, 250)
        self.set_text_color(0, 0, 0)
        self.cell(45, 8, col1, border=1, fill=True)
        self.cell(50, 8, col2, border=1, fill=True)
        self.cell(0, 8, col3, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")


def create_pdf():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ========== 표지 ==========
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font(pdf.korean_font, "B", 32)
    pdf.set_text_color(30, 80, 150)
    pdf.cell(0, 15, "Appium", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font(pdf.korean_font, "B", 20)
    pdf.cell(0, 12, "모바일 자동화 테스트", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 12, "환경 구성 가이드", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    pdf.set_font(pdf.korean_font, "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Android + iOS 크로스 플랫폼 테스트 환경", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Python + pytest 기반", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(25)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(10)
    pdf.set_font(pdf.korean_font, "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, "초보자도 쉽게 따라할 수 있는 단계별 가이드", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font(pdf.korean_font, "", 10)
    pdf.cell(0, 8, "작성일: 2026-01-05", align="C", new_x="LMARGIN", new_y="NEXT")

    # ========== 목차 ==========
    pdf.add_page()
    pdf.chapter_title("목차")
    pdf.ln(5)
    pdf.set_font(pdf.korean_font, "", 11)
    pdf.cell(0, 8, "1. Appium이란?", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "2. 설치 명령어 (환경 구성 단계)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "3. 설치된 구성 요소", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "4. 프로젝트 폴더 구조", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "5. 설정 파일 상세 설명", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "6. 테스트 실행 방법 (단계별 가이드)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "7. 테스트 코드 작성 방법", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "8. 사전 준비 사항", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "9. 자주 발생하는 문제와 해결 방법", new_x="LMARGIN", new_y="NEXT")

    # ========== 1. Appium이란? ==========
    pdf.add_page()
    pdf.chapter_title("1. Appium이란?")
    pdf.body_text(
        "Appium은 모바일 앱을 자동으로 테스트할 수 있게 해주는 무료 오픈소스 도구입니다. "
        "사람이 직접 앱을 클릭하고 입력하는 것처럼, 컴퓨터가 자동으로 앱을 조작하고 테스트합니다."
    )
    pdf.ln(3)
    pdf.section_title("Appium의 장점")
    pdf.bullet_point("무료로 사용 가능 (오픈소스)")
    pdf.bullet_point("Android와 iOS 앱을 하나의 코드로 테스트 가능")
    pdf.bullet_point("Python, Java, JavaScript 등 다양한 언어 지원")
    pdf.bullet_point("실제 기기와 에뮬레이터 모두 테스트 가능")
    pdf.ln(5)

    pdf.section_title("이 환경에서 사용하는 기술 스택")
    pdf.table_row3("구분", "기술", "설명", header=True)
    pdf.table_row3("테스트 도구", "Appium", "모바일 앱 자동화 도구")
    pdf.table_row3("Android 드라이버", "UiAutomator2", "Android 앱 제어용")
    pdf.table_row3("iOS 드라이버", "XCUITest", "iOS 앱 제어용")
    pdf.table_row3("프로그래밍 언어", "Python", "테스트 스크립트 작성용")
    pdf.table_row3("테스트 프레임워크", "pytest", "테스트 실행 및 관리")
    pdf.ln(5)

    pdf.section_title("자동화 테스트가 필요한 이유")
    pdf.body_text(
        "1. 반복 작업 자동화: 매번 수동으로 테스트하는 시간을 절약합니다.\n"
        "2. 실수 방지: 사람이 놓칠 수 있는 버그를 컴퓨터가 정확히 찾아냅니다.\n"
        "3. 빠른 피드백: 코드 변경 후 바로 테스트하여 문제를 빨리 발견합니다.\n"
        "4. 품질 향상: 다양한 시나리오를 빠르게 테스트하여 앱 품질을 높입니다."
    )

    # ========== 2. 설치 명령어 ==========
    pdf.add_page()
    pdf.chapter_title("2. 설치 명령어 (환경 구성 단계)")
    pdf.body_text(
        "Appium 환경을 처음부터 구성할 때 실행해야 하는 명령어들입니다. "
        "이미 설치가 완료된 환경에서는 참고용으로 활용하세요."
    )
    pdf.ln(3)

    pdf.section_title("STEP 1: 프로젝트 폴더 생성")
    pdf.body_text("테스트 프로젝트를 저장할 폴더를 생성하고 이동합니다.")
    pdf.code_block("""# 프로젝트 폴더 생성
mkdir appium

# 폴더로 이동
cd appium""")
    pdf.ln(2)

    pdf.section_title("STEP 2: Node.js 패키지 초기화 및 Appium 설치")
    pdf.body_text("Node.js의 npm을 사용하여 Appium 서버를 설치합니다.")
    pdf.code_block("""# package.json 생성 (프로젝트 초기화)
npm init -y

# Appium 설치 (로컬 프로젝트에 설치)
npm install --save-dev appium""")
    pdf.tip_box("npm init -y는 기본값으로 package.json을 자동 생성합니다.")
    pdf.ln(2)

    pdf.section_title("STEP 3: Appium 드라이버 설치")
    pdf.body_text("Android와 iOS 테스트를 위한 드라이버를 설치합니다.")
    pdf.code_block("""# Android 드라이버 설치 (UiAutomator2)
npx appium driver install uiautomator2

# iOS 드라이버 설치 (XCUITest) - Mac에서만 필요
npx appium driver install xcuitest

# 설치된 드라이버 확인
npx appium driver list --installed""")
    pdf.warning_box("iOS 드라이버(xcuitest)는 macOS에서만 설치 및 사용 가능합니다.")
    pdf.ln(2)

    pdf.add_page()
    pdf.section_title("STEP 4: Python 가상환경 생성 및 활성화")
    pdf.body_text("Python 패키지를 격리된 환경에서 관리하기 위해 가상환경을 생성합니다.")
    pdf.code_block("""# 가상환경 생성 (venv 폴더에 생성)
python -m venv venv

# 가상환경 활성화 (Windows)
.\\venv\\Scripts\\activate

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate""")
    pdf.tip_box("활성화 성공 시 프롬프트 앞에 (venv)가 표시됩니다.")
    pdf.ln(2)

    pdf.section_title("STEP 5: Python 패키지 설치")
    pdf.body_text("테스트에 필요한 Python 라이브러리를 설치합니다.")
    pdf.code_block("""# requirements.txt 파일로 일괄 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install Appium-Python-Client>=5.0.0
pip install pytest>=8.0.0
pip install pytest-html>=4.0.0
pip install allure-pytest>=2.13.0
pip install selenium>=4.20.0""")
    pdf.ln(2)

    pdf.section_title("STEP 6: 프로젝트 구조 생성")
    pdf.body_text("테스트 코드를 정리할 폴더 구조를 생성합니다.")
    pdf.code_block("""# 폴더 생성 (Windows)
mkdir config pages tests utils reports
mkdir tests\\android tests\\ios

# 폴더 생성 (Mac/Linux)
mkdir -p config pages tests/android tests/ios utils reports""")
    pdf.ln(2)

    pdf.section_title("STEP 7: 설치 확인")
    pdf.body_text("모든 설치가 정상적으로 완료되었는지 확인합니다.")
    pdf.code_block("""# Node.js 버전 확인
node --version

# npm 버전 확인
npm --version

# Appium 버전 확인
npx appium --version

# 설치된 Appium 드라이버 확인
npx appium driver list --installed

# Python 버전 확인
python --version

# 설치된 Python 패키지 확인
pip list""")
    pdf.ln(3)

    pdf.section_title("명령어 요약 표")
    pdf.table_row("명령어", "설명", header=True)
    pdf.table_row("npm init -y", "package.json 생성 (프로젝트 초기화)")
    pdf.table_row("npm install --save-dev appium", "Appium 서버 설치")
    pdf.table_row("npx appium driver install uiautomator2", "Android 드라이버 설치")
    pdf.table_row("npx appium driver install xcuitest", "iOS 드라이버 설치 (Mac)")
    pdf.table_row("python -m venv venv", "Python 가상환경 생성")
    pdf.table_row(".\\venv\\Scripts\\activate", "가상환경 활성화 (Windows)")
    pdf.table_row("pip install -r requirements.txt", "Python 패키지 일괄 설치")

    # ========== 3. 설치된 구성 요소 ==========
    pdf.add_page()
    pdf.chapter_title("3. 설치된 구성 요소")
    pdf.body_text("현재 프로젝트에 설치된 모든 패키지 목록입니다. 이미 설치가 완료되어 있습니다.")
    pdf.ln(3)

    pdf.section_title("Node.js 패키지 (Appium 서버)")
    pdf.table_row("패키지 이름", "버전", header=True)
    pdf.table_row("appium", "3.1.2")
    pdf.table_row("appium-uiautomator2-driver", "6.7.8")
    pdf.table_row("appium-xcuitest-driver", "10.14.3")
    pdf.ln(5)

    pdf.section_title("Python 패키지 (테스트 스크립트)")
    pdf.table_row("패키지 이름", "용도", header=True)
    pdf.table_row("Appium-Python-Client", "Python에서 Appium 사용")
    pdf.table_row("pytest", "테스트 실행 프레임워크")
    pdf.table_row("pytest-html", "HTML 형식 리포트 생성")
    pdf.table_row("allure-pytest", "상세 리포트 생성")
    pdf.table_row("selenium", "웹드라이버 기반 라이브러리")
    pdf.ln(3)
    pdf.tip_box("모든 패키지는 이미 설치되어 있으므로 추가 설치가 필요 없습니다.")

    # ========== 4. 프로젝트 폴더 구조 ==========
    pdf.add_page()
    pdf.chapter_title("4. 프로젝트 폴더 구조")
    pdf.body_text("프로젝트의 각 폴더와 파일이 어떤 역할을 하는지 설명합니다.")
    pdf.ln(2)
    pdf.code_block("""appium/
|
|-- config/                 <- 설정 파일 폴더
|   |-- capabilities.py     <- 디바이스 설정 (중요!)
|
|-- pages/                  <- 페이지 객체 폴더
|   |-- base_page.py        <- 공통 기능 모음
|   |-- sample_page.py      <- 샘플 페이지
|
|-- tests/                  <- 테스트 코드 폴더
|   |-- android/            <- Android 테스트
|   |-- ios/                <- iOS 테스트
|   |-- test_cross_platform.py  <- 공통 테스트
|
|-- utils/                  <- 유틸리티 폴더
|   |-- helpers.py          <- 도우미 함수
|
|-- reports/                <- 테스트 결과 저장
|-- venv/                   <- Python 가상환경
|-- conftest.py             <- pytest 설정
|-- pytest.ini              <- pytest 옵션
|-- requirements.txt        <- Python 패키지 목록""")

    pdf.section_title("주요 폴더 설명")
    pdf.bullet_point("config/ : 테스트할 기기 정보를 설정하는 곳")
    pdf.bullet_point("pages/ : 앱의 각 화면을 코드로 정의하는 곳")
    pdf.bullet_point("tests/ : 실제 테스트 코드를 작성하는 곳")
    pdf.bullet_point("reports/ : 테스트 결과와 스크린샷이 저장되는 곳")
    pdf.bullet_point("venv/ : Python 패키지들이 설치된 가상환경")

    # ========== 5. 설정 파일 상세 설명 ==========
    pdf.add_page()
    pdf.chapter_title("5. 설정 파일 상세 설명")

    pdf.section_title("5.1 capabilities.py - 디바이스 설정")
    pdf.body_text(
        "테스트할 기기의 정보를 설정하는 파일입니다. "
        "테스트 전에 반드시 자신의 환경에 맞게 수정해야 합니다."
    )
    pdf.code_block("""# Android 설정 예시
ANDROID_CAPS = {
    "platformName": "Android",      # 플랫폼 (수정 불필요)
    "automationName": "UiAutomator2",  # 드라이버 (수정 불필요)
    "deviceName": "Android Emulator",  # 기기 이름
    "platformVersion": "14",        # Android 버전 (기기에 맞게 수정)
    "app": "C:/path/to/app.apk",    # 테스트할 앱 경로 (필수 수정!)
    "noReset": False,               # 앱 초기화 여부
    "autoGrantPermissions": True,   # 권한 자동 승인
}""")
    pdf.ln(2)
    pdf.warning_box("app 경로는 반드시 실제 APK 파일 경로로 변경해야 합니다!")
    pdf.ln(2)

    pdf.section_title("5.2 conftest.py - pytest 설정")
    pdf.body_text(
        "테스트 실행 시 자동으로 드라이버를 생성하고 정리합니다. "
        "일반적으로 수정할 필요가 없습니다."
    )
    pdf.bullet_point("driver : 플랫폼에 따라 자동 선택되는 드라이버")
    pdf.bullet_point("android_driver : Android 전용 드라이버")
    pdf.bullet_point("ios_driver : iOS 전용 드라이버")
    pdf.ln(3)

    pdf.section_title("5.3 pytest.ini - 테스트 옵션")
    pdf.body_text("테스트 실행 시 기본 옵션을 설정합니다.")
    pdf.code_block("""[pytest]
testpaths = tests          # 테스트 파일 위치
python_files = test_*.py   # 테스트 파일 패턴
addopts = -v --tb=short    # 상세 출력, 짧은 에러 표시""")

    # ========== 6. 테스트 실행 방법 ==========
    pdf.add_page()
    pdf.chapter_title("6. 테스트 실행 방법 (단계별 가이드)")
    pdf.body_text("테스트를 실행하려면 아래 단계를 순서대로 따라하세요.")
    pdf.ln(3)

    pdf.section_title("STEP 1: 명령 프롬프트 열기")
    pdf.body_text("Windows 키 + R을 누르고 'cmd'를 입력한 후 Enter를 누릅니다.")
    pdf.ln(2)

    pdf.section_title("STEP 2: 프로젝트 폴더로 이동")
    pdf.body_text("아래 명령어를 복사하여 붙여넣기 합니다.")
    pdf.code_block("cd C:\\Users\\GME\\appium")
    pdf.ln(2)

    pdf.section_title("STEP 3: 가상환경 활성화")
    pdf.body_text("Python 가상환경을 활성화합니다. 프롬프트 앞에 (venv)가 나타나면 성공입니다.")
    pdf.code_block(".\\venv\\Scripts\\activate")
    pdf.tip_box("(venv) C:\\Users\\GME\\appium> 와 같이 표시되어야 합니다.")
    pdf.ln(2)

    pdf.section_title("STEP 4: Appium 서버 시작")
    pdf.body_text("새 명령 프롬프트 창을 열고, 같은 폴더에서 Appium 서버를 시작합니다.")
    pdf.code_block("""cd C:\\Users\\GME\\appium
npm run appium:start""")
    pdf.body_text("'Appium REST http interface listener started' 메시지가 나오면 성공입니다.")
    pdf.warning_box("이 창은 테스트가 끝날 때까지 닫지 마세요!")

    pdf.add_page()
    pdf.section_title("STEP 5: 테스트 실행")
    pdf.body_text("STEP 3의 창(가상환경이 활성화된 창)에서 테스트를 실행합니다.")
    pdf.ln(2)
    pdf.body_text("Android 테스트 실행:")
    pdf.code_block("pytest tests/android -v --app=\"C:\\path\\to\\your\\app.apk\"")
    pdf.ln(1)
    pdf.body_text("iOS 테스트 실행 (Mac에서만 가능):")
    pdf.code_block("pytest tests/ios -v --app=\"/path/to/your/app.app\"")
    pdf.ln(1)
    pdf.body_text("HTML 리포트와 함께 실행:")
    pdf.code_block("pytest tests/android -v --html=reports/report.html")
    pdf.ln(3)

    pdf.section_title("npm 스크립트 (단축 명령어)")
    pdf.body_text("자주 사용하는 명령어를 간단하게 실행할 수 있습니다.")
    pdf.table_row("명령어", "설명", header=True)
    pdf.table_row("npm run appium:start", "Appium 서버 시작")
    pdf.table_row("npm run appium:drivers", "설치된 드라이버 확인")
    pdf.table_row("npm run test:android", "Android 테스트 실행")
    pdf.table_row("npm run test:ios", "iOS 테스트 실행")

    # ========== 7. 테스트 코드 작성 방법 ==========
    pdf.add_page()
    pdf.chapter_title("7. 테스트 코드 작성 방법")
    pdf.body_text("실제 테스트 코드를 작성하는 방법을 설명합니다.")
    pdf.ln(3)

    pdf.section_title("7.1 Page Object Model (POM) 패턴")
    pdf.body_text(
        "POM은 앱의 각 화면(페이지)을 별도의 클래스로 만드는 방식입니다. "
        "이렇게 하면 코드 관리가 쉽고, 앱이 변경되어도 한 곳만 수정하면 됩니다."
    )
    pdf.ln(2)

    pdf.section_title("7.2 BasePage 클래스 (공통 기능)")
    pdf.body_text("모든 페이지에서 사용하는 공통 기능을 모아놓은 클래스입니다.")
    pdf.code_block("""class BasePage:
    def find_element(self, locator):
        # 화면에서 요소(버튼, 입력창 등) 찾기

    def click(self, locator):
        # 요소 클릭하기

    def input_text(self, locator, text):
        # 텍스트 입력하기

    def swipe_up(self):
        # 화면 위로 스크롤

    def take_screenshot(self, filename):
        # 스크린샷 저장""")
    pdf.ln(3)

    pdf.section_title("7.3 테스트 코드 예시")
    pdf.body_text("로그인 기능을 테스트하는 예시 코드입니다.")
    pdf.code_block("""class TestLogin:
    def test_login_success(self, driver):
        # 1. 로그인 페이지 객체 생성
        login_page = LoginPage(driver)

        # 2. 아이디 입력
        login_page.enter_username("testuser")

        # 3. 비밀번호 입력
        login_page.enter_password("password123")

        # 4. 로그인 버튼 클릭
        login_page.click_login()

        # 5. 로그인 성공 확인
        assert home_page.is_displayed()""")

    pdf.add_page()
    pdf.section_title("7.4 요소 찾기 (Locator) 종류")
    pdf.body_text("앱 화면에서 버튼, 입력창 등을 찾는 방법입니다.")
    pdf.table_row3("Locator 종류", "사용 예시", "설명", header=True)
    pdf.table_row3("AppiumBy.ID", "com.app:id/login_btn", "리소스 ID로 찾기")
    pdf.table_row3("AppiumBy.ACCESSIBILITY_ID", "login_button", "접근성 ID로 찾기")
    pdf.table_row3("AppiumBy.XPATH", "//Button[@text='로그인']", "XPath로 찾기")
    pdf.table_row3("AppiumBy.CLASS_NAME", "android.widget.Button", "클래스명으로 찾기")
    pdf.ln(3)
    pdf.tip_box("Appium Inspector를 사용하면 요소의 Locator를 쉽게 찾을 수 있습니다.")

    pdf.ln(5)
    pdf.section_title("7.5 새 테스트 파일 만들기")
    pdf.body_text("tests/android/ 폴더에 새 파일을 만들 때 아래 형식을 따르세요.")
    pdf.code_block("""# 파일명: test_기능이름.py (예: test_login.py)

import pytest
from appium.webdriver.common.appiumby import AppiumBy

class Test기능이름:
    def test_케이스이름(self, android_driver):
        # 테스트 코드 작성
        pass""")

    # ========== 8. 사전 준비 사항 ==========
    pdf.add_page()
    pdf.chapter_title("8. 사전 준비 사항")
    pdf.body_text("테스트를 실행하기 전에 아래 항목들이 준비되어 있어야 합니다.")
    pdf.ln(3)

    pdf.section_title("8.1 Android 테스트 준비물")
    pdf.numbered_item(1, "Android SDK 설치")
    pdf.body_text("   Android Studio를 설치하면 SDK가 함께 설치됩니다.")
    pdf.numbered_item(2, "ANDROID_HOME 환경변수 설정")
    pdf.body_text("   시스템 환경변수에 Android SDK 경로를 추가해야 합니다.")
    pdf.code_block("""# 환경변수 확인 방법 (명령 프롬프트에서)
echo %ANDROID_HOME%

# 결과 예시: C:\\Users\\사용자명\\AppData\\Local\\Android\\Sdk""")
    pdf.numbered_item(3, "에뮬레이터 또는 실제 기기 준비")
    pdf.bullet_point("에뮬레이터: Android Studio > Device Manager에서 생성")
    pdf.bullet_point("실제 기기: USB 연결 + USB 디버깅 활성화 필요")
    pdf.code_block("""# 연결된 기기 확인
adb devices

# 결과 예시:
# List of devices attached
# emulator-5554   device""")
    pdf.ln(3)

    pdf.section_title("8.2 iOS 테스트 준비물 (Mac 전용)")
    pdf.warning_box("iOS 테스트는 macOS에서만 가능합니다. Windows에서는 실행할 수 없습니다.")
    pdf.numbered_item(1, "Xcode 설치 (App Store에서)")
    pdf.numbered_item(2, "Xcode Command Line Tools 설치")
    pdf.code_block("xcode-select --install")
    pdf.numbered_item(3, "iOS 시뮬레이터 또는 실제 기기 준비")
    pdf.code_block("""# 사용 가능한 시뮬레이터 목록 확인
xcrun simctl list devices""")

    # ========== 9. 자주 발생하는 문제 ==========
    pdf.add_page()
    pdf.chapter_title("9. 자주 발생하는 문제와 해결 방법")
    pdf.ln(3)

    pdf.section_title("문제 1: Appium 서버 연결 실패")
    pdf.body_text("에러 메시지: Could not connect to Appium server")
    pdf.bullet_point("원인: Appium 서버가 실행되지 않음")
    pdf.bullet_point("해결: 'npm run appium:start'로 서버를 먼저 실행하세요")
    pdf.ln(3)

    pdf.section_title("문제 2: 디바이스를 찾을 수 없음")
    pdf.body_text("에러 메시지: No device found / Device not connected")
    pdf.bullet_point("원인: 에뮬레이터가 실행되지 않았거나 기기가 연결되지 않음")
    pdf.bullet_point("해결 1: Android Studio에서 에뮬레이터를 먼저 실행하세요")
    pdf.bullet_point("해결 2: 'adb devices' 명령으로 기기 연결 확인하세요")
    pdf.ln(3)

    pdf.section_title("문제 3: 앱을 찾을 수 없음")
    pdf.body_text("에러 메시지: App not found at path")
    pdf.bullet_point("원인: capabilities.py의 app 경로가 잘못됨")
    pdf.bullet_point("해결: APK/IPA 파일의 전체 경로를 정확히 입력하세요")
    pdf.ln(3)

    pdf.section_title("문제 4: 요소를 찾을 수 없음")
    pdf.body_text("에러 메시지: NoSuchElementException")
    pdf.bullet_point("원인: Locator가 잘못되었거나 요소가 아직 로딩되지 않음")
    pdf.bullet_point("해결 1: Appium Inspector로 정확한 Locator 확인")
    pdf.bullet_point("해결 2: 대기 시간(wait) 늘리기")
    pdf.ln(3)

    pdf.section_title("도움이 필요할 때")
    pdf.bullet_point("Appium 공식 문서: https://appium.io/docs/")
    pdf.bullet_point("Appium Inspector 다운로드:")
    pdf.code_block("https://github.com/appium/appium-inspector/releases")

    # ========== 마지막 페이지 ==========
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font(pdf.korean_font, "B", 16)
    pdf.set_text_color(30, 80, 150)
    pdf.cell(0, 10, "환경 구성 완료!", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font(pdf.korean_font, "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 7,
        "축하합니다! Appium 모바일 자동화 테스트 환경이 모두 구성되었습니다.\n\n"
        "이제 다음 단계를 진행하세요:\n\n"
        "1. config/capabilities.py에서 앱 경로 설정\n"
        "2. 에뮬레이터 또는 실제 기기 준비\n"
        "3. Appium 서버 시작\n"
        "4. 테스트 실행\n\n"
        "테스트 코드는 tests/ 폴더의 샘플을 참고하여 작성하세요.\n"
        "궁금한 점이 있으면 Appium 공식 문서를 참고하세요.",
        align="C"
    )
    pdf.ln(20)
    pdf.set_font(pdf.korean_font, "", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, "프로젝트 위치: C:\\Users\\GME\\appium", align="C", new_x="LMARGIN", new_y="NEXT")

    # ========== PDF 저장 ==========
    output_path = os.path.join(PROJECT_ROOT, "pdf", "Appium_Setup_Guide.pdf")
    pdf.output(output_path)
    print(f"PDF 생성 완료: {output_path}")
    return output_path


if __name__ == "__main__":
    create_pdf()
