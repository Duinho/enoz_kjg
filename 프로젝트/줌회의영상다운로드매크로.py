import asyncio
import re
import os
from playwright.async_api import async_playwright

fm = 1
sS = 2
mS = 3
lS = 5
llS = 10
강의이름 = None
강의날짜 = None
폴더이름 = None
폴더정보 = None
download = None
item = None
page = None
browser = None
new_handle = None

폴더경로 = "os.path.dirname(os.path.abspath(__file__))"

async def 로그인():
    global page  # 전역 변수로 사용
    await page.goto('https://us02web.zoom.us/signin') # Zoom 로그인 페이지로 이동
    await page.wait_for_load_state()
    await asyncio.sleep(sS)
    await page.wait_for_selector('button#onetrust-accept-btn-handler', timeout=10000) # 쿠키 허용 버튼 클릭
    await page.click('button#onetrust-accept-btn-handler')
    await asyncio.sleep(sS)
    await page.fill('input#email', 'pds0335@hanmail.net') # 이메일 및 비밀번호 입력하고 로그인
    await page.fill('input#password', 'Enoz7223')
    await asyncio.sleep(sS)
    await page.press('#password', 'Enter')     
    await page.wait_for_url("*profile")
    await page.goto('https://us02web.zoom.us/recording/management') # 기록관리 페이지로 이동
    await asyncio.sleep(sS)
    await page.wait_for_selector('a.mgb-0.cursor-pointer.topic-actived', timeout=30000)
    
    
async def 정보가져오기():
    global page, 강의이름, 강의날짜, 폴더정보, fm
    fm = 1
    link_element = await page.query_selector('a.mgb-0.cursor-pointer.topic-actived') # 첫 번째 회의 링크 찾기
    if link_element is None: # 첫 번째 회의 링크가 없으면 종료(다운로드 받을 회의가 없으면)
        fm = 0
    await link_element.click()
    await page.wait_for_selector('span.meeting-topic', timeout=30000)
    await asyncio.sleep(sS)
    topic_element = await page.query_selector('span.meeting-topic') # 회의 주제(타이틀) 가져오기
    if topic_element:
        강의이름 = await topic_element.inner_text()
    date_selector = 'span.mgr-md' # 날짜 값 가져오기
    date_element = await page.query_selector(date_selector)
    if date_element:
        date_text = await date_element.inner_text() # 정규식을 사용하여 날짜 값을 추출
        pattern = r'(\d+년 \d+월 \d+일)'
        matches = re.search(pattern, date_text)
        if matches:
            강의날짜 = matches.group(1)
        폴더이름 = f"{강의이름}_{강의날짜}" # 폴더 경로 설정 및 생성
        폴더정보 = os.path.join(폴더경로, 폴더이름)
        os.makedirs(폴더정보, exist_ok=True)
        
        
async def 영상다운(이름):
    global item, browser, 폴더정보, 강의이름, 강의날짜, new_handle  # 전역 변수로 사용
    await item.click()            
    await asyncio.sleep(lS)
    new_handle = None # 새로 열린 창 핸들 얻기
    while not new_handle:
        for handle in browser.contexts[0].pages:
            if handle != page:
                new_handle = handle
                break
        await asyncio.sleep(sS)
    dl_element = await new_handle.query_selector('a.download-btn')
    await asyncio.sleep(mS)
    if dl_element:
        async with new_handle.expect_download() as download_info:
            await dl_element.click()
            download = await download_info.value
            await download.path()
    await download.save_as(os.path.join(폴더정보, f"{강의이름}_{이름}_{강의날짜}.mp4"))
    await new_handle.close()    
    await asyncio.sleep(mS)
    await page.wait_for_selector('span.meeting-topic', timeout=30000)
     
    
async def 삭제():
    global page  # 전역 변수로 사용
    c = 0
    while c :
        delete_element = await page.query_selector('button:nth-child(3)')
        if delete_element:
            await delete_element.click()
            await asyncio.sleep(mS)
            delete1_selector = 'button.zm-button--primary.zm-button--small.zm-button > span'
            print("버튼지정")
            await asyncio.sleep(sS)
            print("버튼찾기다리기")
            delete1_element = await page.query_selector(delete1_selector)
            print("버튼찾기")
            if delete1_element: 
                print("버튼클릭")
                await page.get_by_role("button", name="휴지통으로 이동").click()
                await asyncio.sleep(mS)
        else:
            c = 1              
    await page.wait_for_load_state()
    await asyncio.sleep(sS)
    await page.reload() 
    await asyncio.sleep(lS)
    
    
async def 동작():
    global browser, page, item  # 전역 변수로 사용
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
        )
        page = await browser.new_page(accept_downloads=True)
        await 로그인()
        while fm:
            await 정보가져오기()
            downloadlist = await page.query_selector_all('div.item_list_header.relative > a')  # 영상 다운로드 하기 위해 각 항목으로 접속
            for item in downloadlist:
                inner_text = await item.inner_text()
                if inner_text == "발표자 보기가 포함된 공유 화면":
                    await 영상다운('발표자 공유화면')
                if inner_text == "갤러리 보기가 포함된 공유 화면":
                    await 영상다운('갤러리 공유화면')
                if inner_text == "갤러리 보기":
                    await 영상다운('갤러리')
                if inner_text == "발표자 보기가 포함된 공유 화면":
                    await 영상다운('발표자 공유화면2')
                if inner_text == "갤러리 보기가 포함된 공유 화면":
                    await 영상다운('갤러리 공유화면2')
                if inner_text == "갤러리 보기2":
                    await 영상다운('갤러리2')
            await 삭제()
        await browser.close() # 브라우저 종료

asyncio.run(동작())
