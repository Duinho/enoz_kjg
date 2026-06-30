import importlib.util
import os
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "LMS전산반배정.py"
START_ROW = int(os.environ.get("LMS_GHOST_OUT_START_ROW", "2"))


def load_main_module():
    spec = importlib.util.spec_from_file_location("lms_class_assignment", MAIN_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assign_ghost_out_from_row(module, page, start_row):
    ws = module.ws
    last_row = ws.max_row
    class_date = str(module.강의날짜)

    for row_no in range(start_row, last_row + 1):
        class_name = ws.cell(row=row_no, column=11).value
        student_name = ws.cell(row=row_no, column=12).value
        user_id = ws.cell(row=row_no, column=13).value

        if user_id is None or str(user_id).strip() == "":
            print(f"망령퇴장 종료: {row_no}행 아이디가 비어 있습니다.")
            return

        user_id = str(user_id).strip()
        student_name = str(student_name).strip() if student_name else ""
        class_name = str(class_name).strip() if class_name else ""

        page.fill('input[name="tbKeyWord"].font_blue', user_id)
        page.press('input[name="tbKeyWord"].font_blue', "Enter")
        page.wait_for_timeout(500)

        context = page.context
        selector = f'a[href*="{class_date}"].button_red_small'

        with context.expect_page(timeout=45000) as page_info:
            page.click(selector, timeout=20000)
        new_page = page_info.value
        new_page.wait_for_load_state("load")

        new_page.evaluate(
            """(name) => {
                const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
                if (!selectElement) throw new Error('ddlTargetGroupNo not found');
                let matched = false;
                for (const option of selectElement.options) {
                    const text = (option.textContent || "").trim();
                    if (text.includes(name)) {
                        selectElement.value = option.value;
                        selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                        matched = true;
                        break;
                    }
                }
                if (!matched) throw new Error(`target group not found: ${name}`);
            }""",
            class_name,
        )

        def on_dialog(dialog):
            try:
                dialog.accept()
            except Exception:
                pass

        new_page.once("dialog", on_dialog)
        new_page.locator(
            'a.button_yellow.bold:has-text("수강 변경"), '
            'a.button_red.bold:has-text("수강 인원이 모두 찼습니다. (변경불가 => 가능)")'
        ).click(timeout=20000)
        try:
            new_page.wait_for_timeout(300)
        except PlaywrightError:
            pass
        try:
            if not new_page.is_closed():
                new_page.close()
        except PlaywrightError:
            pass
        page.bring_to_front()
        print(f"{row_no}행 {student_name}({user_id})이(가) {class_name}으로 배정 완료")


def main():
    module = load_main_module()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=["--disable-popup-blocking"])
        try:
            page = browser.new_page()
            module.초기화()
            module.로그인(page)
            assign_ghost_out_from_row(module, page, START_ROW)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
