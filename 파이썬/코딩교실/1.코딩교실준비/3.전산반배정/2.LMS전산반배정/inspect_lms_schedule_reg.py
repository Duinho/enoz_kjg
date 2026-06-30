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
    group_no = sys.argv[1] if len(sys.argv) > 1 else "202606_S2_2_10_1900_35_21"
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
            page.goto(f"https://enozsw.enoz.kr/Admin/Class/popScheduleReg.asp?sOrderNo={group_no}")
            page.wait_for_load_state("load")
            data = page.evaluate(
                """(groupNo) => ({
                    groupNo,
                    url: location.href,
                    title: document.title,
                    bodyText: document.body.innerText,
                    forms: Array.from(document.forms).map((form) => ({
                        name: form.name || '',
                        action: form.action || '',
                        method: form.method || '',
                        inputs: Array.from(form.querySelectorAll('input,select,textarea')).map((el) => ({
                            tag: el.tagName,
                            name: el.name || '',
                            id: el.id || '',
                            type: el.type || '',
                            value: el.tagName === 'SELECT'
                                ? el.value
                                : (el.type === 'password' ? '[redacted]' : (el.value || '')),
                            checked: el.checked || false,
                            options: el.tagName === 'SELECT'
                                ? Array.from(el.options).map((opt) => ({
                                    text: (opt.textContent || '').trim(),
                                    value: opt.value || '',
                                    selected: opt.selected,
                                }))
                                : undefined,
                        })),
                    })),
                    links: Array.from(document.querySelectorAll('a')).map((a) => ({
                        text: (a.textContent || '').trim(),
                        href: a.href || '',
                        onclick: a.getAttribute('onclick') || '',
                        cls: a.className || '',
                    })).filter((x) => x.text || x.href || x.onclick),
                    scripts: Array.from(document.scripts).map((s) => s.textContent || '')
                        .filter((text) => /submit|Schedule|Teacher|teacher|강사|수업|등록|group/i.test(text))
                        .slice(0, 20),
                })""",
                group_no,
            )
            print(json.dumps(data, ensure_ascii=False, indent=2))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
