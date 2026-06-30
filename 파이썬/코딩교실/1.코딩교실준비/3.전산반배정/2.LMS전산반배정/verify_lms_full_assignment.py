import argparse
import csv
import importlib.util
import json
import re
import sys
import time
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / "LMS전산반배정.py"
WORKBOOK = BASE_DIR / "LMS전산반배정.xlsx"
GROUP_LIST_URL = (
    "https://enozsw.enoz.kr/Admin/Class/ClassGroupList.asp?"
    "page=1&ddlKeyTargetDate=202606&ddlJS=&ddlKeyGubun=&ddlKeyTeacher="
    "&ddlKeyLevel=&ddlKeyLecture=&ddlKeyStudyClass=&ddlKeySTime="
    "&ddlKeyETime=&ddlKeyField=&tbKeyWord="
)


@dataclass(frozen=True)
class ExpectedAssignment:
    source: str
    row: int
    expected_class: str
    student_name: str
    user_id: str


@dataclass(frozen=True)
class Settings:
    login_url: str
    course_url: str
    admin_id: str
    admin_pw: str
    class_date: str


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def column_index(cell_ref):
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + (ord(char.upper()) - ord("A") + 1)
    return index


def row_index(cell_ref):
    digits = "".join(ch for ch in cell_ref if ch.isdigit())
    return int(digits) if digits else 0


def load_main_sheet_values():
    import xml.etree.ElementTree as ET

    ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    with zipfile.ZipFile(WORKBOOK) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("main:si", ns):
                text = "".join(node.text or "" for node in item.findall(".//main:t", ns))
                shared.append(text)

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall("rel:Relationship", ns)
        }
        sheet_path = None
        for sheet in workbook.findall(".//main:sheet", ns):
            if sheet.attrib.get("name") == "메인":
                rel_id = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                target = rel_map[rel_id]
                target = target.lstrip("/")
                sheet_path = target if target.startswith("xl/") else "xl/" + target
                break
        if not sheet_path:
            raise RuntimeError("메인 sheet not found in workbook")

        root = ET.fromstring(archive.read(sheet_path))
        values = defaultdict(dict)
        for cell in root.findall(".//main:c", ns):
            ref = cell.attrib.get("r", "")
            row = row_index(ref)
            col = column_index(ref)
            cell_type = cell.attrib.get("t", "")
            value_node = cell.find("main:v", ns)
            inline_text = cell.find("main:is/main:t", ns)
            if cell_type == "s" and value_node is not None:
                raw = shared[int(value_node.text)]
            elif cell_type == "inlineStr" and inline_text is not None:
                raw = inline_text.text or ""
            elif value_node is not None:
                raw = value_node.text or ""
            else:
                raw = ""
            values[row][col] = raw
        return values


def build_expected():
    ws_values = load_main_sheet_values()
    max_row = max(ws_values) if ws_values else 1
    items = []

    def collect(source, class_col, name_col, id_col):
        for row in range(2, max_row + 1):
            expected_class = clean(ws_values[row].get(class_col, ""))
            student_name = clean(ws_values[row].get(name_col, ""))
            user_id = clean(ws_values[row].get(id_col, ""))
            if not expected_class and not user_id:
                continue
            if not expected_class or not user_id:
                items.append(ExpectedAssignment(source, row, expected_class, student_name, user_id))
                continue
            items.append(ExpectedAssignment(source, row, expected_class, student_name, user_id))

    collect("student", 1, 2, 3)
    collect("ghost_in", 6, 7, 8)
    collect("ghost_out", 11, 12, 13)
    # The same user can appear in multiple action ranges. That is executable
    # order data, not a valid final-state expectation. Prefer the concrete
    # placement ranges over ghost_out so we do not undo restored guard classes.
    priority = {"student": 0, "ghost_in": 1, "ghost_out": 2}
    by_user = defaultdict(list)
    for item in items:
        by_user[item.user_id].append(item)

    deduped = []
    conflicts = []
    for user_id, user_items in by_user.items():
        if len(user_items) == 1:
            deduped.append(user_items[0])
            continue
        sorted_items = sorted(user_items, key=lambda item: priority.get(item.source, 99))
        selected = sorted_items[0]
        deduped.append(selected)
        conflicts.append(
            {
                "user_id": user_id,
                "selected_source": selected.source,
                "selected_row": selected.row,
                "selected_class": selected.expected_class,
                "all_sources": ";".join(
                    f"{item.source}:{item.row}:{item.expected_class}" for item in user_items
                ),
            }
        )
    return deduped, conflicts


def load_settings():
    values = load_main_sheet_values()
    return Settings(
        login_url=clean(values[1].get(17, "")),
        course_url=clean(values[2].get(17, "")),
        admin_id=clean(values[3].get(17, "")),
        admin_pw=clean(values[4].get(17, "")),
        class_date=clean(values[5].get(17, "")),
    )


def extract_class_from_group_text(text):
    match = re.search(r"\b(PH|BG|GM)_(MW|TT)_\d{2}\b", text or "")
    return match.group(0) if match else ""


def parse_group_count_text(text):
    match = re.search(r"\((\d+)명\)", text or "")
    if match:
        return int(match.group(1))
    match = re.search(r"\b(\d+)\s*명\b", text or "")
    return int(match.group(1)) if match else None


def current_group_text(detail_page):
    group_no = parse_qs(urlparse(detail_page.url).query).get("group_no", [""])[0]
    return detail_page.evaluate(
        """(groupNo) => {
            const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
            if (!selectElement) return groupNo;
            for (const option of selectElement.options) {
                const text = (option.textContent || "").trim();
                if (text.includes(groupNo)) return text;
            }
            return groupNo;
        }""",
        group_no,
    )


def login(page, settings):
    page.goto(settings.login_url)
    page.fill('input[name="tbAdminId"]', settings.admin_id)
    page.fill('input[name="tbAdminPass"]', settings.admin_pw)
    page.press('input[name="tbAdminPass"]', "Enter")
    page.goto(settings.course_url)
    page.wait_for_load_state("load")
    page.select_option('select[name="ddlTargetDate"]', value=settings.class_date)
    page.select_option('select[name="ddlKeyField"]', value='b.m_id')


def scrape_class_group_counts(page):
    seen_pages = set()
    pending = [GROUP_LIST_URL]
    rows = []

    while pending:
        url = pending.pop(0)
        if url in seen_pages:
            continue
        seen_pages.add(url)
        page.goto(url)
        page.wait_for_load_state("load")
        rows.extend(
            page.evaluate(
                """() => Array.from(document.querySelectorAll('tr')).map((tr) => {
                    const text = (tr.innerText || '').trim();
                    const inputs = Array.from(tr.querySelectorAll('input[name="cbSel"]')).map((el) => el.value || '');
                    return {text, groupNo: inputs[0] || ''};
                }).filter((row) => row.groupNo && /202606_S2_2_10_1900_(24|35)_/.test(row.groupNo))"""
            )
        )
        next_urls = page.evaluate(
            """() => Array.from(document.querySelectorAll('a'))
                .map((a) => a.href || '')
                .filter((href) => /ClassGroupList\\.asp\\?page=\\d+/.test(href)
                    && href.includes('ddlKeyTargetDate=202606'))"""
        )
        for next_url in next_urls:
            if next_url not in seen_pages and next_url not in pending:
                pending.append(next_url)

    result = {}
    for row in rows:
        text = row["text"]
        teacher = extract_class_from_group_text(text)
        count_match = re.search(r"\b(\d+)\s*명\b", text)
        result[row["groupNo"]] = {
            "teacher": teacher,
            "count": int(count_match.group(1)) if count_match else None,
            "text": text,
        }
    return result


def open_course_detail(page, settings, user_id):
    class_date = settings.class_date
    page.fill('input[name="tbKeyWord"].font_blue', user_id)
    page.press('input[name="tbKeyWord"].font_blue', "Enter")
    page.wait_for_timeout(400)
    selector = f'a[href*="{class_date}"].button_red_small'
    with page.context.expect_page(timeout=45000) as page_info:
        page.click(selector, timeout=20000)
    detail = page_info.value
    detail.wait_for_load_state("load")
    return detail


def verify_one(page, settings, item):
    if not item.expected_class or not item.user_id:
        return {
            "source": item.source,
            "row": item.row,
            "expected_class": item.expected_class,
            "user_id": item.user_id,
            "status": "INVALID_INPUT",
            "current_class": "",
            "current_text": "",
            "message": "missing expected class or user id",
        }
    try:
        detail = open_course_detail(page, settings, item.user_id)
        try:
            current_text = current_group_text(detail)
            current_class = extract_class_from_group_text(current_text)
        finally:
            try:
                if not detail.is_closed():
                    detail.close()
            except PlaywrightError:
                pass
        page.bring_to_front()
        return {
            "source": item.source,
            "row": item.row,
            "expected_class": item.expected_class,
            "user_id": item.user_id,
            "status": "OK" if current_class == item.expected_class else "MISMATCH",
            "current_class": current_class,
            "current_text": current_text,
            "message": "",
        }
    except Exception as exc:
        return {
            "source": item.source,
            "row": item.row,
            "expected_class": item.expected_class,
            "user_id": item.user_id,
            "status": "ERROR",
            "current_class": "",
            "current_text": "",
            "message": repr(exc),
        }


def move_one(page, settings, item, current_class):
    detail = open_course_detail(page, settings, item.user_id)
    try:
        target_value = detail.evaluate(
            """(targetClass) => {
                const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
                if (!selectElement) return "";
                for (const option of selectElement.options) {
                    const text = (option.textContent || "").trim();
                    if (text.includes(targetClass)) {
                        selectElement.value = option.value;
                        return option.value;
                    }
                }
                return "";
            }""",
            item.expected_class,
        )
        if not target_value:
            return "FIX_FAIL", "target class not found in select"

        try:
            with detail.expect_navigation(wait_until="load", timeout=10000):
                detail.evaluate(
                    """() => {
                        const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
                        selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                        if (typeof funcSearch === 'function') funcSearch();
                    }"""
                )
        except (PlaywrightError, PlaywrightTimeoutError):
            if detail.is_closed():
                return "FIX_UNKNOWN", "detail page closed during search"
            raise

        hidden_target = detail.evaluate(
            """() => {
                const hidden = document.querySelector('input[name="hhdTargetGroupNo"]');
                return hidden ? hidden.value : "";
            }"""
        )
        if hidden_target:
            target_value = hidden_target

        def on_dialog(dialog):
            try:
                dialog.accept()
            except Exception:
                pass

        detail.on("dialog", on_dialog)
        try:
            with detail.expect_navigation(wait_until="load", timeout=10000):
                detail.evaluate(
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
        except (PlaywrightError, PlaywrightTimeoutError):
            if not detail.is_closed():
                raise
        return "FIX_SUBMITTED", f"{current_class}->{item.expected_class}"
    except Exception as exc:
        return "FIX_FAIL", repr(exc)
    finally:
        try:
            if not detail.is_closed():
                detail.close()
        except PlaywrightError:
            pass
        page.bring_to_front()


def summarize(results, group_counts):
    by_expected = Counter(item["expected_class"] for item in results if item["expected_class"])
    by_current = Counter(item["current_class"] for item in results if item["current_class"])
    mismatches = [item for item in results if item["status"] != "OK"]
    group_rows = []
    for teacher, expected_count in sorted(by_expected.items()):
        actual_by_detail = by_current.get(teacher, 0)
        actual_by_class_list = None
        group_no = ""
        for candidate_group_no, info in group_counts.items():
            if info["teacher"] == teacher:
                actual_by_class_list = info["count"]
                group_no = candidate_group_no
                break
        group_rows.append(
            {
                "teacher": teacher,
                "expected_count": expected_count,
                "actual_by_detail": actual_by_detail,
                "actual_by_class_list": actual_by_class_list,
                "group_no": group_no,
                "ok": expected_count == actual_by_detail
                and (actual_by_class_list is None or expected_count == actual_by_class_list),
            }
        )
    return group_rows, mismatches


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args():
    parser = argparse.ArgumentParser(description="Verify and optionally fix PH LMS class assignment.")
    parser.add_argument("--fix", action="store_true", help="Move mismatched rows to expected classes.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of expected assignments to verify.")
    parser.add_argument("--headless", action="store_true", help="Run browser headless.")
    return parser.parse_args()


def main():
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    expected, conflicts = build_expected()
    if args.limit:
        expected = expected[: args.limit]

    settings = load_settings()
    results = []
    fix_rows = []
    group_counts = {}
    started = time.time()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=args.headless, args=["--disable-popup-blocking"]
        )
        try:
            page = browser.new_page()
            login(page, settings)
            group_counts = scrape_class_group_counts(page)
            page.goto(settings.course_url)
            page.wait_for_load_state("load")
            page.select_option('select[name="ddlTargetDate"]', value=settings.class_date)
            page.select_option('select[name="ddlKeyField"]', value='b.m_id')

            for index, item in enumerate(expected, start=1):
                result = verify_one(page, settings, item)
                results.append(result)
                if result["status"] == "MISMATCH" and args.fix:
                    fix_status, fix_message = move_one(
                        page, settings, item, result["current_class"]
                    )
                    fix_rows.append(
                        {
                            "source": item.source,
                            "row": item.row,
                            "expected_class": item.expected_class,
                            "current_class": result["current_class"],
                            "status": fix_status,
                            "message": fix_message,
                        }
                    )
                    if fix_status == "FIX_SUBMITTED":
                        result = verify_one(page, settings, item)
                        result["message"] = "after_fix"
                        results[-1] = result
                if index % 25 == 0 or index == len(expected):
                    ok_count = sum(1 for row in results if row["status"] == "OK")
                    print(f"PROGRESS\t{index}/{len(expected)}\tOK={ok_count}")
        finally:
            browser.close()

    group_rows, mismatches = summarize(results, group_counts)
    result_csv = BASE_DIR / f"lms_full_assignment_verify_{timestamp}.csv"
    group_csv = BASE_DIR / f"lms_full_assignment_groups_{timestamp}.csv"
    fix_csv = BASE_DIR / f"lms_full_assignment_fixes_{timestamp}.csv"
    summary_json = BASE_DIR / f"lms_full_assignment_summary_{timestamp}.json"
    conflict_csv = BASE_DIR / f"lms_full_assignment_conflicts_{timestamp}.csv"

    write_csv(
        result_csv,
        results,
        [
            "source",
            "row",
            "expected_class",
            "user_id",
            "status",
            "current_class",
            "current_text",
            "message",
        ],
    )
    write_csv(
        group_csv,
        group_rows,
        [
            "teacher",
            "expected_count",
            "actual_by_detail",
            "actual_by_class_list",
            "group_no",
            "ok",
        ],
    )
    if fix_rows:
        write_csv(
            fix_csv,
            fix_rows,
            ["source", "row", "expected_class", "current_class", "status", "message"],
        )
    if conflicts:
        write_csv(
            conflict_csv,
            conflicts,
            [
                "user_id",
                "selected_source",
                "selected_row",
                "selected_class",
                "all_sources",
            ],
        )

    ok_count = sum(1 for row in results if row["status"] == "OK")
    error_count = sum(1 for row in results if row["status"] == "ERROR")
    mismatch_count = sum(1 for row in results if row["status"] == "MISMATCH")
    group_ok_count = sum(1 for row in group_rows if row["ok"])
    summary = {
        "expected_total": len(expected),
        "ok_count": ok_count,
        "mismatch_count": mismatch_count,
        "error_count": error_count,
        "group_total": len(group_rows),
        "group_ok_count": group_ok_count,
        "group_mismatch_count": len(group_rows) - group_ok_count,
        "fix_attempts": len(fix_rows),
        "fix_submitted": sum(1 for row in fix_rows if row["status"] == "FIX_SUBMITTED"),
        "seconds": round(time.time() - started, 1),
        "result_csv": str(result_csv),
        "group_csv": str(group_csv),
        "fix_csv": str(fix_csv) if fix_rows else "",
        "conflict_count": len(conflicts),
        "conflict_csv": str(conflict_csv) if conflicts else "",
    }
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SUMMARY_JSON\t" + json.dumps(summary, ensure_ascii=False))
    print(f"RESULT_CSV\t{result_csv}")
    print(f"GROUP_CSV\t{group_csv}")
    if fix_rows:
        print(f"FIX_CSV\t{fix_csv}")
    if mismatch_count or error_count or group_ok_count != len(group_rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
