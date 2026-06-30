import importlib.util
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "LMS전산반배정.py"
ROWS = list(range(27, 33))


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
            if (!selectElement) return groupNo;
            for (const option of selectElement.options) {
                const text = (option.textContent || "").trim();
                if (text.includes(groupNo)) return text;
            }
            return groupNo;
        }""",
        group_no,
    )


def verify_row(module, page, row_no):
    ws = module.ws
    expected = str(ws.cell(row=row_no, column=6).value or "").strip()
    user_id = str(ws.cell(row=row_no, column=8).value or "").strip()
    page.fill('input[name="tbKeyWord"].font_blue', user_id)
    page.press('input[name="tbKeyWord"].font_blue', "Enter")
    page.wait_for_timeout(500)
    with page.context.expect_page(timeout=45000) as page_info:
        page.click(f'a[href*="{module.강의날짜}"].button_red_small', timeout=20000)
    detail = page_info.value
    detail.wait_for_load_state("load")
    current = current_group_text(detail)
    tt_options = detail.evaluate(
        """() => Array.from(document.querySelectorAll('select[name="ddlTargetGroupNo"] option'))
            .map((option) => (option.textContent || '').trim())
            .filter((text) => text.includes('PH_TT_'))"""
    )
    detail.close()
    page.bring_to_front()
    return {
        "row": row_no,
        "expected": expected,
        "current": current,
        "ok": expected in current,
        "tt_options": tt_options,
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
            for row_no in ROWS:
                results.append(verify_row(module, page, row_no))
        finally:
            browser.close()

    for result in results:
        status = "OK" if result["ok"] else "FAIL"
        print(
            f"{status}\trow={result['row']}\texpected={result['expected']}\t"
            f"current={result['current']}"
        )
    option_set = sorted({text.split()[-1] for result in results for text in result["tt_options"]})
    print("TT_OPTIONS\t" + ",".join(option_set))
    ok_count = sum(1 for result in results if result["ok"])
    print(f"SUMMARY\t{ok_count}/{len(results)} OK")
    if ok_count != len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
