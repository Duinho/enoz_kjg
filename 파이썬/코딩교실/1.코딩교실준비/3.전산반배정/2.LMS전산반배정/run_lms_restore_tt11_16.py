import importlib.util
import sys
import traceback
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "LMS전산반배정.py"
RESTORE_ROWS = list(range(27, 33))


def load_main_module():
    spec = importlib.util.spec_from_file_location("lms_class_assignment", MAIN_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assign_to_class(module, page, row_no):
    ws = module.ws
    target_class = str(ws.cell(row=row_no, column=6).value or "").strip()
    user_id = str(ws.cell(row=row_no, column=8).value or "").strip()
    if not target_class or not user_id:
        raise RuntimeError(f"restore row {row_no}: missing target class or user id")

    page.fill('input[name="tbKeyWord"].font_blue', user_id)
    page.press('input[name="tbKeyWord"].font_blue', "Enter")
    page.wait_for_timeout(500)

    selector = f'a[href*="{module.강의날짜}"].button_red_small'
    with page.context.expect_page(timeout=45000) as page_info:
        page.click(selector, timeout=20000)
    detail_page = page_info.value
    detail_page.wait_for_load_state("load")

    target_value = detail_page.evaluate(
        """(name) => {
            const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
            if (!selectElement) return "";
            for (const option of selectElement.options) {
                const text = (option.textContent || "").trim();
                if (text.includes(name)) {
                    selectElement.value = option.value;
                    return option.value;
                }
            }
            const suffix = (name.match(/_(\\d{2})$/) || [])[1];
            const existing = Array.from(selectElement.options)
                .map((option) => option.value || "")
                .find((value) => value.includes("_35_17") || value.includes("_35_10"));
            if (!suffix || !existing) return "";
            const value = existing.replace(/_35_\\d{2}$/, `_35_${suffix}`);
            const option = document.createElement("option");
            option.value = value;
            option.textContent = `${value} ${name}`;
            selectElement.appendChild(option);
            selectElement.value = value;
            return value;
        }""",
        target_class,
    )
    if not target_value:
        raise RuntimeError(f"restore row {row_no}: target class not found {target_class}")

    with detail_page.expect_navigation(wait_until="load"):
        detail_page.evaluate(
            """() => {
            const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
            if (!selectElement) return;
            selectElement.dispatchEvent(new Event('change', { bubbles: true }));
            if (typeof funcSearch === 'function') funcSearch();
        }"""
        )

    hidden_target_value = detail_page.evaluate(
        """() => {
            const hidden = document.querySelector('input[name="hhdTargetGroupNo"]');
            return hidden ? hidden.value : "";
        }"""
    )
    if hidden_target_value and hidden_target_value != target_value:
        target_value = hidden_target_value

    def on_dialog(dialog):
        try:
            dialog.accept()
        except Exception:
            pass

    detail_page.on("dialog", on_dialog)
    try:
        with detail_page.expect_navigation(wait_until="load", timeout=10000):
            detail_page.evaluate(
                """(value) => {
                    const form = document.frm;
                    const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
                    if (!form || !selectElement) throw new Error("course edit form/select not found");
                    let option = Array.from(selectElement.options).find((opt) => opt.value === value);
                    if (!option) {
                        option = document.createElement("option");
                        option.value = value;
                        option.textContent = value;
                        selectElement.appendChild(option);
                    }
                    selectElement.value = value;
                    const hidden = document.querySelector('input[name="hhdTargetGroupNo"]');
                    if (hidden) hidden.value = value;
                    form.action = "popCourseEditProc.asp";
                    form.submit();
                }""",
                target_value,
            )
    except (PlaywrightError, PlaywrightTimeoutError) as exc:
        if not detail_page.is_closed():
            raise
        print(f"RESTORE_POPUP_CLOSED row={row_no} target={target_class}: {exc}")
    page.wait_for_timeout(500)
    try:
        if not detail_page.is_closed():
            detail_page.close()
    except Exception:
        pass
    page.bring_to_front()
    print(f"RESTORE_OK row={row_no} target={target_class} value={target_value}")


def main():
    module = load_main_module()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=["--disable-popup-blocking"])
        try:
            page = browser.new_page()
            module.초기화()
            module.로그인(page)
            for row_no in RESTORE_ROWS:
                assign_to_class(module, page, row_no)
        finally:
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
