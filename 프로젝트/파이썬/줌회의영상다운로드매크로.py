import asyncio
import re
import os
import sys
from playwright.async_api import async_playwright


fm = None
err = None
강의이름 = None
강의날짜 = None
폴더이름 = None
폴더정보 = None
download = None
item = None
page = None
browser = None
new_handle = None

폴더경로 = os.path.dirname(os.path.abspath(__file__))

async def 로그인():
    global page                                                                       # 전역 변수로 사용
    await page.goto('https://us02web.zoom.us/signin')                                 # Zoom 로그인 페이지로 이동
    await page.wait_for_load_state()
    await page.wait_for_selector('button#onetrust-accept-btn-handler', timeout=10000) # 쿠키 허용 버튼 클릭
    await page.click('button#onetrust-accept-btn-handler')
    await asyncio.sleep(3)
    await page.fill('input#email', 'pds0335@hanmail.net')                             # 이메일 및 비밀번호 입력하고 로그인
    await page.fill('input#pa1word', 'Enoz7223')
    await asyncio.sleep(1)
    await page.pre1('#pa1word', 'Enter')     
    await page.wait_for_url("*profile")
    await page.goto('https://us02web.zoom.us/recording/management')                   # 기록관리 페이지로 이동
    await asyncio.sleep(1)
    await page.wait_for_selector('h1[data-v-d8466eb2]:has-text("기록 관리")', timeout=30000)
    await asyncio.sleep(3)
    
    
    
async def 정보가져오기():
    global page, 강의이름, 강의날짜, 폴더정보, fm, err
    try:
        fm = await page.query_selector('span[role="alert"]:has-text("검색과 일치하는 결과를 찾을 수 없습니다")')
        if fm:                                                                                                  # 첫 번째 회의 링크가 없으면 종료(다운로드 받을 회의가 없으면)
            print("모든 영상 다운로드 완료")
            await browser.close()
            sys.exit()
        link_element = await page.query_selector('a.mgb-0.cursor-pointer.topic-actived')                        # 첫 번째 회의 링크 찾기        
        await link_element.click()
        await page.wait_for_selector('span.meeting-topic', timeout=30000)
        await asyncio.sleep(1)
        topic_element = await page.query_selector('span.meeting-topic')                                         # 회의 주제(타이틀) 가져오기
        if topic_element:
            강의이름 = await topic_element.inner_text()                                                          # 강의 이름 가져오기
        date_element = await page.query_selector('span.mgr-md')                                                 # 날짜 값 가져오기
        if date_element:
            date_text = await date_element.inner_text()                                                         # 정규식을 사용하여 날짜 값을 추출
            pattern = r'(\d+년 \d+월 \d+일)'
            matches = re.search(pattern, date_text)
            강의날짜 = matches.group(1)
            폴더이름 = f"{강의이름}_{강의날짜}"                                                                   # 폴더 경로 설정 및 생성
            폴더정보 = os.path.join(폴더경로, '녹화영상', 강의날짜, 폴더이름)
            os.makedirs(폴더정보, exist_ok=True)
    except Exception as e:
        print(f"{강의이름}정보가져오기에서 오류 발생: {e}")                                                        # 디버깅을 위한 오류 위치 출력    
        err = 1
      
        
async def 영상다운(이름):
    global item, browser, 폴더정보, 강의이름, 강의날짜, new_handle, err                                            # 전역 변수로 사용
    try:
        await item.click()    
        new_handle = None                                                                                        # 새로 열린 창 핸들 얻기
        while not new_handle:
            for handle in browser.contexts[0].pages:
                if handle != page:
                    new_handle = handle
                    break
                await asyncio.sleep(1)    
        await new_handle.wait_for_selector('a.download-btn', timeout=30000)
        dl_element = await new_handle.query_selector('a.download-btn')                                          # 다운로드 버튼을 찾기
        if dl_element:
            async with new_handle.expect_download() as download_info:
                await dl_element.click()  
                download = await download_info.value
                await download.path()
            await download.save_as(os.path.join(폴더정보, f"{강의이름}_{이름}_{강의날짜}.mp4"))                   # 지정한 폴더에 다운로드하고 이름 바꾸기
            await new_handle.close()
            new_handle = None
            await page.wait_for_selector('span.meeting-topic', timeout=30000)
            await asyncio.sleep(1)
    except Exception as e:
        print(f"{강의이름}의 {이름} 영상다운에서 오류 발생: {e}")                                                 # 디버깅을 위한 오류 위치 출력
        if new_handle:
            await new_handle.close()
            err = 1
            
    
async def 삭제():
    global page, err                                                                                                       # 전역 변수로 사용
    try:
        if err:
            await page.goto('https://us02web.zoom.us/recording/management')                                                # 기록관리 페이지로 이동
            await asyncio.sleep(1)
            await page.wait_for_selector('h1[data-v-d8466eb2]:has-text("기록 관리")', timeout=30000)
            print(f"{강의이름}설치 재시작")              
            await asyncio.sleep(1)
            err = None
            
        else :
            delete_element = await page.query_selector('button:nth-child(3)')                                              # 삭제
            if delete_element:
                await delete_element.click()                                                                               # 버튼 누르기
                await asyncio.sleep(1)
                delete1_element = await page.query_selector('button.zm-button--primary.zm-button--small.zm-button > span') # 휴지통으로 이동           
                await asyncio.sleep(1)
                if delete1_element: 
                    await page.get_by_role("button", name="휴지통으로 이동").click()                                        # 버튼 누르기
                    await asyncio.sleep(1)
                    await page.wait_for_load_state()            
            await asyncio.sleep(1)
            await page.reload() 
            await page.wait_for_selector('text=휴지통', timeout=30000)
            await asyncio.sleep(2)
    except Exception as e:
        print(f"{강의이름}삭제에서 오류 발생: {e}")                                                                         # 디버깅을 위한 오류 위치 출력
        await page.goto('https://us02web.zoom.us/recording/management')                                                   # 기록관리 페이지로 이동
        await asyncio.sleep(1)
        await page.wait_for_selector('h1[data-v-d8466eb2]:has-text("기록 관리")', timeout=30000)
        print(f"{강의이름}설치 재시작")           
        await asyncio.sleep(3)

    
async def 동작():
    global browser, page, item, err                                                            # 전역 변수로 사용
    async with async_playwright() as playwright:                                               # 크로미움 브라우저 열기
        browser = await playwright.chromium.launch(
            headle1=False,
        )
        page = await browser.new_page(accept_downloads=True)                                   # 새로운 창이 열리면 page에 저장
        await 로그인()
        while(1):
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
            await 삭제()

asyncio.run(동작())
