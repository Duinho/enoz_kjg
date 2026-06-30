import argparse
import json
import re
import zipfile
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent
WORKBOOK = BASE_DIR / "LMS전산반배정.xlsx"


def clean(value):
    return "" if value is None else str(value).strip()


def column_index(cell_ref):
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + (ord(char.upper()) - ord("A") + 1)
    return index


def row_index(cell_ref):
    digits = "".join(ch for ch in cell_ref if ch.isdigit())
    return int(digits) if digits else 0


def load_settings():
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
                shared.append("".join(node.text or "" for node in item.findall(".//main:t", ns)))
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall("rel:Relationship", ns)}
        sheet_path = None
        for sheet in workbook.findall(".//main:sheet", ns):
            if sheet.attrib.get("name") == "메인":
                rel_id = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                target = rel_map[rel_id].lstrip("/")
                sheet_path = target if target.startswith("xl/") else "xl/" + target
                break
        root = ET.fromstring(archive.read(sheet_path))
        values = {}
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
            values[(row, col)] = raw
    return {
        "login_url": clean(values.get((1, 17), "")),
        "course_url": clean(values.get((2, 17), "")),
        "admin_id": clean(values.get((3, 17), "")),
        "admin_pw": clean(values.get((4, 17), "")),
        "class_date": clean(values.get((5, 17), "")),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("group_no")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()
    settings = load_settings()
    url = (
        "https://enozsw.enoz.kr/Admin/Class/StudyList.asp?"
        f"ddlTargetDate={settings['class_date']}&ddlKeyField=a.group_no&tbKeyWord={args.group_no}"
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headless, args=["--disable-popup-blocking"])
        try:
            page = browser.new_page()
            page.goto(settings["login_url"])
            page.fill('input[name="tbAdminId"]', settings["admin_id"])
            page.fill('input[name="tbAdminPass"]', settings["admin_pw"])
            page.press('input[name="tbAdminPass"]', "Enter")
            page.wait_for_load_state("load")
            page.goto(url)
            page.wait_for_load_state("load")
            data = page.evaluate(
                """() => {
                    const rows = Array.from(document.querySelectorAll('tr')).map((tr) => {
                        const text = tr.innerText || '';
                        const links = Array.from(tr.querySelectorAll('a')).map((a) => ({
                            text: (a.textContent || '').trim(),
                            href: a.href || '',
                            onclick: a.getAttribute('onclick') || '',
                            cls: a.className || '',
                        }));
                        return {text, links};
                    }).filter((row) => /popCourseEdit|button_red_small|수강수정|ScheduleList/.test(JSON.stringify(row)));
                    return {
                        url: location.href,
                        bodyText: (document.body.innerText || '').slice(0, 20000),
                        rows,
                    };
                }"""
            )
            print(json.dumps(data, ensure_ascii=False, indent=2))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
