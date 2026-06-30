import importlib.util
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "LMS전산반배정.py"
OUT = BASE_DIR / "lms_detail_dump.html"


def load_main_module():
    spec = importlib.util.spec_from_file_location("lms_class_assignment", MAIN_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    module = load_main_module()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=["--disable-popup-blocking"])
        try:
            page = browser.new_page()
            module.초기화()
            module.로그인(page)
            ws = module.ws
            user_id = str(ws.cell(27, 8).value or "").strip()
            page.fill('input[name="tbKeyWord"].font_blue', user_id)
            page.press('input[name="tbKeyWord"].font_blue', "Enter")
            page.wait_for_timeout(500)
            with page.context.expect_page(timeout=45000) as page_info:
                page.click(f'a[href*="{module.강의날짜}"].button_red_small', timeout=20000)
            detail = page_info.value
            detail.wait_for_load_state("load")
            OUT.write_text(detail.content(), encoding="utf-8")
            print(str(OUT))
            detail.close()
        finally:
            browser.close()


if __name__ == "__main__":
    main()
