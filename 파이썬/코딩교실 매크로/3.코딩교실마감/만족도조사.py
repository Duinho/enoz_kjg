from playwright.sync_api import sync_playwright
import numpy as np
import time

def mj(link, repeat, evaluation_count, satisfaction_count):
    """UI에서 입력받은 값을 기반으로 자동화를 수행"""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        for _ in range(repeat):  # 반복 횟수만큼 반복
            page.goto(link)  # 링크로 이동
            if evaluation_count > 0:
                process_evaluation(page, evaluation_count)
            if satisfaction_count > 0:
                process_satisfaction(page, satisfaction_count)
        time.sleep(0.5)
        
        browser.close()

def process_evaluation(page, count):
    """역량 향상 평가 문항 처리"""
    page.wait_for_selector('span.NPEfkd.RveJvd.snByac', timeout=10000)
    col_a = np.random.choice([5, 4, 3, 2, 1], size=count, p=[0.985, 0.009, 0.004, 0.0015, 0.0005])
    for j in range(1, len(col_a)):
        col_a[j] += 5 * j
    elements = page.query_selector_all('.AB7Lab.Id5V1')
    for k in range(count):
        elements[col_a[k] - 1].click()
    # 다음 버튼 클릭
    elements = page.query_selector_all('span.NPEfkd.RveJvd.snByac')
    for element in elements:
        if element.inner_text() == '다음':
            element.click()
            break 

def process_satisfaction(page, count):
    """만족도 조사 문항 처리"""
    page.wait_for_selector('span.NPEfkd.RveJvd.snByac', timeout=10000)  # 제출 버튼이 나올 때까지 대기
    col_a = np.random.choice([5, 4, 3, 2, 1], size=count, p=[0.985, 0.009, 0.004, 0.0015, 0.0005])
    for j in range(1, len(col_a)):
        col_a[j] += 5 * j
    elements = page.query_selector_all('.AB7Lab.Id5V1')
    for k in range(count):
        elements[col_a[k] - 1].click()
    # 제출 버튼 클릭
    elements = page.query_selector_all('span.NPEfkd.RveJvd.snByac')
    for element in elements:
        if element.inner_text() == '제출':
            element.click()
            break
