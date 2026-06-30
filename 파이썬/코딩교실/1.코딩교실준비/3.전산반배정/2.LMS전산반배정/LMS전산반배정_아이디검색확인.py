import importlib.util
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "LMS전산반배정.py"
USER_ID = "blessedew"


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
            page.fill('input[name="tbKeyWord"].font_blue', USER_ID)
            page.press('input[name="tbKeyWord"].font_blue', "Enter")
            page.wait_for_timeout(1000)
            rows = page.evaluate(
                """() => Array.from(document.querySelectorAll('a.button_red_small')).map((a) => ({
                    text: (a.textContent || '').trim(),
                    href: a.href,
                    rowText: (a.closest('tr') ? a.closest('tr').innerText : '').trim(),
                }))"""
            )
            print(f"RESULT_COUNT {len(rows)}")
            for idx, row in enumerate(rows, 1):
                print(f"RESULT {idx}")
                print(row["text"])
                print(row["href"])
                print(row["rowText"])
        finally:
            browser.close()


if __name__ == "__main__":
    main()
