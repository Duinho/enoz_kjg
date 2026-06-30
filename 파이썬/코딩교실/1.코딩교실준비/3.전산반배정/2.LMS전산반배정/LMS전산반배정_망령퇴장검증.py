import importlib.util
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "LMS전산반배정.py"
SAMPLE_ROWS = [2, 3, 96, 97, 128, 129, 130, 131, 150, 173, 200, 236, 253]


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


def verify_rows(module, page, sample_rows):
    ws = module.ws
    class_date = str(module.강의날짜)
    results = []

    for row_no in sample_rows:
        class_name = str(ws.cell(row=row_no, column=11).value or "").strip()
        student_name = str(ws.cell(row=row_no, column=12).value or "").strip()
        user_id = str(ws.cell(row=row_no, column=13).value or "").strip()
        if not user_id:
            results.append((row_no, class_name, student_name, user_id, "", False))
            continue

        page.fill('input[name="tbKeyWord"].font_blue', user_id)
        page.press('input[name="tbKeyWord"].font_blue', "Enter")
        page.wait_for_timeout(500)

        selector = f'a[href*="{class_date}"].button_red_small'
        with page.context.expect_page(timeout=45000) as page_info:
            page.click(selector, timeout=20000)
        detail_page = page_info.value
        detail_page.wait_for_load_state("load")
        group_text = current_group_text(detail_page)
        ok = class_name in group_text
        results.append((row_no, class_name, student_name, user_id, group_text, ok))
        detail_page.close()
        page.bring_to_front()

    return results


def main():
    module = load_main_module()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=["--disable-popup-blocking"])
        try:
            page = browser.new_page()
            module.초기화()
            module.로그인(page)
            results = verify_rows(module, page, SAMPLE_ROWS)
        finally:
            browser.close()

    for row_no, class_name, student_name, user_id, group_text, ok in results:
        status = "OK" if ok else "FAIL"
        print(f"{status}\t{row_no}\t{student_name}\t{user_id}\texpected={class_name}\tcurrent={group_text}")

    ok_count = sum(1 for *_, ok in results if ok)
    print(f"SUMMARY\t{ok_count}/{len(results)} OK")
    if ok_count != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
