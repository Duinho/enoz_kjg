import argparse
import csv
import json
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from run_lms_assign_tt_students import (
    Assignment,
    MAIN_SHEET,
    TT_SHEET,
    clean,
    class_sort_key,
    dedupe_assignments,
    find_workbook,
    get_required_sheet,
    id_hash,
    load_workbook_values,
    login,
    move_one,
    normalize_group,
    parse_rows_filter,
    parse_settings,
    verify_one,
    write_csv,
)


BASE_DIR = Path(__file__).resolve().parent
MW_SHEET = "\uc6d4\uc218"


def build_sheet_assignments(sheet_values, prefix, code):
    items = []
    last_group = ""
    max_row = max(sheet_values) if sheet_values else 1
    for row in range(3, max_row + 1):
        group_value = clean(sheet_values[row].get(1, ""))
        if group_value:
            last_group = normalize_group(group_value)
        user_id = clean(sheet_values[row].get(6, ""))
        name = clean(sheet_values[row].get(5, ""))
        if not user_id:
            continue
        if not last_group:
            raise ValueError(f"row {row} has user_id but no preceding group number")
        items.append(Assignment(row=row, target_class=f"{prefix}_{code}_{last_group}", user_id=user_id, name=name))
    return items


def build_main_range(values, class_col, name_col, id_col):
    items = []
    max_row = max(values) if values else 1
    for row in range(2, max_row + 1):
        target = clean(values[row].get(class_col, ""))
        name = clean(values[row].get(name_col, ""))
        user_id = clean(values[row].get(id_col, ""))
        if not target and not user_id:
            continue
        if not target or not user_id:
            continue
        items.append(Assignment(row=row, target_class=target, user_id=user_id, name=name))
    return items


def build_source_assignments(source):
    workbook_path = find_workbook()
    sheets = load_workbook_values(workbook_path)
    main_values = get_required_sheet(sheets, MAIN_SHEET)
    settings = parse_settings(main_values)
    mw_values = get_required_sheet(sheets, MW_SHEET)
    tt_values = get_required_sheet(sheets, TT_SHEET)

    mw_items = build_sheet_assignments(mw_values, settings.prefix, "MW")
    tt_items = build_sheet_assignments(tt_values, settings.prefix, "TT")
    ghost_in_items = build_main_range(main_values, 6, 7, 8)
    ghost_out_items = build_main_range(main_values, 11, 12, 13)

    if source == "mw":
        items = mw_items
    elif source == "tt":
        items = tt_items
    elif source == "ghost-in":
        items = ghost_in_items
    elif source == "ghost-out-actionable":
        protected_ids = {item.user_id for item in mw_items + tt_items + ghost_in_items}
        items = [item for item in ghost_out_items if item.user_id not in protected_ids]
    elif source == "all-safe":
        protected_ids = {item.user_id for item in mw_items + tt_items + ghost_in_items}
        actionable_ghost_out = [item for item in ghost_out_items if item.user_id not in protected_ids]
        items = mw_items + tt_items + ghost_in_items + actionable_ghost_out
    else:
        raise ValueError(f"unknown source: {source}")
    return workbook_path, settings, items


def parse_args():
    parser = argparse.ArgumentParser(description="Assign LMS students from a selected workbook source.")
    parser.add_argument(
        "--source",
        required=True,
        choices=["mw", "tt", "ghost-in", "ghost-out-actionable", "all-safe"],
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--rows", default="")
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def main():
    args = parse_args()
    started = time.time()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    workbook_path, settings, assignments = build_source_assignments(args.source)
    row_filter = parse_rows_filter(args.rows)
    if row_filter:
        assignments = [item for item in assignments if item.row in row_filter]
    assignments, duplicates, conflicts = dedupe_assignments(assignments)
    assignments = sorted(assignments, key=lambda item: (class_sort_key(item.target_class), item.row))
    if args.limit:
        assignments = assignments[: args.limit]

    distribution = Counter(item.target_class for item in assignments)
    summary = {
        "source": args.source,
        "workbook": str(workbook_path),
        "class_date": settings.class_date,
        "prefix": settings.prefix,
        "total": len(assignments),
        "class_count": len(distribution),
        "duplicates_same_target": len(duplicates),
        "conflicts": len(conflicts),
        "distribution": dict(sorted(distribution.items(), key=lambda kv: class_sort_key(kv[0]))),
    }
    summary_path = BASE_DIR / f"lms_source_{args.source}_summary_{timestamp}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SUMMARY_JSON\t" + json.dumps(summary, ensure_ascii=False), flush=True)
    print(f"SUMMARY_FILE\t{summary_path}", flush=True)

    if conflicts:
        print("CONFLICTS_FOUND", flush=True)
        return 2
    if not args.execute:
        print("DRY_RUN_ONLY", flush=True)
        return 0

    results = []
    result_path = BASE_DIR / f"lms_source_{args.source}_results_{timestamp}.csv"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headless, args=["--disable-popup-blocking"])
        try:
            page = browser.new_page()
            login(page, settings)
            for index, item in enumerate(assignments, start=1):
                row = {
                    "row": item.row,
                    "target_class": item.target_class,
                    "id_hash": id_hash(item.user_id),
                    "before_class": "",
                    "before_group_no": "",
                    "after_class": "",
                    "after_group_no": "",
                    "status": "",
                    "message": "",
                }
                try:
                    before = verify_one(page, settings, item)
                    row["before_class"] = before["current_class"]
                    row["before_group_no"] = before["current_group_no"]
                    if before["current_class"] == item.target_class:
                        row["after_class"] = before["current_class"]
                        row["after_group_no"] = before["current_group_no"]
                        row["status"] = "ALREADY_OK"
                    else:
                        move_status, move_message = move_one(page, settings, item, before["current_class"])
                        row["message"] = move_message
                        if move_status == "MOVE_SUBMITTED":
                            after = verify_one(page, settings, item)
                            row["after_class"] = after["current_class"]
                            row["after_group_no"] = after["current_group_no"]
                            row["status"] = "MOVED_OK" if after["current_class"] == item.target_class else "VERIFY_FAIL"
                        else:
                            row["status"] = move_status
                except Exception as exc:
                    row["status"] = "ERROR"
                    row["message"] = repr(exc)
                results.append(row)
                if index % 25 == 0 or index == len(assignments):
                    ok_count = sum(1 for result in results if result["status"] in {"ALREADY_OK", "MOVED_OK"})
                    print(f"PROGRESS\t{index}/{len(assignments)}\tOK={ok_count}", flush=True)
        finally:
            browser.close()

    write_csv(
        result_path,
        results,
        ["row", "target_class", "id_hash", "before_class", "before_group_no", "after_class", "after_group_no", "status", "message"],
    )
    status_counts = Counter(row["status"] for row in results)
    run_summary = {
        **summary,
        "result_csv": str(result_path),
        "status_counts": dict(status_counts),
        "seconds": round(time.time() - started, 1),
    }
    run_summary_path = BASE_DIR / f"lms_source_{args.source}_run_summary_{timestamp}.json"
    run_summary_path.write_text(json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("RUN_SUMMARY_JSON\t" + json.dumps(run_summary, ensure_ascii=False), flush=True)
    print(f"RESULT_FILE\t{result_path}", flush=True)
    print(f"RUN_SUMMARY_FILE\t{run_summary_path}", flush=True)
    bad_count = sum(1 for row in results if row["status"] not in {"ALREADY_OK", "MOVED_OK"})
    return 1 if bad_count else 0


if __name__ == "__main__":
    sys.exit(main())
