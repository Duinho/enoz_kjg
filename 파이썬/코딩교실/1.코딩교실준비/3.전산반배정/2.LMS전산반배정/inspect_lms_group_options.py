import importlib.util
import json
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
            user_id = str(ws.cell(27, 8).value or "").strip()
            page.fill('input[name="tbKeyWord"].font_blue', user_id)
            page.press('input[name="tbKeyWord"].font_blue', "Enter")
            page.wait_for_timeout(500)
            with page.context.expect_page(timeout=45000) as page_info:
                page.click(f'a[href*="{module.강의날짜}"].button_red_small', timeout=20000)
            detail = page_info.value
            detail.wait_for_load_state("load")
            data = detail.evaluate(
                """() => {
                    const select = document.querySelector('select[name="ddlTargetGroupNo"]');
                    const options = select ? Array.from(select.options).map((option) => ({
                        value: option.value,
                        text: (option.textContent || '').trim(),
                        selected: option.selected,
                    })) : [];
                    const forms = Array.from(document.forms).map((form) => ({
                        id: form.id || '',
                        name: form.name || '',
                        action: form.action || '',
                        method: form.method || '',
                        inputs: Array.from(form.querySelectorAll('input,select,textarea')).map((el) => ({
                            tag: el.tagName,
                            name: el.name || '',
                            id: el.id || '',
                            type: el.type || '',
                            value: el.tagName === 'SELECT' ? el.value : (el.value || ''),
                        })).slice(0, 80),
                    }));
                    const buttons = Array.from(document.querySelectorAll('a,button,input[type=button],input[type=submit]')).map((el) => ({
                        tag: el.tagName,
                        text: (el.textContent || el.value || '').trim(),
                        href: el.href || '',
                        onclick: el.getAttribute('onclick') || '',
                        cls: el.className || '',
                    })).slice(0, 120);
                    return {url: location.href, options, forms, buttons};
                }"""
            )
            data["tt_options"] = [
                opt for opt in data["options"] if "PH_TT" in opt["text"] or "PH_TT" in opt["value"]
            ]
            data["mw_options"] = [
                opt for opt in data["options"] if "PH_MW" in opt["text"] or "PH_MW" in opt["value"]
            ]
            print(json.dumps(data, ensure_ascii=False, indent=2))
            detail.close()
        finally:
            browser.close()


if __name__ == "__main__":
    main()
