import importlib.util
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "LMS전산반배정.py"
STUDENT_ROWS = [2, 10, 20, 35, 50, 65, 80, 95, 110, 115]
GHOST_OUT_ROWS = [2, 50, 100, 142, 143, 180, 220, 260, 301]


def load_main_module():
    spec = importlib.util.spec_from_file_location("lms_class_assignment", MAIN_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def current_group_text(page):
    group_no = parse_qs(urlparse(page.url).query).get("group_no", [""])[0]
    return page.evaluate(
        """(groupNo) => {
            const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
            if (!selectElement) return "";
            for (const option of selectElement.options) {
                const text = (option.textContent || "").trim();
                if (text.includes(groupNo)) return text;
            }
            return groupNo;
        }""",
        group_no,
    )


def verify_one(module, page, row_no, columns, label):
    ws = module.ws
    class_date = str(module.강의날짜)
    expected = str(ws.cell(row=row_no, column=columns[0]).value or "").strip()
    user_id = str(ws.cell(row=row_no, column=columns[2]).value or "").strip()
    if not expected or not user_id:
        return {"label": label, "row": row_no, "expected": expected, "current": "", "ok": False}

    page.fill('input[name="tbKeyWord"].font_blue', user_id)
    page.press('input[name="tbKeyWord"].font_blue', "Enter")
    page.wait_for_timeout(500)

    selector = f'a[href*="{class_date}"].button_red_small'
    with page.context.expect_page(timeout=45000) as page_info:
        page.click(selector, timeout=20000)
    detail_page = page_info.value
    detail_page.wait_for_load_state("load")
    current = current_group_text(detail_page)
    detail_page.close()
    page.bring_to_front()
    return {
        "label": label,
        "row": row_no,
        "expected": expected,
        "current": current,
        "ok": expected in current,
    }


def main():
    module = load_main_module()
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=["--disable-popup-blocking"])
        try:
            page = browser.new_page()
            module.초기화()
            module.로그인(page)
            for row in STUDENT_ROWS:
                results.append(verify_one(module, page, row, (1, 2, 3), "student"))
            for row in GHOST_OUT_ROWS:
                results.append(verify_one(module, page, row, (11, 12, 13), "ghost_out"))
        finally:
            browser.close()

    ok_count = 0
    for result in results:
        status = "OK" if result["ok"] else "FAIL"
        if result["ok"]:
            ok_count += 1
        print(
            f"{status}\t{result['label']}\trow={result['row']}\t"
            f"expected={result['expected']}\tcurrent={result['current']}"
        )
    print(f"SUMMARY\t{ok_count}/{len(results)} OK")
    if ok_count != len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
