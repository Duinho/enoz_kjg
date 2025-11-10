# 만족도조사.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import numpy as np
import time

# 5점 편향 확률 (값 배열 [5,4,3,2,1]과 순서 일치)
_PROBS_5_TO_1 = np.array([0.985, 0.009, 0.004, 0.0015, 0.0005])

def mj(link: str, repeat: int, evaluation_count: int, satisfaction_count: int):
    """UI에서 입력받은 값으로 설문 자동화"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for _ in range(repeat):
            page.goto(link)
            page.wait_for_load_state("networkidle")

            if evaluation_count > 0:
                process_evaluation(page, evaluation_count)

            if satisfaction_count > 0:
                process_satisfaction(page, satisfaction_count)

            time.sleep(0.2)

        browser.close()

# ---------- 내부 유틸 ----------

def _sample_scores(num_questions: int) -> np.ndarray:
    """문항 수만큼 [5,4,3,2,1] 점수에서 샘플링(5점 확률이 가장 큼)"""
    return np.random.choice([5, 4, 3, 2, 1], size=num_questions, p=_PROBS_5_TO_1)

def _score_to_index(score: int, n_options: int) -> int:
    """
    점수(1~5)를 보기 개수 n_options의 0-based 인덱스로 매핑.
    좌→우 = 1→5 가정. score↑ ⇒ 오른쪽으로 이동.
    """
    if n_options <= 1:
        return 0
    # score=1 -> 0, score=5 -> n_options-1
    pos = round((score - 1) * (n_options - 1) / 4)
    return int(max(0, min(pos, n_options - 1)))

def _query_radio_items(group):
    """
    라디오 버튼 요소 목록 조회.
    구글폼 테마에 따라 클래스가 달라질 수 있어 보조 셀렉터도 시도.
    """
    radios = group.query_selector_all('.AB7Lab.Id5V1')
    if not radios:
        radios = group.query_selector_all('[role="radio"]')
    return radios

def _click_likert_on_page(page, expected_count: int):
    """
    현재 페이지에서 라디오 문항 최대 expected_count개 처리.
    각 문항의 실제 보기 수를 읽고 확률적으로 선택.
    """
    page.wait_for_selector('[role="radiogroup"]', timeout=10000)
    groups_all = page.query_selector_all('[role="radiogroup"]')

    radio_groups = []
    per_counts = []
    for g in groups_all:
        radios = _query_radio_items(g)
        if radios:
            radio_groups.append(g)
            per_counts.append(len(radios))

    n = min(expected_count, len(radio_groups))
    if n == 0:
        return

    scores = _sample_scores(n)

    for i in range(n):
        radios = _query_radio_items(radio_groups[i])
        if not radios:
            continue
        idx = _score_to_index(int(scores[i]), len(radios))
        radios[idx].click()

def _click_by_text(page, text: str):
    """버튼 텍스트로 클릭 시도(정확히 일치). 실패해도 예외를 터뜨리지 않음."""
    try:
        page.get_by_text(text, exact=True).click()
        page.wait_for_load_state("networkidle")
    except PlaywrightTimeoutError:
        pass
    except Exception:
        pass

# ---------- 페이지 처리 ----------

def process_evaluation(page, count: int):
    """역량 향상 평가 페이지 처리"""
    # 설문 첫 화면에 '다음'만 있는 경우 대비
    try:
        # 라디오가 없고 '다음'이 보이면 먼저 넘김
        has_radios = bool(page.query_selector('[role="radiogroup"]'))
        if not has_radios:
            el = page.get_by_text("다음", exact=True)
            if el:
                el.click()
                page.wait_for_load_state("networkidle")
    except Exception:
        pass

    _click_likert_on_page(page, count)
    _click_by_text(page, "다음")

def process_satisfaction(page, count: int):
    """만족도 조사 페이지 처리"""
    _click_likert_on_page(page, count)
    _click_by_text(page, "제출")
