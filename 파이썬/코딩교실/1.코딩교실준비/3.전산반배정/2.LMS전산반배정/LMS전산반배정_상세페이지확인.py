import importlib.util
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "LMS전산반배정.py"


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
            user_id = str(ws.cell(2, 13).value).strip()
            class_date = str(module.강의날짜)

            page.fill('input[name="tbKeyWord"].font_blue', user_id)
            page.press('input[name="tbKeyWord"].font_blue', "Enter")
            page.wait_for_timeout(500)
            with page.context.expect_page(timeout=45000) as page_info:
                page.click(f'a[href*="{class_date}"].button_red_small', timeout=20000)
            detail_page = page_info.value
            detail_page.wait_for_load_state("load")

            body_text = detail_page.locator("body").inner_text(timeout=10000)
            print("URL=", detail_page.url)
            print("TEXT_START")
            print(body_text[:6000])
            print("TEXT_END")

            html = detail_page.content()
            for needle in ["BG_MW_14", "BG_TT_14", "Group", "현재", "수강", "권도연"]:
                print(f"COUNT {needle} = {html.count(needle)}")

            detail_page.close()
        finally:
            browser.close()


if __name__ == "__main__":
    main()
