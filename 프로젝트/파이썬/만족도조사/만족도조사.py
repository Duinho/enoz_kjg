import asyncio
import openpyxl
import os
from docx import Document
from docx.shared import RGBColor
import win32com.client as win32
from playwright.async_api import async_playwright
import numpy as np


result = 0
page = None
browser = None
col_9 = None



async def 엑셀():
    global col_9

    desktop_path = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(desktop_path, '만족도조사리스트.xlsx')
    wb = openpyxl.load_workbook(excel_file, data_only=True)
    sheet = wb.active

    col_9 = [sheet[f"A{i}"].value for i in range(2, sheet.max_row + 1)]
    print(col_9)
    wb.close()
     
 
async def 시험():
    global page, col_9
    for i in range(len(col_9)):
        await page.goto('https://forms.gle/W8iM32CbPtJSsjrW9')
        await page.wait_for_selector('span.NPEfkd.RveJvd.snByac', timeout=10000)
        col_a = np.random.choice([5, 4], size=8, p=[0.95, 0.05])
        
        for j in range(1, len(col_a)):
            col_a[j] += 5*j
        
        elements = await page.query_selector_all('.AB7Lab.Id5V1')
        
        for k in range(0,8):
            await elements[col_a[k]-1].click()
    
        await page.fill('textarea[aria-labelledby="i33"]', str(col_9[i]))
        #await page.click('span.NPEfkd.RveJvd.snByac')
        



async def 동작():
    global browser, page  # 전역 변수로 사용
    
    await 엑셀()
    
    async with async_playwright() as playwright: # 크로미움 브라우저 열기
        browser = await playwright.chromium.launch(
            headless=False,
        )
        page = await browser.new_page(accept_downloads=True) # 새로운 창이 열리면 page에 저장
        await 시험()
    
asyncio.run(동작())
