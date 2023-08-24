import asyncio
import re
import os
from playwright.async_api import async_playwright
import openpyxl

fm = 1
sS = 2
mS = 3
lS = 5
lsS = 7
llS = 10
강의날짜 = 202308
아이디 = None
반이름 = None
학생이름 = None
page = None
browser = None
new_handle = None

폴더경로 = "os.path.dirname(os.path.abspath(__file__))"

async def 로그인():
    global page, new_handle  # 전역 변수로 사용
    await page.goto('https://enozsw-bukgu.enoz.kr/Admin') # 로그인 사이트로 이동
    await page.wait_for_load_state()
    await asyncio.sleep(sS)
    await page.fill('input[name="tbAdminId"]', 'admin') # 아이디 및 비밀번호 입력하고 로그인
    await page.fill('input[name="tbAdminPass"]', 'admin55&&')
    await asyncio.sleep(sS)
    await page.press('input[name="tbAdminPass"]', 'Enter')
    await asyncio.sleep(sS)
    await page.goto('https://enozsw-bukgu.enoz.kr/Admin/Class/StudyList.asp') # 수강 관리로 이동
    await asyncio.sleep(sS)
    await page.select_option('select[name="ddlKeyField"]', value='b.m_id') # 아이디로 검색으로 바꾸기
    await asyncio.sleep(sS)

async def 반배정():
    global page, new_handle  # 전역 변수로 사용
    
    # 엑셀 파일 열기
    excel_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '반배정.xlsx')
    wb = openpyxl.load_workbook(excel_file_path)
    ws = wb.active
    
    for row in ws.iter_rows(min_row=2, values_only=True):  # 첫 번째 행은 헤더이므로 건너뜁니다.
        반이름 = row[0]
        아이디 = row[1]
        학생이름 = row[2]
        
        await page.fill('input[name="tbKeyWord"].font_blue', 아이디)   # 아이디 검색
        await page.press('input[name="tbKeyWord"].font_blue', 'Enter')
        await asyncio.sleep(mS)
        await page.click(f'a[href*="{강의날짜}"].button_red_small') # 강의 날짜에 맞는 것으로 선택
        await asyncio.sleep(mS)
        new_handle = None # 새로 열린 창 핸들 얻기
        while not new_handle:
            for handle in browser.contexts[0].pages:
                if handle != page:
                    new_handle = handle
                    break
            await asyncio.sleep(sS)
            
            await new_handle.evaluate('''(name) => { 
            const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
            for (const option of selectElement.options) {
                if (option.textContent.includes(name)) {
                    option.selected = true;
                    const event = new Event('change', { bubbles: true });
                    selectElement.dispatchEvent(event);
                    break;
                }
            }
        }''', 반이름) # 반이름에 해당되는 항목 선택
        
        new_handle.on('dialog', lambda dialog: asyncio.ensure_future(handle_alert(new_handle, dialog))) # Alert 팝업창 핸들링
        
        await asyncio.sleep(mS)
        await new_handle.click('a.button_yellow.bold:has-text("수강 변경")') ## 수강 변경 클릭
        
        await asyncio.sleep(sS)
        await page.bring_to_front()
        await asyncio.sleep(sS)
        print(학생이름,"(",아이디,")",반이름,"로 배정 완료") 
        
    # 엑셀 파일 닫기
    wb.close()

# 'dialog' 이벤트 핸들러
async def handle_alert(page, dialog):
    await dialog.accept()


async def 동작():
    global browser, page, item  # 전역 변수로 사용
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
            args=['--disable-popup-blocking']
        )
        page = await browser.new_page(accept_downloads=True)
        await 로그인()
        await 반배정()
        print("코드 종료")
        await browser.close() # 브라우저 종료

asyncio.run(동작())

