import json
from collections import Counter

from run_lms_assign_tt_students import (
    MAIN_SHEET,
    TT_SHEET,
    build_tt_assignments,
    clean,
    find_workbook,
    get_required_sheet,
    load_workbook_values,
    normalize_group,
    parse_settings,
)


MW_SHEET = "\uc6d4\uc218"


def build_sheet_assignments(sheet_values, prefix, code):
    assignments = []
    last_group = ""
    max_row = max(sheet_values) if sheet_values else 1
    for row in range(3, max_row + 1):
        group_value = clean(sheet_values[row].get(1, ""))
        if group_value:
            last_group = normalize_group(group_value)
        user_id = clean(sheet_values[row].get(6, ""))
        if not user_id:
            continue
        assignments.append((row, f"{prefix}_{code}_{last_group}", user_id))
    return assignments


def build_main_range(values, source, class_col, id_col):
    max_row = max(values) if values else 1
    rows = []
    for row in range(2, max_row + 1):
        target = clean(values[row].get(class_col, ""))
        user_id = clean(values[row].get(id_col, ""))
        if target or user_id:
            rows.append((source, row, target, user_id))
    return rows


def count_by_class(rows):
    return dict(sorted(Counter(row[1] if len(row) == 3 else row[2] for row in rows).items()))


def main():
    workbook = find_workbook()
    sheets = load_workbook_values(workbook)
    main_values = get_required_sheet(sheets, MAIN_SHEET)
    settings = parse_settings(main_values)
    mw_values = get_required_sheet(sheets, MW_SHEET)
    tt_values = get_required_sheet(sheets, TT_SHEET)

    mw_rows = build_sheet_assignments(mw_values, settings.prefix, "MW")
    tt_rows = [(item.row, item.target_class, item.user_id) for item in build_tt_assignments(tt_values, settings.prefix)]
    ghost_in = build_main_range(main_values, "ghost_in", 6, 8)
    ghost_out = build_main_range(main_values, "ghost_out", 11, 13)
    protected_ids = {row[2] for row in mw_rows + tt_rows}
    protected_ids.update(row[3] for row in ghost_in)
    actionable_ghost_out = [row for row in ghost_out if row[3] and row[3] not in protected_ids]

    payload = {
        "workbook": str(workbook),
        "prefix": settings.prefix,
        "class_date": settings.class_date,
        "mw_sheet_total": len(mw_rows),
        "tt_sheet_total": len(tt_rows),
        "ghost_in_total": len(ghost_in),
        "ghost_out_total": len(ghost_out),
        "actionable_ghost_out_total": len(actionable_ghost_out),
        "mw_sheet_counts": count_by_class(mw_rows),
        "tt_sheet_counts": count_by_class(tt_rows),
        "ghost_in_counts": dict(sorted(Counter(row[2] for row in ghost_in).items())),
        "ghost_out_counts": dict(sorted(Counter(row[2] for row in ghost_out).items())),
        "actionable_ghost_out_counts": dict(sorted(Counter(row[2] for row in actionable_ghost_out).items())),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
