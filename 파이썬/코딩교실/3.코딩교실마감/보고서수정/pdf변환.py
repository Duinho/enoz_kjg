# -*- coding: utf-8 -*-
"""
Convert report files to PDF.

- Input: files under REPORT_ROOT (default: BASE_DIR/보고서)
- Output: BASE_DIR/pdf
- Supported: .doc/.docx (MS Word), .hwp/.hwpx (Hancom HWP)
Requirements:
  - Windows
  - pip install pywin32
  - MS Word for .doc/.docx
  - Hancom Office (HWP) for .hwp/.hwpx
"""

import os
import sys
import shutil
import time

import pythoncom
import win32com.client as win32

# ===== CONFIG =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_ROOT = os.path.join(BASE_DIR, "보고서")
RECURSIVE = True
INCLUDE_ROOT = True
OVERWRITE = True

WORD_VISIBLE = False
HWP_VISIBLE = False
KILL_EXISTING_WORD = False
KILL_EXISTING_HWP = False
HWP_OPEN_RETRY = 3
HWP_OPEN_WAIT_SEC = 0.6

WORD_EXTS = {".doc", ".docx"}
HWP_EXTS = {".hwp", ".hwpx"}

wdExportFormatPDF = 17  # Word SaveAs2/FileFormat=17 (PDF)


def purge_gen_cache():
    try:
        p = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "gen_py", sys.winver)
        shutil.rmtree(p, ignore_errors=True)
    except Exception:
        pass


def kill_process(image_name):
    try:
        os.system(f"taskkill /F /IM {image_name} >NUL 2>&1")
    except Exception:
        pass


def list_target_folders(root, recursive=True, include_root=False):
    if not os.path.isdir(root):
        return []
    subdirs = []
    if include_root:
        subdirs.append(root)
    if recursive:
        for r, dirs, _ in os.walk(root):
            for d in dirs:
                subdirs.append(os.path.join(r, d))
    else:
        for name in os.listdir(root):
            p = os.path.join(root, name)
            if os.path.isdir(p):
                subdirs.append(p)
    # Keep deterministic order while keeping root first if included.
    if include_root:
        head = subdirs[:1]
        tail = sorted(subdirs[1:])
        return head + tail
    return sorted(subdirs)


def collect_files_in_folder(folder, exts):
    out = []
    if not os.path.isdir(folder):
        return out
    for f in os.listdir(folder):
        if f.startswith("~$"):
            continue
        p = os.path.join(folder, f)
        if os.path.isfile(p) and os.path.splitext(f)[1].lower() in exts:
            out.append(p)
    return sort_paths(out)


def sort_paths(paths):
    return sorted(paths, key=lambda p: (os.path.splitext(os.path.basename(p))[0].lower(), p.lower()))


def ensure_unique_path(dest_path):
    if not os.path.exists(dest_path):
        return dest_path
    root, ext = os.path.splitext(dest_path)
    idx = 1
    while True:
        candidate = f"{root}_{idx}{ext}"
        if not os.path.exists(candidate):
            return candidate
        idx += 1


def open_word_app():
    word = win32.Dispatch("Word.Application")
    word.Visible = WORD_VISIBLE
    try:
        word.DisplayAlerts = 0
    except Exception:
        pass
    try:
        word.AutomationSecurity = 3  # msoAutomationSecurityForceDisable
    except Exception:
        pass
    return word


def open_hwp_app():
    last_error = None
    for prog_id in ("HWPFrame.HwpObject", "HwpCtrl.HwpObject"):
        try:
            hwp = win32.Dispatch(prog_id)
            try:
                hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckModule")
            except Exception:
                pass
            try:
                hwp.XHwpWindows.Item(0).Visible = HWP_VISIBLE
            except Exception:
                try:
                    hwp.Visible = HWP_VISIBLE
                except Exception:
                    pass
            return hwp
        except Exception as exc:
            last_error = exc
    raise last_error


def hwp_open_doc(hwp, src_path):
    for _ in range(max(1, HWP_OPEN_RETRY)):
        try:
            ret = hwp.Open(os.path.abspath(src_path), "HWP", "forceopen:true")
        except Exception:
            ret = False
        if ret:
            return True
        # Allow time for any security prompt to be acknowledged.
        time.sleep(HWP_OPEN_WAIT_SEC)
        try:
            if os.path.normcase(getattr(hwp, "Path", "")) == os.path.normcase(os.path.abspath(src_path)):
                return True
        except Exception:
            pass
    return False


def convert_word_files(word, files, pdf_root, prefix_map=None):
    if not files:
        return 0, 0
    if prefix_map is None:
        prefix_map = {}
    if word is None:
        print(f"    SKIP Word: {len(files)} file(s) (Word not available)")
        return 0, len(files)

    ok, fail = 0, 0
    for src in files:
        rel_path = os.path.relpath(src, REPORT_ROOT)
        base = os.path.splitext(os.path.basename(src))[0]
        name_prefix = prefix_map.get(src, "")
        dest_pdf = os.path.abspath(os.path.join(pdf_root, f"{name_prefix}{base}.pdf"))
        if not OVERWRITE and os.path.exists(dest_pdf):
            dest_pdf = ensure_unique_path(dest_pdf)

        try:
            doc = word.Documents.Open(
                FileName=os.path.abspath(src),
                ConfirmConversions=False,
                ReadOnly=True,
                AddToRecentFiles=False,
                Revert=False,
                Visible=False,
            )
        except Exception as exc:
            print(f"    FAIL Word open: {rel_path} | {exc}")
            fail += 1
            continue

        try:
            try:
                doc.ExportAsFixedFormat(
                    OutputFileName=dest_pdf,
                    ExportFormat=wdExportFormatPDF,
                    OpenAfterExport=False,
                    OptimizeFor=0,  # wdExportOptimizeForPrint
                    Range=0,  # wdExportAllDocument
                    From=1,
                    To=1,
                    Item=0,  # wdExportDocumentContent
                    IncludeDocProps=True,
                    KeepIRM=True,
                    CreateBookmarks=0,  # wdExportCreateNoBookmarks
                    DocStructureTags=True,
                    BitmapMissingFonts=True,
                    UseISO19005_1=False,
                )
            except Exception:
                doc.SaveAs2(dest_pdf, FileFormat=wdExportFormatPDF)
            ok += 1
        except Exception as exc:
            print(f"    FAIL Word PDF: {rel_path} | {exc}")
            fail += 1
        finally:
            try:
                doc.Close(False)
            except Exception:
                pass
    return ok, fail


def _hwp_save_as_pdf(hwp, dest_pdf):
    act = hwp.CreateAction("FileSaveAs")
    ps = act.CreateSet()
    act.GetDefault(ps)
    ps.SetItem("FileName", dest_pdf)
    ps.SetItem("Format", "PDF")
    act.Execute(ps)


def _hwp_close(hwp):
    try:
        hwp.Run("FileClose")
        return
    except Exception:
        pass
    try:
        hwp.HAction.Run("FileClose")
    except Exception:
        pass


def convert_hwp_files(hwp, files, pdf_root, prefix_map=None):
    if not files:
        return 0, 0
    if prefix_map is None:
        prefix_map = {}
    if hwp is None:
        print(f"    SKIP HWP: {len(files)} file(s) (HWP not available)")
        return 0, len(files)

    ok, fail = 0, 0
    for src in files:
        rel_path = os.path.relpath(src, REPORT_ROOT)
        base = os.path.splitext(os.path.basename(src))[0]
        name_prefix = prefix_map.get(src, "")
        dest_pdf = os.path.abspath(os.path.join(pdf_root, f"{name_prefix}{base}.pdf"))
        if not OVERWRITE and os.path.exists(dest_pdf):
            dest_pdf = ensure_unique_path(dest_pdf)

        if not hwp_open_doc(hwp, src):
            print(f"    FAIL HWP open: {rel_path} | open failed")
            fail += 1
            continue

        try:
            _hwp_save_as_pdf(hwp, dest_pdf)
            ok += 1
        except Exception as exc:
            print(f"    FAIL HWP PDF: {rel_path} | {exc}")
            fail += 1
        finally:
            _hwp_close(hwp)
    return ok, fail


def main():
    purge_gen_cache()
    if KILL_EXISTING_WORD:
        kill_process("WINWORD.EXE")
    if KILL_EXISTING_HWP:
        kill_process("Hwp.exe")

    pdf_root = os.path.join(BASE_DIR, "pdf")
    os.makedirs(pdf_root, exist_ok=True)

    if not os.path.isdir(REPORT_ROOT):
        print(f"Report folder not found: {REPORT_ROOT}")
        sys.exit(1)

    targets = list_target_folders(REPORT_ROOT, RECURSIVE, INCLUDE_ROOT)
    if not targets:
        print("No target folders found.")
        sys.exit(0)

    tasks = []
    for folder in targets:
        word_files = collect_files_in_folder(folder, WORD_EXTS)
        hwp_files = collect_files_in_folder(folder, HWP_EXTS)
        if not word_files and not hwp_files:
            continue
        all_files = sort_paths(word_files + hwp_files)
        tasks.append((folder, word_files, hwp_files, all_files))

    if not tasks:
        print("No files found to convert.")
        sys.exit(0)

    pythoncom.CoInitialize()
    word = None
    hwp = None
    total_ok = total_fail = 0
    word_init_failed = False
    hwp_init_failed = False
    try:
        print(f"Targets: {len(tasks)} folder(s) | Output: {pdf_root}\n")
        for idx, (folder, word_files, hwp_files, all_files) in enumerate(tasks, 1):
            prefix_map = {}
            if all_files:
                width = max(2, len(str(len(all_files))))
                for file_idx, src in enumerate(all_files, 1):
                    prefix_map[src] = f"{idx}.{file_idx:0{width}d}_"

            if word_files and word is None and not word_init_failed:
                try:
                    word = open_word_app()
                except Exception as exc:
                    word_init_failed = True
                    print(f"Word init failed: {exc}")

            if hwp_files and hwp is None and not hwp_init_failed:
                try:
                    hwp = open_hwp_app()
                except Exception as exc:
                    hwp_init_failed = True
                    print(f"HWP init failed: {exc}")

            ok1, fail1 = convert_word_files(word, word_files, pdf_root, prefix_map)
            ok2, fail2 = convert_hwp_files(hwp, hwp_files, pdf_root, prefix_map)
            ok = ok1 + ok2
            fail = fail1 + fail2
            if ok or fail:
                rel_name = os.path.relpath(folder, REPORT_ROOT)
                if rel_name == ".":
                    rel_name = os.path.basename(REPORT_ROOT)
                print(f"[{idx}/{len(tasks)}] {rel_name} | ok {ok} | fail {fail}")
                total_ok += ok
                total_fail += fail

        print(f"\nDone | ok {total_ok} | fail {total_fail}")
        print(f"PDF output: {pdf_root}")
    finally:
        if word:
            try:
                word.Quit()
            except Exception:
                pass
        if hwp:
            try:
                hwp.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()
