# 라이브러리 설치를 위해 터미널에 아래의 pip 명령어 입력
# 먼저 pip install openpyxl playwright 입력
# 그 다음 playwright install 입력
# 위 터미널 창에 붙여넣기하여 라이브러리 설치

import os
import openpyxl
from openpyxl import Workbook
from playwright.sync_api import sync_playwright
import random
import time
from datetime import datetime

# --- 경로 설정 --------------------------------------------------------------
폴더경로 = os.path.dirname(os.path.abspath(__file__))
excel_file_path = os.path.join(폴더경로, '추가인원 가입 수강신청.xlsx')
사용자_데이터_디렉토리 = os.path.join(폴더경로, 'UserData')

# --- 전역 리스트 초기화 ----------------------------------------------------
클릭 = 0
학교_리스트    = []
아파트_리스트  = []
동_리스트      = []
아이디1_리스트 = []
아이디2_리스트 = []
아이디3_리스트 = []
남아_리스트    = []
여아_리스트    = []
부_리스트      = []
모_리스트      = []

# --- 성씨 및 확률 ----------------------------------------------------------
성 = [
    ("김", 0.21782), ("이", 0.14882), ("박", 0.08536), ("최", 0.04754), ("정", 0.04402),
    ("강", 0.02355), ("조", 0.02161), ("윤", 0.02077), ("장", 0.02017), ("임", 0.01674),
    ("한", 0.01560), ("오", 0.01548), ("서", 0.01524), ("신", 0.01526), ("권", 0.01427),
    ("황", 0.01412), ("안", 0.01393), ("송", 0.01389), ("류", 0.01300), ("전", 0.01098),
    ("홍", 0.01137), ("고", 0.00957), ("문", 0.00938), ("양", 0.00884), ("손", 0.00919),
    ("배", 0.00812), ("백", 0.00773), ("허", 0.00660), ("유", 0.00566), ("남", 0.00559),
    ("심", 0.00551), ("노", 0.00498), ("정", 0.00442), ("하", 0.00463), ("곽", 0.00410),
    ("성", 0.00405), ("차", 0.00396), ("주", 0.00389), ("우", 0.00390), ("구", 0.00392),
    ("신", 0.00369), ("임", 0.00379), ("라", 0.00377), ("전", 0.00386), ("민", 0.00350),
    ("유", 0.00381), ("진", 0.00315), ("지", 0.00311), ("엄", 0.00291), ("채", 0.00254),
    ("원", 0.00262), ("천", 0.00239), ("방", 0.00191), ("공", 0.00183), ("강", 0.00201),
    ("현", 0.00180), ("함", 0.00164), ("변", 0.00164), ("염", 0.00139), ("양", 0.00181),
    ("변", 0.00121), ("여", 0.00123), ("추", 0.00121), ("노", 0.00134), ("도", 0.00115),
    ("소", 0.00098), ("신", 0.00103), ("석", 0.00100), ("선", 0.00085), ("설", 0.00086),
    ("마", 0.00078), ("길", 0.00075), ("주", 0.00081), ("연", 0.00068), ("방", 0.00068),
    ("위", 0.00062), ("표", 0.00062), ("명", 0.00059), ("기", 0.00056), ("반", 0.00054),
    ("왕", 0.00051), ("금", 0.00051), ("옥", 0.00051), ("육", 0.00047), ("인", 0.00045),
    ("맹", 0.00044), ("제", 0.00044), ("모", 0.00042), ("장", 0.00041), ("남", 0.00042),
    ("탁", 0.00043), ("국", 0.00039), ("여", 0.00039), ("진", 0.00042), ("어", 0.00038),
    ("은", 0.00034), ("편", 0.00033), ("구", 0.00029), ("용", 0.00016), ("남궁", 0.00015)
]
성씨, weights = zip(*성)

# --- 고정 비밀번호 ----------------------------------------------------------
비밀번호 = 'enoz7223!'

# --- 정보 시트에서 불러올 변수들 ------------------------------------------------
BG회원가입   = ""
BG수강신청   = ""
PH회원가입   = ""
PH수강신청   = ""
반복횟수     = 0
랜덤최소     = 0
랜덤최대     = 0

def 초기화():
    """'정보' 시트에서 BG/PH 사이트 URL, 반복횟수, 랜덤대기값을 읽어옵니다."""
    global BG회원가입, BG수강신청, PH회원가입, PH수강신청
    global 반복횟수, 랜덤최소, 랜덤최대
    global 아이디1_리스트, 아이디2_리스트, 아이디3_리스트
    global 남아_리스트, 여아_리스트, 부_리스트, 모_리스트
    
    아이디1_리스트.clear()
    아이디2_리스트.clear()
    아이디3_리스트.clear()
    남아_리스트.clear()
    여아_리스트.clear()
    부_리스트.clear()
    모_리스트.clear()
        
    wb = openpyxl.load_workbook(excel_file_path, data_only=True)
    ws = wb["정보"]

    반복횟수   = ws.cell(row=1, column=20).value
    랜덤최소   = ws.cell(row=2, column=20).value
    랜덤최대   = ws.cell(row=3, column=20).value
    
    아이디마지막행 = 92
    자녀마지막행   = 501
    부모마지막행   = 78
    
    for row in ws.iter_rows(min_row=2, max_row=아이디마지막행, values_only=True):
        아이디1_리스트.append(row[5])
        아이디2_리스트.append(row[6])
        아이디3_리스트.append(row[7])

    for row in ws.iter_rows(min_row=2, max_row=자녀마지막행, values_only=True):
        남아_리스트.append(row[10])
        여아_리스트.append(row[11])

    for row in ws.iter_rows(min_row=2, max_row=부모마지막행, values_only=True):
        부_리스트.append(row[14])
        모_리스트.append(row[15])
    wb.close()

def load_lists(sheet_name):

    global 학교_리스트, 아파트_리스트, 동_리스트
    global 회원가입사이트, 수강신청사이트

    학교_리스트.clear()
    아파트_리스트.clear()
    동_리스트.clear()

    wb = openpyxl.load_workbook(excel_file_path, data_only=True)
    ws = wb[sheet_name]

    학교마지막행   = 31

    for row in ws.iter_rows(min_row=2, max_row=학교마지막행, values_only=True):
        학교_리스트.append(row[0])
        아파트_리스트.append(row[1])
        동_리스트.append(row[2])

    회원가입사이트 = ws.cell(row=1, column=20).value
    수강신청사이트 = ws.cell(row=2, column=20).value

    wb.close()

def 엑셀_초기화_및_데이터_저장(sheet_name, 이름, 아이디, 나이, 요일, 학교, 주소):
    """
    '추가인원 가입 현황.xlsx'에
    sheet_name(PH 또는 BG) 시트를 만들어(또는 기존 시트 사용)
    가입 기록을 남깁니다.
    """
    현황_경로 = os.path.join(폴더경로, '추가인원 가입 현황.xlsx')
    if not os.path.exists(현황_경로):
        wb2 = Workbook()
        ws2 = wb2.active
        ws2.title = sheet_name
        ws2.append(["이름","아이디","나이","학교","주소","가입일시"])
    else:
        wb2 = openpyxl.load_workbook(현황_경로)
        if sheet_name in wb2.sheetnames:
            ws2 = wb2[sheet_name]
        else:
            ws2 = wb2.create_sheet(title=sheet_name)
            ws2.append(["이름","아이디","나이","요일","학교","주소","가입일시"])

    ws2.append([
        이름,
        아이디,
        나이,
        요일,
        학교,
        주소,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ])
    wb2.save(현황_경로)
    wb2.close()

def handle_alert(dialog):
    """팝업 알림 자동 수락"""
    global 클릭
    time.sleep(1)
    클릭 = 1
    dialog.accept()

def 회원가입(page, sheet_name):
    global 이름,요일
    
    load_lists(sheet_name)
    page.goto(회원가입사이트)
    time.sleep(2)
    page.keyboard.press('F5')
    time.sleep(3)
    if page.locator('a[href="/Account/LoginProc"]:has-text("LOGOUT")').count() > 0:
        page.locator('a[href="/Account/LoginProc"]').click()
        time.sleep(1)
        page.goto(회원가입사이트)

    page.wait_for_load_state('networkidle')
    page.locator("#cbAgree1").click(force=True)
    page.locator("#cbAgree2").click(force=True)
    page.click(".btn_type4.c1:has-text('다음')")
    page.wait_for_selector("input[name='tbMemName'].type2.w1.IsKor")

    # 이름 & 성별
    이름   = random.choices(성씨, weights=weights, k=1)[0]
    아이성 = 이름
    성별   = random.randint(0, 6)
    if 성별 < 5:
        page.select_option('select[name="ddlSex"]', value='남자')
        이름 += 남아_리스트[random.randint(0, len(남아_리스트)-1)]
    else:
        page.select_option('select[name="ddlSex"]', value='여자')
        이름 += 여아_리스트[random.randint(0, len(여아_리스트)-1)]
    page.fill('input[name="tbMemName"]', 이름)

    # 아이디 생성
    랜덤 = random.randint(0, 2)
    if 랜덤 == 0:
        아이디 = 아이디1_리스트[random.randint(0, len(아이디1_리스트)-1)]
    elif 랜덤 == 1:
        아이디 = 아이디2_리스트[random.randint(0, len(아이디2_리스트)-1)]
    else:
        아이디 = 아이디3_리스트[random.randint(0, len(아이디3_리스트)-1)]
    랜덤 = random.randint(0, 11)
    if 랜덤 < 3:
        아이디 += 아이디1_리스트[random.randint(0, len(아이디1_리스트)-1)]
    elif 랜덤 < 6:
        아이디 += 아이디2_리스트[random.randint(0, len(아이디2_리스트)-1)]
    elif 랜덤 < 9:
        아이디 += 아이디3_리스트[random.randint(0, len(아이디3_리스트)-1)]
    else:
        아이디 += str(random.randint(0, 9))
    if random.choice([True, False]):
        아이디 += str(random.randint(0, 9))
    if len(아이디) > 15:
        아이디 = 아이디[:15]
    page.fill('input[name="tbMemID"]', 아이디)
    page.locator("text=중복확인").click()
    page.fill('input[name="tbMemPass"]', 비밀번호)
    page.fill('input[name="tbMemPass2"]', 비밀번호)

    # 전화번호
    page.fill('input[name="tbMobile1"]', '010')
    중간번호 = ''.join(str(random.randint(0,9)) for _ in range(4))
    끝번호   = ''.join(str(random.randint(0,9)) for _ in range(4))
    page.fill('input[name="tbMobile2"]', 중간번호)
    page.fill('input[name="tbMobile3"]', 끝번호)

    # 생년월일
    나이     = random.randint(11, 13)
    출생년도 = 2026 - 나이
    page.select_option('select[name="ddlBirthDay1"]', value=str(출생년도))
    page.select_option('select[name="ddlBirthDay2"]', value=f"{random.randint(1,12):02}")
    page.select_option('select[name="ddlBirthDay3"]', value=f"{random.randint(1,28):02}")

    # 학교 & 주소
    학교선택 = random.randint(0, len(학교_리스트)-1)
    학교     = 학교_리스트[학교선택]
    page.select_option('select[name="ddlAcaName1"]', value=학교)
    page.fill('input[name="tbGrade1"]', str(나이 - 7))
    page.fill('input[name="tbClass1"]', str(random.randint(1,5)))
    page.click("span:text('우편번호 찾기')")
    time.sleep(2)
    page.keyboard.type(아파트_리스트[학교선택])
    time.sleep(1)
    page.keyboard.press('Enter')
    time.sleep(1)
    for _ in range(6):
        page.keyboard.press('Tab')
    page.keyboard.press('Enter')
    time.sleep(1)
    호   = f"{random.randint(1,5)}0{random.randint(1,9)}"
    주소 = f"{동_리스트[학교선택]} {호}호"
    page.fill('input[name="tbAddr2"]', 주소)
    주소 = f"{아파트_리스트[학교선택]} {주소}"

    # 부모 정보
    부모성별 = random.randint(0,2)
    if 부모성별 < 1:
        부모이름 = f"{아이성}{부_리스트[random.randint(0, len(부_리스트)-1)]}"
    else:
        부모이름 = f"{random.choices(성씨, weights=weights, k=1)[0]}{모_리스트[random.randint(0, len(모_리스트)-1)]}"
    page.fill('input[name="tbPName"]', 부모이름)
    page.fill('input[name="tbPMobile1"]', '010')
    page.fill('input[name="tbPMobile2"]', 중간번호)
    page.fill('input[name="tbPMobile3"]', 끝번호)

    # 이메일
    포털 = ["@gmail.com","@naver.com","@daum.net","@nate.com"]
    page.fill('input[name="tbMemEmail"]', f"{아이디}{random.choice(포털)}")

    page.click("#rdRoute1")
    time.sleep(1)
    page.wait_for_selector("span:text('회원가입')", state="visible")
    page.once('dialog', handle_alert)
    page.click("span:text('회원가입')")
    for _ in range(3):
        time.sleep(1)
        page.keyboard.press('Enter')
    wc = random.randint(0,1)
    if wc ==  0:
        요일 = "월수"
    else:
        요일 = "화목"
    # 기록 저장
    엑셀_초기화_및_데이터_저장(sheet_name, 이름, 아이디, 나이, 요일, 학교, 주소)

# --- 수강신청 로직 ----------------------------------------------------------
def 신청(page, sheet_name):
    # 2) 페이지 이동 및 초기 클릭
    page.goto(수강신청사이트)
    time.sleep(1)
    if page.locator('input#q1_2').count() > 0:
        page.locator('input#q1_2').click()
        time.sleep(1)

    # 3) 요일·회차 선택 (BG / PH 분기)
    if sheet_name == "BG":
        if 요일 == "월수":
            page.locator('label.cc-cc.check[for="3_19"]').click()
        else:
            page.locator('label.cc-cc.check[for="4_20"]').click()
    elif sheet_name == "PH":   
        if 요일 == "월수":
            page.locator('button.btn_week[data-week="2,4"]').click()
            time.sleep(1)
            page.locator('label.cc-cc.check[for="1_53"]').click()
        else:
            page.locator('button.btn_week[data-week="3,5"]').click()
            time.sleep(1)
            page.locator('label.cc-cc.check[for="2_54"]').click()
        time.sleep(1)

    # 4) 수강신청 버튼 클릭 (팝업 처리)
    page.once('dialog', handle_alert)
    page.locator('a.btn_type5.mb30:has-text("수강신청")').click()
    time.sleep(1)
    page.keyboard.press('Enter')
    time.sleep(1)

    # 5) 설문 응답 — 있는 만큼만 동적으로 클릭
    page.wait_for_selector('input#btn_poll', timeout=10000)
    poll_buttons = page.locator('input[id^="q"][id$="_1"]')
    total = poll_buttons.count()
    for idx in range(total):
        poll_buttons.nth(idx).click()

    # 6) 나머지 버튼 클릭 및 완료
    page.click('input#btn_poll')
    time.sleep(1)
    page.click('input#cbAddress')
    time.sleep(1)
    page.click('input#cbPc')
    time.sleep(1)
    page.once('dialog', handle_alert)
    page.click('a:has(span:text("신청"))')
    time.sleep(1)
    page.keyboard.press('Enter')
    time.sleep(1)

    print(f"{이름} 신청 완료")
    time.sleep(random.randint(랜덤최소, 랜덤최대))


def 동작():
    """전체 흐름: 설정 로드 → playwright 실행 → PH/BG 반복 처리."""
    if not os.path.exists(사용자_데이터_디렉토리):
        os.makedirs(사용자_데이터_디렉토리)

    초기화()
    with sync_playwright() as playwright:
        context = playwright.firefox.launch_persistent_context(
            user_data_dir=사용자_데이터_디렉토리,
            headless=False,
            args=['--disable-popup-blocking']
        )
        page = context.new_page()  
        
        # BG 시트 반복 처리
        for _ in range(반복횟수):
            회원가입(page, "BG")
            신청(page,"BG")

        time.sleep(5)
        context.close()

if __name__ == "__main__":
    동작()