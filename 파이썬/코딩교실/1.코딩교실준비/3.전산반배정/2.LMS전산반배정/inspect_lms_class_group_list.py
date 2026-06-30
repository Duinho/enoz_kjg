import importlib.util
import json
import sys
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
    target_url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "https://enozsw.enoz.kr/Admin/Class/ClassGroupList.asp"
    )
    module = load_main_module()
    module.초기화()
    login_url = module.ws.cell(row=1, column=17).value
    admin_id = module.ws.cell(row=3, column=17).value
    admin_pw = module.ws.cell(row=4, column=17).value
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=["--disable-popup-blocking"])
        try:
            page = browser.new_page()
            page.goto(login_url)
            page.fill('input[name="tbAdminId"]', str(admin_id))
            page.fill('input[name="tbAdminPass"]', str(admin_pw))
            page.press('input[name="tbAdminPass"]', 'Enter')
            page.wait_for_load_state("load")
            page.wait_for_timeout(1500)
            page.goto(target_url)
            page.wait_for_load_state("load")
            data = page.evaluate(
                """() => ({
                    url: location.href,
                    title: document.title,
                    bodyText: document.body.innerText.slice(0, 50000),
                    links: Array.from(document.querySelectorAll('a')).map((a) => ({
                        text: (a.textContent || '').trim(),
                        href: a.href || '',
                        onclick: a.getAttribute('onclick') || '',
                        cls: a.className || '',
                    })).filter((x) => x.text || x.href || x.onclick),
                    targetRows: Array.from(document.querySelectorAll('tr')).map((tr) => ({
                        text: tr.innerText || '',
                        links: Array.from(tr.querySelectorAll('a')).map((a) => ({
                            text: (a.textContent || '').trim(),
                            href: a.href || '',
                            onclick: a.getAttribute('onclick') || '',
                            cls: a.className || '',
                        })),
                        inputs: Array.from(tr.querySelectorAll('input,select')).map((el) => ({
                            tag: el.tagName,
                            name: el.name || '',
                            id: el.id || '',
                            type: el.type || '',
                            value: el.value || '',
                        })),
                    })).filter((row) => /202606_S2_2_10_1900_(24|35)_/.test(row.text)),
                    scripts: Array.from(document.scripts).map((s) => s.textContent || '')
                        .filter((text) => /FuncSchedule|FuncClass|ClassGroup|schedule_view|class_group|반배정|스케쥴/.test(text))
                        .slice(0, 20),
                    forms: Array.from(document.forms).map((form) => ({
                        action: form.action || '',
                        method: form.method || '',
                        inputs: Array.from(form.querySelectorAll('input,select')).map((el) => ({
                            tag: el.tagName,
                            name: el.name || '',
                            id: el.id || '',
                            type: el.type || '',
                            value: el.tagName === 'SELECT' ? el.value : (el.type === 'password' ? '[redacted]' : (el.value || '')),
                        })).slice(0, 120),
                    }))
                })"""
            )
            print(json.dumps(data, ensure_ascii=False, indent=2))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
