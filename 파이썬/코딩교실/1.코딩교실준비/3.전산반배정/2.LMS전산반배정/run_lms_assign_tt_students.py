import argparse
import csv
import hashlib
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
MAIN_SHEET = "\uba54\uc778"
TT_SHEET = "\ud654\ubaa9"
GROUP_LIST_URL = (
    "https://enozsw.enoz.kr/Admin/Class/ClassGroupList.asp?"
    "page=1&ddlKeyTargetDate={class_date}&ddlJS=&ddlKeyGubun=&ddlKeyTeacher="
    "&ddlKeyLevel=&ddlKeyLecture=&ddlKeyStudyClass=&ddlKeySTime=&ddlKeyETime="
    "&ddlKeyField=&tbKeyWord="
)


@dataclass(frozen=True)
class Settings:
    login_url: str
    course_url: str
    admin_id: str
    admin_pw: str
    class_date: str
    prefix: str


@dataclass(frozen=True)
class Assignment:
    row: int
    target_class: str
    user_id: str
    name: str


def clean(value):
    return "" if value is None else str(value).strip()


def find_workbook():
    candidates = [
        path
        for path in BASE_DIR.glob("LMS*.xlsx")
        if not path.name.startswith("~$")
    ]
    if not candidates:
        raise FileNotFoundError("LMS workbook was not found")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def column_index(cell_ref):
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + (ord(char.upper()) - ord("A") + 1)
    return index


def row_index(cell_ref):
    digits = "".join(ch for ch in cell_ref if ch.isdigit())
    return int(digits) if digits else 0


def load_workbook_values(workbook_path):
    import posixpath
    import xml.etree.ElementTree as ET

    ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    sheets = {}
    with zipfile.ZipFile(workbook_path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("main:si", ns):
                shared.append("".join(node.text or "" for node in item.findall(".//main:t", ns)))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall("rel:Relationship", ns)
        }

        for sheet in workbook.findall(".//main:sheet", ns):
            name = sheet.attrib.get("name", "")
            rel_id = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            target = rel_map[rel_id].lstrip("/")
            sheet_path = target if target.startswith("xl/") else posixpath.normpath("xl/" + target)
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
            sheets[name] = values
    return sheets


def get_required_sheet(sheets, target_name):
    if target_name in sheets:
        return sheets[target_name]
    names = ", ".join(sheets)
    raise KeyError(f"sheet not found: {target_name}; available={names}")


def parse_settings(main_values):
    prefix = clean(main_values[7].get(17, "")) or "PH"
    prefix = prefix.strip("_") or "PH"
    return Settings(
        login_url=clean(main_values[1].get(17, "")),
        course_url=clean(main_values[2].get(17, "")),
        admin_id=clean(main_values[3].get(17, "")),
        admin_pw=clean(main_values[4].get(17, "")),
        class_date=clean(main_values[5].get(17, "")),
        prefix=prefix,
    )


def normalize_group(value):
    text = clean(value)
    if not text:
        return ""
    try:
        return f"{int(float(text)):02d}"
    except ValueError:
        return text.zfill(2) if text.isdigit() else text


def build_tt_assignments(tt_values, prefix):
    assignments = []
    last_group = ""
    max_row = max(tt_values) if tt_values else 1
    for row in range(3, max_row + 1):
        group_value = clean(tt_values[row].get(1, ""))
        if group_value:
            last_group = normalize_group(group_value)
        user_id = clean(tt_values[row].get(6, ""))
        name = clean(tt_values[row].get(5, ""))
        if not user_id:
            continue
        if not last_group:
            raise ValueError(f"row {row} has user_id but no preceding TT group number")
        assignments.append(
            Assignment(
                row=row,
                target_class=f"{prefix}_TT_{last_group}",
                user_id=user_id,
                name=name,
            )
        )
    return assignments


def dedupe_assignments(assignments):
    selected = {}
    duplicates = []
    conflicts = []
    for item in assignments:
        existing = selected.get(item.user_id)
        if existing is None:
            selected[item.user_id] = item
            continue
        if existing.target_class == item.target_class:
            duplicates.append((existing, item))
            continue
        conflicts.append((existing, item))
    return list(selected.values()), duplicates, conflicts


def class_sort_key(class_name):
    match = re.search(r"_(TT|MW)_(\d+)$", class_name)
    if not match:
        return (class_name, 0)
    return (match.group(1), int(match.group(2)))


def id_hash(user_id):
    return hashlib.sha1(user_id.encode("utf-8")).hexdigest()[:10]


def extract_class(text):
    match = re.search(r"\b[A-Z]{2}_(?:MW|TT)_\d{2}\b", text or "")
    return match.group(0) if match else ""


def parse_count(text):
    match = re.search(r"\b(\d+)\s*" + "\uba85" + r"\b", text or "")
    if match:
        return int(match.group(1))
    match = re.search(r"\((\d+)", text or "")
    return int(match.group(1)) if match else None


def parse_rows_filter(raw):
    rows = set()
    for part in (raw or "").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            left, right = part.split("-", 1)
            rows.update(range(int(left), int(right) + 1))
        else:
            rows.add(int(part))
    return rows


def login(page, settings):
    page.goto(settings.login_url)
    page.fill('input[name="tbAdminId"]', settings.admin_id)
    page.fill('input[name="tbAdminPass"]', settings.admin_pw)
    page.press('input[name="tbAdminPass"]', "Enter")
    page.goto(settings.course_url)
    page.wait_for_load_state("load")
    page.select_option('select[name="ddlTargetDate"]', value=settings.class_date)
    page.select_option('select[name="ddlKeyField"]', value="b.m_id")


def scrape_class_group_map(page, settings):
    group_map = {}
    seen_pages = set()
    pending = [GROUP_LIST_URL.format(class_date=settings.class_date)]
    while pending:
        url = pending.pop(0)
        if url in seen_pages:
            continue
        seen_pages.add(url)
        page.goto(url)
        page.wait_for_load_state("load")
        rows = page.evaluate(
            """() => Array.from(document.querySelectorAll('tr')).map((tr) => {
                const text = (tr.innerText || '').trim();
                const input = tr.querySelector('input[name="cbSel"]');
                return { text, groupNo: input ? input.value : "" };
            }).filter((row) => row.groupNo && /202606_S2_2_10_1900_(24|35)_/.test(row.groupNo))"""
        )
        for row in rows:
            teacher = extract_class(row["text"])
            if teacher:
                group_map[teacher] = {
                    "group_no": row["groupNo"],
                    "count": parse_count(row["text"]),
                    "text": row["text"],
                }
        next_urls = page.evaluate(
            """() => Array.from(document.querySelectorAll('a'))
                .map((a) => a.href || '')
                .filter((href) => /ClassGroupList\\.asp\\?page=\\d+/.test(href)
                    && href.includes('ddlKeyTargetDate=202606'))"""
        )
        for next_url in next_urls:
            if next_url not in seen_pages and next_url not in pending:
                pending.append(next_url)
    return group_map


def reset_search(page, settings):
    if not page.url.startswith(settings.course_url.split("?")[0]):
        page.goto(settings.course_url)
        page.wait_for_load_state("load")
    page.select_option('select[name="ddlTargetDate"]', value=settings.class_date)
    page.select_option('select[name="ddlKeyField"]', value="b.m_id")


def current_group_text(detail_page):
    group_no = parse_qs(urlparse(detail_page.url).query).get("group_no", [""])[0]
    return detail_page.evaluate(
        """(groupNo) => {
            const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
            if (!selectElement) return groupNo;
            if (selectElement.selectedIndex >= 0) {
                const selected = (selectElement.options[selectElement.selectedIndex].textContent || '').trim();
                if (selected && selected.includes(groupNo)) return selected;
            }
            for (const option of selectElement.options) {
                const text = (option.textContent || '').trim();
                if (text.includes(groupNo)) return text;
            }
            return groupNo;
        }""",
        group_no,
    )


def current_group_no(detail_page):
    return detail_page.evaluate(
        """() => {
            const field = document.querySelector('input[name="group_no"]');
            return field ? field.value : "";
        }"""
    ) or parse_qs(urlparse(detail_page.url).query).get("group_no", [""])[0]


def open_course_detail(page, settings, user_id):
    reset_search(page, settings)
    page.fill('input[name="tbKeyWord"].font_blue', user_id)
    page.press('input[name="tbKeyWord"].font_blue', "Enter")
    page.wait_for_timeout(500)
    selector = f'a[href*="{settings.class_date}"].button_red_small'
    count = page.locator(selector).count()
    if count < 1:
        raise RuntimeError("course detail link not found")
    with page.context.expect_page(timeout=45000) as page_info:
        page.locator(selector).first.click(timeout=20000)
    detail = page_info.value
    detail.wait_for_load_state("load")
    return detail


def verify_one(page, settings, item):
    detail = open_course_detail(page, settings, item.user_id)
    try:
        current_text = current_group_text(detail)
        current_class = extract_class(current_text)
        group_no = current_group_no(detail)
        option_classes = detail.evaluate(
            """() => Array.from(document.querySelectorAll('select[name="ddlTargetGroupNo"] option'))
                .map((option) => (option.textContent || '').trim())
                .map((text) => {
                    const match = text.match(/\\b[A-Z]{2}_(?:MW|TT)_\\d{2}\\b/);
                    return match ? match[0] : '';
                })
                .filter(Boolean)"""
        )
        return {
            "current_class": current_class,
            "current_group_no": group_no,
            "current_text": current_text,
            "target_available": item.target_class in option_classes,
        }
    finally:
        try:
            if not detail.is_closed():
                detail.close()
        except PlaywrightError:
            pass
        page.bring_to_front()


def move_one(page, settings, item, current_class, forced_group_no=""):
    detail = open_course_detail(page, settings, item.user_id)
    try:
        target = detail.evaluate(
            """(targetClass) => {
                const selectElement = document.querySelector('select[name="ddlTargetGroupNo"]');
                if (!selectElement) return null;
                for (const option of selectElement.options) {
                    const text = (option.textContent || '').trim();
                    if (text.includes(targetClass)) {
                        selectElement.value = option.value;
                        return { value: option.value, text };
                    }
                }
                return null;
            }""",
            item.target_class,
        )
        if not target and not forced_group_no:
            return "TARGET_NOT_FOUND", "target class option was not found"

        target_value = forced_group_no or target["value"]
        if target:
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
                    return "POPUP_CLOSED_DURING_SELECT", "popup closed during target selection"
                raise

            hidden_target = detail.evaluate(
                """() => {
                    const hidden = document.querySelector('input[name="hhdTargetGroupNo"]');
                    return hidden ? hidden.value : "";
                }"""
            )
            target_value = hidden_target or target_value

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
        status = "FORCED_MOVE_SUBMITTED" if forced_group_no and not target else "MOVE_SUBMITTED"
        return status, f"{current_class}->{item.target_class}"
    finally:
        try:
            if not detail.is_closed():
                detail.close()
        except PlaywrightError:
            pass
        page.bring_to_front()


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args():
    parser = argparse.ArgumentParser(description="Assign only TT students from LMS workbook.")
    parser.add_argument("--execute", action="store_true", help="Submit LMS class changes.")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode.")
    parser.add_argument("--limit", type=int, default=0, help="Limit rows for smoke tests.")
    parser.add_argument("--start-row", type=int, default=0, help="Start from a TT sheet row.")
    parser.add_argument("--rows", default="", help="Comma/range TT sheet rows, e.g. 68-75,80.")
    parser.add_argument("--verify-only", action="store_true", help="Do not submit changes.")
    parser.add_argument(
        "--force-missing-targets",
        action="store_true",
        help="If target is absent from the popup select but exists in ClassGroupList, submit with that group number.",
    )
    parser.add_argument(
        "--force-group-no",
        default="",
        help="Explicit target group number to use when the popup select does not contain the target class.",
    )
    parser.add_argument("--dump-groups", action="store_true", help="Print current ClassGroupList mapping and exit.")
    return parser.parse_args()


def main():
    args = parse_args()
    started = time.time()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    workbook_path = find_workbook()
    sheets = load_workbook_values(workbook_path)
    main_values = get_required_sheet(sheets, MAIN_SHEET)
    tt_values = get_required_sheet(sheets, TT_SHEET)
    settings = parse_settings(main_values)
    assignments = build_tt_assignments(tt_values, settings.prefix)
    if args.start_row:
        assignments = [item for item in assignments if item.row >= args.start_row]
    row_filter = parse_rows_filter(args.rows)
    if row_filter:
        assignments = [item for item in assignments if item.row in row_filter]
    assignments, duplicates, conflicts = dedupe_assignments(assignments)
    assignments = sorted(assignments, key=lambda item: (class_sort_key(item.target_class), item.row))
    if args.limit:
        assignments = assignments[: args.limit]

    distribution = Counter(item.target_class for item in assignments)
    summary = {
        "workbook": str(workbook_path),
        "class_date": settings.class_date,
        "prefix": settings.prefix,
        "tt_total": len(assignments),
        "tt_class_count": len(distribution),
        "duplicates_same_target": len(duplicates),
        "conflicts": len(conflicts),
        "distribution": dict(sorted(distribution.items(), key=lambda kv: class_sort_key(kv[0]))),
    }
    summary_path = BASE_DIR / f"lms_tt_assignment_summary_{timestamp}.json"
    result_path = BASE_DIR / f"lms_tt_assignment_results_{timestamp}.csv"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SUMMARY_JSON\t" + json.dumps(summary, ensure_ascii=False), flush=True)
    print(f"SUMMARY_FILE\t{summary_path}", flush=True)

    if conflicts:
        conflict_path = BASE_DIR / f"lms_tt_assignment_conflicts_{timestamp}.csv"
        rows = [
            {
                "existing_row": left.row,
                "existing_target": left.target_class,
                "new_row": right.row,
                "new_target": right.target_class,
                "id_hash": id_hash(left.user_id),
            }
            for left, right in conflicts
        ]
        write_csv(conflict_path, rows, ["existing_row", "existing_target", "new_row", "new_target", "id_hash"])
        print(f"CONFLICT_FILE\t{conflict_path}", flush=True)
        return 2

    if not assignments:
        print("NO_ASSIGNMENTS", flush=True)
        return 3

    if not args.execute or args.verify_only:
        print("DRY_RUN_ONLY", flush=True)
        return 0

    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headless, args=["--disable-popup-blocking"])
        try:
            page = browser.new_page()
            login(page, settings)
            if args.dump_groups:
                group_map = scrape_class_group_map(page, settings)
                compact_map = {
                    key: {"group_no": value["group_no"], "count": value["count"]}
                    for key, value in sorted(group_map.items(), key=lambda kv: class_sort_key(kv[0]))
                }
                print("GROUP_COUNTS_JSON\t" + json.dumps(compact_map, ensure_ascii=False), flush=True)
                return 0
            group_map = scrape_class_group_map(page, settings) if args.force_missing_targets else {}
            if args.force_missing_targets:
                forced_targets = {
                    key: value["group_no"]
                    for key, value in group_map.items()
                    if key.startswith(f"{settings.prefix}_TT_")
                }
                print("GROUP_MAP_JSON\t" + json.dumps(forced_targets, ensure_ascii=False), flush=True)
                reset_search(page, settings)
            for index, item in enumerate(assignments, start=1):
                row = {
                    "row": item.row,
                    "target_class": item.target_class,
                    "id_hash": id_hash(item.user_id),
                    "before_class": "",
                    "before_group_no": "",
                    "after_class": "",
                    "after_group_no": "",
                    "target_group_no": "",
                    "target_available": "",
                    "status": "",
                    "message": "",
                }
                try:
                    before = verify_one(page, settings, item)
                    row["before_class"] = before["current_class"]
                    row["before_group_no"] = before["current_group_no"]
                    row["target_available"] = before["target_available"]
                    if before["current_class"] == item.target_class:
                        row["status"] = "ALREADY_OK"
                        row["after_class"] = before["current_class"]
                        row["after_group_no"] = before["current_group_no"]
                    else:
                        forced_group_no = ""
                        if args.force_group_no and not before["target_available"]:
                            forced_group_no = args.force_group_no
                        if args.force_missing_targets and not before["target_available"]:
                            forced_group_no = group_map.get(item.target_class, {}).get("group_no", "")
                        row["target_group_no"] = forced_group_no
                        move_status, move_message = move_one(
                            page,
                            settings,
                            item,
                            before["current_class"],
                            forced_group_no=forced_group_no,
                        )
                        row["message"] = move_message
                        if move_status in {"MOVE_SUBMITTED", "FORCED_MOVE_SUBMITTED"}:
                            after = verify_one(page, settings, item)
                            row["after_class"] = after["current_class"]
                            row["after_group_no"] = after["current_group_no"]
                            if after["current_class"] == item.target_class:
                                row["status"] = "MOVED_OK"
                            elif forced_group_no and after["current_group_no"] == forced_group_no:
                                row["status"] = "MOVED_GROUP_OK_UNSCHEDULED"
                            else:
                                row["status"] = "VERIFY_FAIL"
                        else:
                            row["status"] = move_status
                    if not row["after_class"]:
                        after = verify_one(page, settings, item)
                        row["after_class"] = after["current_class"]
                        row["after_group_no"] = after["current_group_no"]
                        if row["status"] == "ALREADY_OK" and after["current_class"] != item.target_class:
                            row["status"] = "VERIFY_FAIL"
                except Exception as exc:
                    row["status"] = "ERROR"
                    row["message"] = repr(exc)
                results.append(row)
                if index % 10 == 0 or index == len(assignments):
                    ok_count = sum(1 for result in results if result["status"] in {"ALREADY_OK", "MOVED_OK"})
                    print(f"PROGRESS\t{index}/{len(assignments)}\tOK={ok_count}", flush=True)
        finally:
            browser.close()

    write_csv(
        result_path,
        results,
        [
            "row",
            "target_class",
            "id_hash",
            "before_class",
            "before_group_no",
            "after_class",
            "after_group_no",
            "target_group_no",
            "target_available",
            "status",
            "message",
        ],
    )
    status_counts = Counter(row["status"] for row in results)
    run_summary = {
        **summary,
        "result_csv": str(result_path),
        "status_counts": dict(status_counts),
        "seconds": round(time.time() - started, 1),
    }
    run_summary_path = BASE_DIR / f"lms_tt_assignment_run_summary_{timestamp}.json"
    run_summary_path.write_text(json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("RUN_SUMMARY_JSON\t" + json.dumps(run_summary, ensure_ascii=False), flush=True)
    print(f"RESULT_FILE\t{result_path}", flush=True)
    print(f"RUN_SUMMARY_FILE\t{run_summary_path}", flush=True)
    bad_count = sum(
        1
        for row in results
        if row["status"] not in {"ALREADY_OK", "MOVED_OK", "MOVED_GROUP_OK_UNSCHEDULED"}
    )
    return 1 if bad_count else 0


if __name__ == "__main__":
    sys.exit(main())
