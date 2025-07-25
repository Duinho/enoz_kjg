import os
import openpyxl
import re,datetime
import time
import shutil
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# ——————————————————————————————
# 설정
# ——————————————————————————————
BASE_DIR            = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH          = os.path.join(BASE_DIR, '보고서수정.xlsx')
REPORT_DIR          = os.path.join(BASE_DIR, '보고서')

# 전역 매핑
name_change_map      = {}
cancellation_map     = {}
additional_map       = {}
session_dates_map    = {}
session_descriptions = []


# ——————————————————————————————
# HTML 후처리 통합
# ——————————————————————————————
def process_html(path,
                 suffix_change=None,
                 attendance=None,
                 clear_fields=(),
                 education_idx=None,
                 additions=None):
    """
    HTML 문서 후처리 통합 함수
      1) suffix_change: (orig_num, new_num) 튜플로 Group No/담당강사명 교체
      2) attendance: (session_idx, cancels) 로 출결현황 + 취소자 처리
      3) clear_fields: 비울 레이블 리스트 (예: ('출결현황','특이사항'))
      4) education_idx: 차시 인덱스로 교육내용 삽입
      5) additions: 추가인원 이름 리스트로 [출] 삽입
    """
    with open(path, 'r', encoding='cp949', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 1) suffix 교체
    if suffix_change:
        o_num, n_num = suffix_change
        for lbl in ('Group No', '담당강사명'):
            td0 = soup.find('td', string=lbl)
            if td0:
                td1 = td0.find_next_sibling('td')
                txt = td1.get_text()
                td1.string = txt.rsplit('_', 1)[0] + '_' + n_num

    # 2) 출결현황 + 취소자
    if attendance:
        idx, cancels = attendance
        td0 = soup.find('td', string='출결현황')
        if td0:
            td1 = td0.find_next_sibling('td')
            students = [seg.split('[')[0].strip()
                        for seg in td1.get_text().split(',') if seg.strip()]
            new_p = soup.new_tag('p', **{'class':'MsoNormal'})
            for i, stu in enumerate(students, 1):
                cf = next((n for nm, n in cancels if nm == stu), None)
                status, color = ('결','#EE0000') if cf and idx>=cf else ('출','blue')
                sp0 = soup.new_tag('span', **{'class':'SpellE'}); sp0.string = stu
                sp1 = soup.new_tag('span', lang='EN-US', style=f'color:{color}'); sp1.string = f'[{status}]'
                new_p.append(sp0); new_p.append(sp1)
                if i < len(students): new_p.append(', ')
            # 누락 취소자
            for nm, cf in cancels:
                if nm not in students and idx>=cf:
                    if new_p.contents and not str(new_p.contents[-1]).endswith(', '):
                        new_p.append(', ')
                    sp0 = soup.new_tag('span', **{'class':'SpellE'}); sp0.string = nm
                    sp1 = soup.new_tag('span', lang='EN-US', style='color:#EE0000'); sp1.string = '[결]'
                    new_p.append(sp0); new_p.append(sp1)
            td1.clear()
            td1.append(new_p)

    # 3) clear_fields
    for lbl in clear_fields:
        td0 = soup.find('td', string=lbl)
        if td0:
            td0.find_next_sibling('td').clear()

    # 4) 교육내용 삽입
    if education_idx:
        td0 = soup.find('td', string='교육내용')
        if td0:
            td1 = td0.find_next_sibling('td')
            p = soup.new_tag('p', **{'class':'MsoNormal'})
            p.string = session_descriptions[education_idx-1]
            td1.clear()
            td1.append(p)

    # 5) 추가인원 [출] 삽입
    if additions:
        td0 = soup.find('td', string='출결현황')
        if td0:
            td1 = td0.find_next_sibling('td')
            # <p class="MsoNormal"> 태그 준비
            p = td1.find('p', class_='MsoNormal')
            if not p:
                p = soup.new_tag('p', **{'class':'MsoNormal'})
                td1.clear()
                td1.append(p)

            # 현재 p 안의 학생 이름 리스트
            existing = [span.get_text() for span in p.find_all('span', class_='SpellE')]

            for nm in additions:
                if nm not in existing:
                    # 기존 항목 뒤에 콤마+공백
                    if p.contents:
                        p.append(', ')
                    # 이름 span
                    sp0 = soup.new_tag('span', **{'class':'SpellE'})
                    sp0.string = nm
                    # 상태 span
                    sp1 = soup.new_tag('span', lang='EN-US', style='color:blue')
                    sp1.string = '[출]'
                    p.append(sp0)
                    p.append(sp1)
            # td1.append 가 아니라 p 내부에만 append 했으니 줄바꿈 파편 없음

    # 결과 저장
    with open(path, 'w', encoding='cp949', errors='ignore') as f:
        f.write(str(soup))



# ——————————————————————————————
# 설정 불러오기
# ——————————————————————————————
def 초기화():
    global 로그인사이트, 스케쥴관리링크, adminID, adminPW
    global 지역, 대상년월, 월수반, 화목반, 목표월수, 목표화목
    global session_descriptions, additional_map

    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb['메인']
    로그인사이트   = ws.cell(1,17).value
    스케쥴관리링크  = ws.cell(2,17).value
    adminID        = ws.cell(3,17).value
    adminPW        = ws.cell(4,17).value
    지역           = f"{ws.cell(5,17).value}_"
    대상년월       = ws.cell(6,17).value
    월수반         = ws.cell(7,17).value
    화목반         = ws.cell(8,17).value
    목표월수       = ws.cell(9,17).value
    목표화목       = ws.cell(10,17).value

    session_descriptions[:] = [ws.cell(i,19).value or '' for i in range(1,9)]

    # 반이름 변경
    name_change_map.clear()
    for o,n in wb['반이름변경'].iter_rows(min_row=1, max_col=2, values_only=True):
        if o and n:
            name_change_map[o] = n

    # 취소자
    cancellation_map.clear()
    for row in wb['취소자'].iter_rows(min_row=1, values_only=True):
        orig = row[0]
        if not orig: 
            continue
        lst = []
        for c in row[1:]:
            if c:
                nm, num = c.split(',')
                lst.append((nm.strip(), int(num)))
        cancellation_map[orig] = lst

    # 추가인원
    additional_map.clear()
    for row in wb['추가인원'].iter_rows(min_row=1, values_only=True):
        orig = row[0]
        if not orig:
            continue
        additional_map[orig] = [c.strip() for c in row[1:] if c and c.strip()]

    # 날짜 맵 초기화
    session_dates_map.clear()



# ——————————————————————————————
# 로그인
# ——————————————————————————————

def 로그인(page):
    page.goto(로그인사이트)
    page.fill('input[name="tbAdminId"]', adminID)
    page.fill('input[name="tbAdminPass"]', adminPW)
    page.press('input[name="tbAdminPass"]', 'Enter')
    page.goto(스케쥴관리링크)
    page.wait_for_selector('select[name="ddlTargetDate"]')
    page.select_option('select[name="ddlTargetDate"]', str(대상년월))
    page.wait_for_selector('select[name="ddlKeyField"]')
    page.select_option('select[name="ddlKeyField"]','a.tutor_id')


# ——————————————————————————————
# 보고서다운: 기존 그룹 다운로드 + 취소자 처리
# ——————————————————————————————

def 보고서다운(page):
    os.makedirs(REPORT_DIR, exist_ok=True)
    inp = 'input[name="tbKeyWord"][size="25"]'
    btn = 'a.button_gray_small:has-text("보고서"),a.button_red_small:has-text("보고서")'

    for prefix, count in [('MW',월수반), ('TT',화목반)]:
        for i in range(1, count+1):
            orig   = f"{prefix}_{i:02d}"
            code   = f"{지역}{orig}"
            mapped = name_change_map.get(orig, orig)
            grp    = os.path.join(REPORT_DIR, f"{지역}{mapped}")
            os.makedirs(grp, exist_ok=True)

            page.fill(inp, code); page.press(inp,'Enter')
            loc = page.locator(btn); loc.nth(7).wait_for(timeout=30000)
            bts = loc.all()

            # 날짜 역순 수집
            dates = []
            for b in bts[::-1]:
                href = b.get_attribute('href') or ''
                m = re.findall(r"'(.*?)'", href)
                if len(m)>1:
                    dates.append(m[1])
            session_dates_map[orig] = dates

            missing = []
            for idx, b in enumerate(bts[::-1],1):
                cls = b.get_attribute('class') or ''
                date = dates[idx-1] if idx-1 < len(dates) else 'Unknown'
                dst  = os.path.join(grp, f"{지역}{mapped}_{date}.doc")

                if 'button_red_small' in cls:
                    missing.append(date)
                    continue

                with page.expect_popup() as pp: b.click()
                pop = pp.value; pop.wait_for_selector('a.button_yellow')
                with pop.expect_download() as dl: pop.click('a.button_yellow')
                dl.value.save_as(dst); pop.close()

                # 1) suffix 교체
                if orig in name_change_map:
                    o_n, n_n = orig.split('_')[1], mapped.split('_')[1]
                    process_html(dst, suffix_change=(o_n,n_n))
                # 2) 취소자
                process_html(dst, attendance=(idx, cancellation_map.get(orig, [])))

            if missing:
                print(f"{code}의 {', '.join(f'[{d}]' for d in missing)}인 보고서가 작성되지 않았습니다.")


# ——————————————————————————————
# stub 생성: orig 기준으로 missing_orig 찾아 생성
# ——————————————————————————————

def create_stubs():
    """
    orig 기준으로 폴더가 없는 반만 stub 생성.
    폴더명·파일명은 orig 그대로, HTML 내부의 Group No/강사명은 매핑(template) suffix,
    '수업일시' 셀은 날짜와 요일만 실제 세션 날짜로 교체합니다.
    """
    for prefix, total in [('MW', 목표월수), ('TT', 목표화목)]:
        # 1) 템플릿용 orig 찾기 (다운로드된 mapped 폴더가 있는 첫 orig)
        template_orig = None
        for i in range(1, total+1):
            o2 = f"{prefix}_{i:02d}"
            m2 = name_change_map.get(o2, o2)
            if os.path.isdir(os.path.join(REPORT_DIR, f"{지역}{m2}")):
                template_orig = o2
                break
        if not template_orig:
            print(f"[WARN] {prefix}용 템플릿 그룹이 없습니다.")
            continue

        dates           = session_dates_map.get(template_orig, [])
        template_mapped = name_change_map.get(template_orig, template_orig)
        src_template    = os.path.join(
            REPORT_DIR,
            f"{지역}{template_mapped}",
            f"{지역}{template_mapped}_{dates[0]}.doc"
        )
        if not os.path.exists(src_template):
            print(f"[ERROR] 템플릿 파일 없음: {src_template}")
            continue

        # 2) 1~total orig 순회하며 orig 폴더가 없으면 stub 생성
        for i in range(1, total+1):
            orig    = f"{prefix}_{i:02d}"
            grp_dir = os.path.join(REPORT_DIR, f"{지역}{orig}")
            if os.path.isdir(grp_dir):
                continue

            os.makedirs(grp_dir, exist_ok=True)

            # 3) 날짜별 stub 파일 생성
            for idx, date in enumerate(dates, start=1):
                dst = os.path.join(grp_dir, f"{지역}{orig}_{date}.doc")
                if os.path.exists(dst):
                    continue
                shutil.copy(src_template, dst)

                # ─── 수업일시 셀만 날짜/요일 교체 ─────────────────────
                with open(dst, 'r', encoding='cp949', errors='ignore') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                td0 = soup.find('td', string='수업일시')
                if td0:
                    td1 = td0.find_next_sibling('td')
                    raw = td1.get_text()
                    # 새 날짜 포맷: "YYYY.MM.DD"
                    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                    date_str = dt.strftime("%Y.%m.%d")
                    dow      = dt.strftime("%a").upper()    # "WED"
                    new_prefix = f"{date_str}({dow})"
                    # 원본 텍스트에서 앞부분 YYYY.MM.DD(DOW) 부분만 교체
                    new_text = re.sub(
                        r"\d{4}\.\d{2}\.\d{2}\([A-Z]{3}\)",
                        new_prefix,
                        raw
                    )
                    td1.clear()
                    td1.append(new_text)
                with open(dst, 'w', encoding='cp949', errors='ignore') as f:
                    f.write(str(soup))
                # ───────────────────────────────────────────────────

                # 4) 나머지 후처리: suffix 교체, clear_fields, 교육내용 삽입
                process_html(
                    dst,
                    suffix_change=(
                        template_orig.split('_')[1],
                        orig.split('_')[1]
                    ),
                    clear_fields=('출결현황', '특이사항'),
                    education_idx=idx
                )

    print("▶︎ 누락된 반 스텁 생성 완료")

# ——————————————————————————————
# 추가인원 삽입: 모든 파일에 [출] 붙임
# ——————————————————————————————

def add_additional_members():
    for orig, names in additional_map.items():
        # 먼저 orig 폴더부터 확인
        dir_orig   = os.path.join(REPORT_DIR, f"{지역}{orig}")
        if os.path.isdir(dir_orig):
            grp_dir = dir_orig
        else:
            # orig 폴더 없으면 mapped 폴더
            mapped = name_change_map.get(orig, orig)
            grp_dir = os.path.join(REPORT_DIR, f"{지역}{mapped}")
            if not os.path.isdir(grp_dir):
                # 심지어 mapped 폴더도 없으면 스킵
                continue

        # grp_dir 안의 모든 .doc 파일에 추가인원 삽입
        for fn in os.listdir(grp_dir):
            if fn.endswith('.doc'):
                path = os.path.join(grp_dir, fn)
                process_html(path, additions=names)

# ——————————————————————————————
# 메인
# ——————————————————————————————

if __name__ == '__main__':
    초기화()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, args=['--disable-popup-blocking'])
        page    = browser.new_context(accept_downloads=True).new_page()
        로그인(page)
        보고서다운(page)
        browser.close()
    create_stubs()
    add_additional_members()
