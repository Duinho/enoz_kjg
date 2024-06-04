import re
import os
import sys
import time
from playwright.sync_api import sync_playwright

폴더경로 = os.path.dirname(os.path.abspath(__file__))
강의이름 = None
강의날짜 = None
폴더정보 = None

def 로그인(page):
    page.goto('https://us02web.zoom.us/signin')
    page.wait_for_load_state()
    page.click('button#onetrust-accept-btn-handler')
    page.fill('input#email', 'pds0335@hanmail.net')
    page.fill('input#password', 'Enoz7223')
    page.press('#password', 'Enter')
    page.wait_for_load_state()
    page.goto('https://us02web.zoom.us/recording/management')

def 정보가져오기(page):
    global 강의이름, 강의날짜, 폴더정보
    fm = page.query_selector('span[role="alert"]:has-text("검색과 일치하는 결과를 찾을 수 없습니다")')
    if fm:
        print("모든 영상 다운로드 완료")
        sys.exit()
    link_element = page.query_selector('a.mgb-0.cursor-pointer.topic-actived')
    link_element.click()
    page.wait_for_selector('span.meeting-topic', timeout=30000)
    topic_element = page.query_selector('span.meeting-topic')
    강의이름 = topic_element.inner_text()
    date_element = page.query_selector('span.mgr-md')
    date_text = date_element.inner_text()
    pattern = r'(\d+년 \d+월 \d+일)'
    matches = re.search(pattern, date_text)
    강의날짜 = matches.group(1)
    폴더이름 = f"{강의이름}_{강의날짜}"
    폴더정보 = os.path.join(폴더경로, '녹화영상', 강의날짜, 폴더이름)
    os.makedirs(폴더정보, exist_ok=True)

def 영상다운(page, 이름):
    item = page.query_selector(f'div.item_list_header.relative > a:has-text("{이름}")')
    if item:
        item.click()
        download_page = page.context.wait_for_page()
        download_button = download_page.query_selector('a.download-btn')
        download = download_button.click().save_as(os.path.join(폴더정보, f"{강의이름}_{이름}_{강의날짜}.mp4"))
        download_page.close()

def 삭제(page):
    delete_button = page.query_selector('button:has-text("삭제")')
    if delete_button:
        delete_button.click()
        confirm_button = page.wait_for_selector('button.zm-button--primary.zm-button--small.zm-button > span:has-text("휴지통으로 이동")')
        confirm_button.click()

def 동작():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,channel="chrome")
        page = browser.new_page(accept_downloads=True)
        로그인(page)
        while True:
            정보가져오기(page)
            영상다운(page, "발표자 보기가 포함된 공유 화면")
            영상다운(page, "갤러리 보기가 포함된 공유 화면")
            영상다운(page, "갤러리 보기")
            삭제(page)
        browser.close()

동작()
