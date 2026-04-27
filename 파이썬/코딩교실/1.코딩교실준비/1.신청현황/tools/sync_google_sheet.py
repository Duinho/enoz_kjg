from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path
from typing import Any

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKBOOK = ROOT / "_sincheong" / "코딩교실 신청 현황.xlsx"
DEFAULT_SPREADSHEET_ID = "1eG8aPnjIbI2UQiAJbii6QnCoW2kgUK4fGRwQnKz6JT4"
DEFAULT_SHEETS = ("pohang1", "gumi1")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync local application status workbook to Google Sheets.")
    parser.add_argument("--credentials", required=True, help="Path to Google service-account JSON credentials.")
    parser.add_argument("--workbook", default=str(DEFAULT_WORKBOOK), help="Local workbook path.")
    parser.add_argument("--spreadsheet-id", default=DEFAULT_SPREADSHEET_ID, help="Google spreadsheet ID.")
    parser.add_argument(
        "--sheets",
        default=",".join(DEFAULT_SHEETS),
        help="Comma-separated worksheet names to sync from the local workbook.",
    )
    return parser.parse_args()


def import_gspread():
    try:
        import gspread
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: gspread. Run `py -3 -m pip install -r requirements.txt` first."
        ) from exc
    return gspread


def normalize_cell(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, dt.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, dt.date):
        return value.strftime("%Y-%m-%d")
    return value


def trim_grid(rows: list[list[Any]]) -> list[list[Any]]:
    last_row = 0
    last_col = 0

    for row_index, row in enumerate(rows, start=1):
        row_has_value = False
        for col_index, value in enumerate(row, start=1):
            if value != "":
                row_has_value = True
                last_col = max(last_col, col_index)
        if row_has_value:
            last_row = row_index

    if last_row == 0 or last_col == 0:
        return [[]]

    return [row[:last_col] for row in rows[:last_row]]


def read_workbook_sheet(workbook_path: Path, sheet_name: str) -> list[list[Any]]:
    workbook = openpyxl.load_workbook(workbook_path, data_only=False)
    try:
        if sheet_name not in workbook.sheetnames:
            raise KeyError(f"Sheet not found in local workbook: {sheet_name}")

        worksheet = workbook[sheet_name]
        rows = [
            [normalize_cell(cell.value) for cell in row]
            for row in worksheet.iter_rows()
        ]
        return trim_grid(rows)
    finally:
        workbook.close()


def get_or_create_worksheet(spreadsheet, title: str, rows: int, cols: int):
    try:
        return spreadsheet.worksheet(title)
    except Exception:
        return spreadsheet.add_worksheet(title=title, rows=max(rows, 100), cols=max(cols, 20))


def worksheet_update(worksheet, values: list[list[Any]]) -> None:
    row_count = max(len(values), 1)
    col_count = max((len(row) for row in values), default=1)
    worksheet.resize(rows=max(row_count, 1), cols=max(col_count, 1))
    worksheet.clear()

    if values and values != [[]]:
        try:
            worksheet.update(values=values, range_name="A1", value_input_option="USER_ENTERED")
        except TypeError:
            worksheet.update("A1", values, value_input_option="USER_ENTERED")


def main() -> int:
    args = parse_args()
    workbook_path = Path(args.workbook).resolve()
    credentials_path = Path(args.credentials).resolve()
    sheet_names = [name.strip() for name in args.sheets.split(",") if name.strip()]

    if not workbook_path.exists():
        print(f"Local workbook not found: {workbook_path}", file=sys.stderr)
        return 1
    if not credentials_path.exists():
        print(f"Google credentials not found: {credentials_path}", file=sys.stderr)
        return 1
    if not sheet_names:
        print("No sheets were requested.", file=sys.stderr)
        return 1

    gspread = import_gspread()
    client = gspread.service_account(filename=str(credentials_path))
    spreadsheet = client.open_by_key(args.spreadsheet_id)

    synced = []
    for sheet_name in sheet_names:
        values = read_workbook_sheet(workbook_path, sheet_name)
        rows = max(len(values), 1)
        cols = max((len(row) for row in values), default=1)
        worksheet = get_or_create_worksheet(spreadsheet, sheet_name, rows, cols)
        worksheet_update(worksheet, values)
        synced.append(f"{sheet_name}({rows}x{cols})")

    now = dt.datetime.now()
    try:
        dashboard = spreadsheet.worksheet("대시보드")
        dashboard.update_acell("F1", now.strftime("%m월 %d일 %H시 %M분 현황"))
    except Exception as exc:
        print(f"Dashboard timestamp update skipped: {exc}", file=sys.stderr)

    try:
        log_sheet = get_or_create_worksheet(spreadsheet, "업데이트로그", 100, 4)
        log_sheet.append_row(
            [now.strftime("%Y-%m-%d %H:%M:%S"), "google_sync", ", ".join(synced), "OK"],
            value_input_option="USER_ENTERED",
        )
    except Exception as exc:
        print(f"Update log append skipped: {exc}", file=sys.stderr)

    print("Google Sheets sync completed: " + ", ".join(synced))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
