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


def login(page, module):
    login_url = module.ws.cell(row=1, column=17).value
    admin_id = module.ws.cell(row=3, column=17).value
    admin_pw = module.ws.cell(row=4, column=17).value
    page.goto(login_url)
    page.fill('input[name="tbAdminId"]', str(admin_id))
    page.fill('input[name="tbAdminPass"]', str(admin_pw))
    page.press('input[name="tbAdminPass"]', 'Enter')
    page.wait_for_load_state("load")
    page.wait_for_timeout(1500)


def snapshot(page, label):
    return page.evaluate(
        """(label) => {
            const fields = Array.from(document.querySelectorAll('input,select,textarea')).map((el) => ({
                tag: el.tagName,
                name: el.name || '',
                id: el.id || '',
                type: el.type || '',
                valuePresent: !!(el.value || ''),
                checked: !!el.checked,
                optionCount: el.tagName === 'SELECT' ? el.options.length : null,
            }));
            const names = Array.from(new Set(fields.map((f) => f.name).filter(Boolean))).sort();
            const cbNames = fields.filter((f) => /checkbox/i.test(f.type)).map((f) => f.name);
            return {
                label,
                url: location.href,
                bodyHasNoUnassigned: /미배정 회원이 없습니다/.test(document.body.innerText || ''),
                bodyHasRows: /\\n\\s*1\\s/.test(document.body.innerText || ''),
                fieldCount: fields.length,
                fieldNames: names,
                checkboxNames: Array.from(new Set(cbNames)).sort(),
                formActions: Array.from(document.forms).map((form) => form.action || ''),
                submitScripts: Array.from(document.scripts).map((s) => s.textContent || '')
                    .filter((text) => /ProcAuto|cb_num|Teacher|Group|order|user|group/i.test(text))
                    .slice(0, 5),
            };
        }""",
        label,
    )


def main():
    module = load_main_module()
    module.초기화()
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=["--disable-popup-blocking"])
        try:
            page = browser.new_page()
            login(page, module)
            for popup in ("popClassRegNew.asp", "popClassRegOrg.asp"):
                page.goto(f"https://enozsw.enoz.kr/Admin/Class/{popup}")
                page.wait_for_load_state("load")
                results.append(snapshot(page, f"{popup}:initial"))
                for target_date in ("202606", "202605", "202510", "202506"):
                    for level in ("1", "2", "3"):
                        for lec in ("10", "7"):
                            page.goto(f"https://enozsw.enoz.kr/Admin/Class/{popup}")
                            page.wait_for_load_state("load")
                            if page.locator('select[name="ddlKeyTargetDate"]').count():
                                page.select_option('select[name="ddlKeyTargetDate"]', value=target_date)
                            if page.locator('select[name="ddlLevelIdx"]').count():
                                page.select_option('select[name="ddlLevelIdx"]', value=level)
                            if page.locator('select[name="ddlLecIDX"]').count():
                                page.select_option('select[name="ddlLecIDX"]', value=lec)
                            with page.expect_navigation(wait_until="load"):
                                page.evaluate("document.forms[0].action = location.pathname.split('/').pop() + '?t=search'; document.forms[0].submit();")
                            snap = snapshot(page, f"{popup}:{target_date}:L{level}:lec{lec}")
                            results.append(snap)
                            if snap["fieldCount"] > 10 and not snap["bodyHasNoUnassigned"]:
                                print(json.dumps(results, ensure_ascii=False, indent=2))
                                return
        finally:
            browser.close()
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
