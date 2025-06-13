import os
import openpyxl
from playwright.sync_api import sync_playwright

# 변수 선언
폴더경로 = os.path.dirname(os.path.abspath(__file__))  # 지금 코드 파일이 있는 위치를 저장
excel_file_path = os.path.join(폴더경로, 'LMS전산반배정.xlsx')  # 엑셀 파일 경로

def 초기화():
    global wb, ws
    wb = openpyxl.load_workbook(excel_file_path)
    ws = wb.active

def 로그인(page):
    # 로그인 사이트 정보를 읽어옴
    global 강의날짜
    로그인사이트 = ws.cell(row=1, column=17).value
    adminID = ws.cell(row=2, column=17).value
    adminPW = ws.cell(row=3, column=17).value
    수강관리링크 = ws.cell(row=4, column=17).value
    강의날짜 = ws.cell(row=5, column=17).value

    # 로그인 프로세스
    page.goto(로그인사이트)
    page.fill('input[name="tbAdminId"]', adminID)
    page.fill('input[name="tbAdminPass"]', adminPW)
    page.press('input[name="tbAdminPass"]', 'Enter')
    page.goto(수강관리링크)
    page.select_option('select[name="ddlTargetDate"]', value=str(강의날짜))
    page.select_option('select[name="ddlKeyField"]', value='b.m_id')

def 반배정(page, 대상):
    # 대상에 따른 열 인덱스 설정
    if 대상 == '학생배정':
        col_range = slice(0, 3)  # A ~ C
    elif 대상 == '망령출동':
        col_range = slice(5, 8)  # F ~ H
    elif 대상 == '망령퇴장':
        col_range = slice(10, 13)  # K ~ M

    마지막_행 = ws.max_row
    for row in ws.iter_rows(min_row=2, max_row=마지막_행, values_only=True):
        반이름, 학생이름, 아이디 = row[col_range]

        아이디 = f'{아이디}' if 아이디 is not None else None  # 아이디가 None인 경우 처리

        if 아이디 is None:  # 아이디가 None인 경우 현재 프로세스 종료
            print(f"{대상}에서 처리할 아이디가 없습니다. 다음으로 넘어갑니다.")
            return  # 현재 반배정 함수 종료

        page.fill('input[name="tbKeyWord"].font_blue', 아이디)
        page.press('input[name="tbKeyWord"].font_blue', 'Enter')

        # 해당 날짜와 맞는 링크를 클릭
        page.click(f'a[href*="{강의날짜}"].button_red_small')

        # 새 탭이 열릴 때까지 기다림
        new_page = browser.contexts[0].wait_for_event("page")
        new_page.wait_for_load_state("load")
        
        # 새 탭에서 반이름 선택
        new_page.evaluate('''(name) => { 
            const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
            for (const option of selectElement.options) {
                if (option.textContent.includes(name)) {
                    option.selected = true;
                    const event = new Event('change', { bubbles: true });
                    selectElement.dispatchEvent(event);
                    break;
                }
            }
        }''', 반이름)

        # 팝업 대화 상자 핸들링
        new_page.once('dialog', lambda dialog: dialog.accept())
        
        # 수강 변경 버튼 클릭
        new_page.locator('a.button_yellow.bold:has-text("수강 변경"), a.button_red.bold:has-text("수강 인원이 모두 찼습니다. (변경불가 => 가능)")').click()

        new_page.close()
        page.bring_to_front()
        print(f"{학생이름}({아이디})이(가) {반이름}으로 배정 완료")

def 동작():
    global browser
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=['--disable-popup-blocking'])
        page = browser.new_page()
        초기화()
        로그인(page)
        
        # 각 배정 과정을 순서대로 실행
        #반배정(page, '망령출동')
        반배정(page, '학생배정')
        #반배정(page, '망령퇴장')

        browser.close()

동작()
