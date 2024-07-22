import re
import os
import openpyxl
from openpyxl.utils import get_column_letter
from playwright.sync_api import sync_playwright
import win32com.client as win32
import time

result = 0
폴더경로 = os.path.dirname(os.path.abspath(__file__))  # 폴더경로를 코드가 있는 디렉토리로 저장
excel_file_path = os.path.join(폴더경로, '학교알리미학생수.xlsx')  # 엑셀 파일 경로

def 엑셀():
    global 학교알리미주소, 학교, 시도, 시군구, 학년
    wb = openpyxl.load_workbook(excel_file_path)
    ws = wb['정보']
    학교알리미주소 = ws.cell(row=1, column=17).value
    학교 = ws.cell(row=2, column=17).value
    시도 = ws.cell(row=3, column=17).value
    시군구 = ws.cell(row=4, column=17).value
    if "초등학교" in 학교:
        학년 = ['1', '2', '3', '4', '5', '6']
    else:
        학년 = ['1', '2', '3']
    wb.close()
    return ws

def 헤더추가(ws):
    headers = ['학교명', '1학년', '2학년', '3학년', '4학년', '5학년', '6학년', '합계']
    for col_index, header in enumerate(headers, start=1):
        ws.cell(row=1, column=col_index, value=header)

def 학년받아오기(page):
    page.goto(학교알리미주소)
    radio_buttons = page.query_selector_all('input[name="level1"]')
    for radio in radio_buttons:
        label = page.query_selector(f'label[for="{radio.get_attribute("id")}"]')
        if label and 학교 in label.inner_text():
            label.click()
            page.wait_for_load_state('load')   
            break
    radio_buttons = page.query_selector_all('input[name="level2"]')
    for radio in radio_buttons:
        label = page.query_selector(f'label[for="{radio.get_attribute("id")}"]')
        if label and 시도 in label.inner_text():
            label.click()
            page.wait_for_load_state('load')   
            break
    radio_buttons = page.query_selector_all('input[name="level3"]')
    for radio in radio_buttons:
        label = page.query_selector(f'label[for="{radio.get_attribute("id")}"]')
        if label and 시군구 in label.inner_text():
            label.click()
            page.wait_for_load_state('load') 
            break 
    학교명 = []
    labels = page.query_selector_all('label[for^="shlCd"]')
    for label in labels:
        학교명.append(label.inner_text())
    return 학교명

def 학교정보검색(page, 학교명, 학년, ws):
    row_index = 2  # 첫 번째 줄은 헤더이므로 두 번째 줄부터 시작
    for 학교 in 학교명:
        label = page.query_selector(f'label:has-text("{학교}")')
        if label:
            label.click()
            page.wait_for_load_state('load')   
            page.click('a[data-tab-id="tabSel"]')
            page.wait_for_load_state('load')   
            page.click('a.accordian_title:has-text("학생현황")')
            page.wait_for_load_state('load')   
            page.click('label[for="hangmok03"]')
            page.wait_for_load_state('load')   
            page.click('#webSearchButton')
            time.sleep(0.1)
            page.wait_for_load_state('load')   
            # 숫자로 변환하여 저장하는 부분 수정
            values = []
            row_header = page.query_selector('th:has-text("합 계")')
            if row_header:
                parent_row = row_header.evaluate_handle('el => el.parentElement')
                for grade in 학년:
                    index = (int(grade) * 3) + 1  # 학년 값에 따라 올바른 번째의 셀 선택
                    selector = f'td:nth-child({index})'
                    value = parent_row.query_selector(selector).inner_text()
                    values.append(int(value.replace(',', '')))  # 숫자로 변환하여 리스트에 추가

            # 학교명과 values를 엑셀 파일에 저장
            ws.cell(row=row_index, column=1, value=학교)
            for col_index, value in enumerate(values, start=2):
                ws.cell(row=row_index, column=col_index, value=value)

            row_index += 1  # 다음 줄로 이동
            print(f'{학교} 학생 수 저장 완료')
            page.click('a.slidedown[href="javascript:research();"]')
            time.sleep(0.1)
            page.wait_for_load_state('load')   

def 동작():
    global browser, page  # 전역 변수로 사용
    with sync_playwright() as p:  # 크로미움 브라우저 열기
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()  # 새로운 창이 열리면 page에 저장
        ws = 엑셀()
        헤더추가(ws)  # 헤더 추가
        학교명 = 학년받아오기(page)
        학교정보검색(page, 학교명, 학년, ws)
        ws.parent.save(excel_file_path)  # 엑셀 파일 저장
        print('모든 학교 저장 완료')
        browser.close()  # 브라우저 닫기

동작()
