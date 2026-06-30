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
            page.wait_for_timeout(1000)
            data = page.evaluate(
                """() => ({
                    url: location.href,
                    title: document.title,
                    bodyText: document.body.innerText.slice(0, 4000),
                    links: Array.from(document.querySelectorAll('a')).map((a) => ({
                        text: (a.textContent || '').trim(),
                        href: a.href || '',
                        onclick: a.getAttribute('onclick') || '',
                        cls: a.className || '',
                    })).filter((x) => x.text || x.href || x.onclick).slice(0, 300),
                    forms: Array.from(document.forms).map((form) => ({
                        action: form.action || '',
                        method: form.method || '',
                        inputs: Array.from(form.querySelectorAll('input,select')).map((el) => ({
                            tag: el.tagName,
                            name: el.name || '',
                            id: el.id || '',
                            type: el.type || '',
                            value: el.tagName === 'SELECT' ? el.value : (el.type === 'password' ? '[redacted]' : (el.value || '')),
                        })).slice(0, 100),
                    }))
                })"""
            )
            print(json.dumps(data, ensure_ascii=False, indent=2))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
