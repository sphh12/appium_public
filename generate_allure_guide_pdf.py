# -*- coding: utf-8 -*-
"""
Allure 리포트 설정 가이드 PDF 생성
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
        self.cell(0, 10, "Allure 리포트 설정 가이드", align="C", new_x="LMARGIN", new_y="NEXT")
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
        self.set_fill_color(230, 245, 230)
        self.set_text_color(50, 100, 50)
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


def create_allure_guide_pdf():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ========== 표지 ==========
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font(pdf.korean_font, "B", 28)
    pdf.set_text_color(30, 80, 150)
    pdf.cell(0, 15, "Allure Report", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font(pdf.korean_font, "B", 18)
    pdf.cell(0, 12, "테스트 리포트 설정 가이드", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    pdf.set_font(pdf.korean_font, "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Appium + pytest 테스트 결과를 시각적으로 확인", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(25)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(10)
    pdf.set_font(pdf.korean_font, "", 10)
    pdf.cell(0, 8, "작성일: 2026-01-05", align="C", new_x="LMARGIN", new_y="NEXT")

    # ========== 목차 ==========
    pdf.add_page()
    pdf.chapter_title("목차")
    pdf.ln(5)
    pdf.set_font(pdf.korean_font, "", 11)
    pdf.cell(0, 8, "1. Allure Report란?", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "2. 설치 방법", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "3. 테스트 실행 및 리포트 생성", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "4. Allure 리포트 보기", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "5. 테스트 코드에 Allure 기능 추가", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "6. 리포트 화면 구성", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "7. 유용한 명령어 모음", new_x="LMARGIN", new_y="NEXT")

    # ========== 1. Allure Report란? ==========
    pdf.add_page()
    pdf.chapter_title("1. Allure Report란?")
    pdf.body_text(
        "Allure Report는 테스트 결과를 시각적으로 보여주는 리포트 도구입니다. "
        "pytest 실행 결과를 그래프, 차트, 상세 로그로 확인할 수 있어 "
        "테스트 분석이 훨씬 쉬워집니다."
    )
    pdf.ln(3)

    pdf.section_title("Allure Report의 장점")
    pdf.bullet_point("시각적인 대시보드로 테스트 결과 한눈에 파악")
    pdf.bullet_point("테스트 성공/실패/스킵 비율을 그래프로 표시")
    pdf.bullet_point("각 테스트의 실행 시간, 단계별 로그 확인")
    pdf.bullet_point("스크린샷, 로그 파일 등 첨부 가능")
    pdf.bullet_point("테스트 이력 추적 및 트렌드 분석")
    pdf.ln(5)

    pdf.section_title("다른 리포트 도구와 비교")
    pdf.table_row("리포트 도구", "특징", header=True)
    pdf.table_row("pytest 기본", "터미널 텍스트 출력만 제공")
    pdf.table_row("pytest-html", "간단한 HTML 리포트")
    pdf.table_row("Allure", "상세한 시각적 리포트 (권장)")

    # ========== 2. 설치 방법 ==========
    pdf.add_page()
    pdf.chapter_title("2. 설치 방법")
    pdf.body_text("Allure 리포트를 사용하려면 두 가지를 설치해야 합니다.")
    pdf.ln(3)

    pdf.section_title("2.1 allure-pytest 설치 (Python 패키지)")
    pdf.body_text("pytest에서 Allure 결과를 생성하기 위한 패키지입니다.")
    pdf.code_block("""# 가상환경 활성화 후 실행
cd C:\\Users\\GME\\appium-mobile-test
.\\venv\\Scripts\\Activate.ps1

# allure-pytest 설치
pip install allure-pytest""")
    pdf.ln(2)

    pdf.section_title("2.2 Allure CLI 설치 (명령어 도구)")
    pdf.body_text("리포트를 생성하고 보기 위한 명령어 도구입니다.")
    pdf.ln(2)

    pdf.body_text("방법 1: Scoop으로 설치 (권장)")
    pdf.code_block("""# Scoop 설치 (없는 경우)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
irm get.scoop.sh | iex

# Allure 설치
scoop install allure

# 설치 확인
allure --version""")
    pdf.ln(2)

    pdf.body_text("방법 2: Chocolatey로 설치")
    pdf.code_block("""# Chocolatey로 설치
choco install allure

# 설치 확인
allure --version""")
    pdf.ln(2)

    pdf.tip_box("Scoop이나 Chocolatey 둘 중 하나만 사용하면 됩니다.")

    # ========== 3. 테스트 실행 및 리포트 생성 ==========
    pdf.add_page()
    pdf.chapter_title("3. 테스트 실행 및 리포트 생성")
    pdf.body_text("테스트를 실행하면서 Allure 결과 파일을 생성하는 방법입니다.")
    pdf.ln(3)

    pdf.section_title("3.1 기본 실행 명령어")
    pdf.code_block("""# 테스트 실행 + Allure 결과 생성
python -m pytest tests/test_01.py -v --platform=android --alluredir=allure-results""")
    pdf.ln(2)

    pdf.section_title("옵션 설명")
    pdf.table_row("옵션", "설명", header=True)
    pdf.table_row("tests/test_01.py", "실행할 테스트 파일")
    pdf.table_row("-v", "상세 출력 (verbose)")
    pdf.table_row("--platform=android", "Android 플랫폼 지정")
    pdf.table_row("--alluredir=allure-results", "Allure 결과 저장 폴더")
    pdf.ln(3)

    pdf.section_title("3.2 전체 테스트 실행")
    pdf.code_block("""# tests 폴더 전체 테스트 실행
python -m pytest tests/ -v --platform=android --alluredir=allure-results

# 특정 테스트 클래스만 실행
python -m pytest tests/test_01.py::TestAndroidSample -v --platform=android --alluredir=allure-results

# 특정 테스트 함수만 실행
python -m pytest tests/test_01.py::TestAndroidSample::test_Login -v --platform=android --alluredir=allure-results""")
    pdf.ln(2)

    pdf.warning_box("--alluredir 옵션을 빼면 Allure 결과가 생성되지 않습니다!")

    # ========== 4. Allure 리포트 보기 ==========
    pdf.add_page()
    pdf.chapter_title("4. Allure 리포트 보기")
    pdf.body_text("테스트 실행 후 Allure 리포트를 확인하는 방법입니다.")
    pdf.ln(3)

    pdf.section_title("4.1 리포트 서버 실행 (권장)")
    pdf.body_text("브라우저에서 실시간으로 리포트를 확인합니다.")
    pdf.code_block("""# 리포트 서버 시작 (브라우저 자동 열림)
allure serve allure-results""")
    pdf.tip_box("Ctrl+C를 누르면 서버가 종료됩니다.")
    pdf.ln(3)

    pdf.section_title("4.2 HTML 리포트 생성")
    pdf.body_text("리포트를 HTML 파일로 저장하여 나중에 확인합니다.")
    pdf.code_block("""# HTML 리포트 생성
allure generate allure-results -o allure-report --clean

# 생성된 리포트 열기
allure open allure-report""")
    pdf.ln(2)

    pdf.section_title("옵션 설명")
    pdf.table_row("옵션", "설명", header=True)
    pdf.table_row("allure-results", "테스트 결과 폴더 (입력)")
    pdf.table_row("-o allure-report", "HTML 리포트 저장 폴더 (출력)")
    pdf.table_row("--clean", "기존 리포트 삭제 후 새로 생성")

    # ========== 5. 테스트 코드에 Allure 기능 추가 ==========
    pdf.add_page()
    pdf.chapter_title("5. 테스트 코드에 Allure 기능 추가")
    pdf.body_text("테스트 코드에 Allure 데코레이터를 추가하면 더 상세한 리포트를 생성할 수 있습니다.")
    pdf.ln(3)

    pdf.section_title("5.1 기본 데코레이터")
    pdf.code_block("""import allure
import pytest

@allure.feature("로그인")
@allure.story("정상 로그인")
@allure.severity(allure.severity_level.CRITICAL)
class TestLogin:

    @allure.title("유효한 계정으로 로그인 성공")
    @allure.description("올바른 아이디와 비밀번호로 로그인 테스트")
    def test_login_success(self, android_driver):
        # 테스트 코드
        pass""")
    pdf.ln(2)

    pdf.section_title("데코레이터 설명")
    pdf.table_row("데코레이터", "설명", header=True)
    pdf.table_row("@allure.feature", "기능 그룹 (대분류)")
    pdf.table_row("@allure.story", "사용자 스토리 (중분류)")
    pdf.table_row("@allure.title", "테스트 제목")
    pdf.table_row("@allure.description", "테스트 상세 설명")
    pdf.table_row("@allure.severity", "심각도 (CRITICAL, NORMAL 등)")
    pdf.ln(3)

    pdf.section_title("5.2 테스트 단계 추가")
    pdf.code_block("""import allure

def test_login_flow(self, android_driver):
    with allure.step("로그인 화면 진입"):
        login_btn = android_driver.find_element(...)
        login_btn.click()

    with allure.step("아이디 입력"):
        username = android_driver.find_element(...)
        username.send_keys("test_user")

    with allure.step("비밀번호 입력"):
        password = android_driver.find_element(...)
        password.send_keys("password123")

    with allure.step("로그인 버튼 클릭"):
        submit = android_driver.find_element(...)
        submit.click()""")
    pdf.tip_box("with allure.step()을 사용하면 리포트에서 각 단계를 구분하여 볼 수 있습니다.")

    # ========== 5.3 스크린샷 첨부 ==========
    pdf.add_page()
    pdf.section_title("5.3 스크린샷 첨부")
    pdf.body_text("테스트 실패 시 또는 중요한 시점에 스크린샷을 리포트에 첨부합니다.")
    pdf.code_block("""import allure

def test_with_screenshot(self, android_driver):
    # 테스트 실행...

    # 스크린샷 첨부
    allure.attach(
        android_driver.get_screenshot_as_png(),
        name="현재 화면",
        attachment_type=allure.attachment_type.PNG
    )""")
    pdf.ln(3)

    pdf.section_title("5.4 실패 시 자동 스크린샷 (conftest.py)")
    pdf.body_text("conftest.py에 추가하면 테스트 실패 시 자동으로 스크린샷을 저장합니다.")
    pdf.code_block("""# conftest.py에 추가
import allure
import pytest

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("android_driver")
        if driver:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="failure_screenshot",
                attachment_type=allure.attachment_type.PNG
            )""")

    # ========== 6. 리포트 화면 구성 ==========
    pdf.add_page()
    pdf.chapter_title("6. 리포트 화면 구성")
    pdf.body_text("Allure 리포트의 주요 화면과 기능을 설명합니다.")
    pdf.ln(3)

    pdf.section_title("6.1 Overview (대시보드)")
    pdf.bullet_point("전체 테스트 결과 요약")
    pdf.bullet_point("성공/실패/스킵 비율 파이 차트")
    pdf.bullet_point("테스트 실행 시간 통계")
    pdf.ln(3)

    pdf.section_title("6.2 Suites (테스트 묶음)")
    pdf.bullet_point("테스트 파일/클래스별 결과 확인")
    pdf.bullet_point("각 테스트의 상세 정보 확인")
    pdf.ln(3)

    pdf.section_title("6.3 Graphs (그래프)")
    pdf.bullet_point("테스트 결과 분포 그래프")
    pdf.bullet_point("심각도별 분류")
    pdf.bullet_point("실행 시간 분포")
    pdf.ln(3)

    pdf.section_title("6.4 Timeline (타임라인)")
    pdf.bullet_point("테스트 실행 순서와 시간 시각화")
    pdf.bullet_point("병렬 실행 상태 확인")
    pdf.ln(3)

    pdf.section_title("6.5 Behaviors (기능별)")
    pdf.bullet_point("@allure.feature, @allure.story 기준 분류")
    pdf.bullet_point("기능별 테스트 커버리지 확인")

    # ========== 7. 유용한 명령어 모음 ==========
    pdf.add_page()
    pdf.chapter_title("7. 유용한 명령어 모음")
    pdf.ln(3)

    pdf.section_title("테스트 실행")
    pdf.code_block("""# 기본 실행
python -m pytest tests/test_01.py -v --platform=android --alluredir=allure-results

# 실패한 테스트만 재실행
python -m pytest tests/test_01.py -v --platform=android --alluredir=allure-results --lf

# 특정 마커가 있는 테스트만 실행
python -m pytest tests/ -v --platform=android --alluredir=allure-results -m "smoke"
""")
    pdf.ln(2)

    pdf.section_title("리포트 확인")
    pdf.code_block("""# 서버로 바로 보기 (권장)
allure serve allure-results

# HTML 파일로 생성
allure generate allure-results -o allure-report --clean

# 생성된 HTML 열기
allure open allure-report""")
    pdf.ln(2)

    pdf.section_title("결과 정리")
    pdf.code_block("""# 이전 결과 삭제 (Windows PowerShell)
Remove-Item -Recurse -Force allure-results

# 이전 결과 삭제 (CMD)
rmdir /s /q allure-results""")
    pdf.ln(5)

    pdf.section_title("명령어 요약 표")
    pdf.table_row("명령어", "설명", header=True)
    pdf.table_row("pip install allure-pytest", "Python 패키지 설치")
    pdf.table_row("scoop install allure", "Allure CLI 설치")
    pdf.table_row("--alluredir=allure-results", "결과 저장 옵션")
    pdf.table_row("allure serve allure-results", "리포트 서버 실행")
    pdf.table_row("allure generate ... -o ...", "HTML 리포트 생성")

    # ========== 마지막 페이지 ==========
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font(pdf.korean_font, "B", 16)
    pdf.set_text_color(30, 80, 150)
    pdf.cell(0, 10, "Allure 리포트 설정 완료!", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font(pdf.korean_font, "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 7,
        "이제 테스트 결과를 시각적으로 확인할 수 있습니다.\n\n"
        "실행 순서:\n\n"
        "1. 테스트 실행: pytest ... --alluredir=allure-results\n"
        "2. 리포트 보기: allure serve allure-results\n\n"
        "테스트 코드에 @allure 데코레이터를 추가하면\n"
        "더 상세한 리포트를 생성할 수 있습니다.",
        align="C"
    )

    # ========== PDF 저장 ==========
    output_path = os.path.join(PROJECT_ROOT, "pdf", "Allure_Report_Guide.pdf")
    pdf.output(output_path)
    print(f"PDF 생성 완료: {output_path}")
    return output_path


if __name__ == "__main__":
    create_allure_guide_pdf()
