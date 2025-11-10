# -*- coding: utf-8 -*-
"""
보고서/<각 폴더> 내 .doc/.docx -> BASE_DIR/pdf 로 일괄 변환
- 대상: BASE_DIR/보고서 아래의 하위 폴더들
- 저장: BASE_DIR/pdf (폴더가 없으면 자동 생성)
- 실패 파일만 개별 로그, 폴더별 요약 출력
필수: Windows, MS Word, pip install pywin32
"""

import os, sys, shutil
import pythoncom
import win32com.client as win32

# ===== 옵션 =====
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))     # 이 스크립트가 있는 폴더
REPORT_ROOT    = os.path.join(BASE_DIR, "보고서")               # 순회 시작 루트
RECURSIVE      = True    # 보고서/ 하위 폴더 재귀(True) / 1단계만(False)
OVERWRITE      = True    # 같은 이름의 PDF가 있으면 덮어쓰기
WORD_VISIBLE   = False   # Word 창 표시 여부

# Word 상수
wdExportFormatPDF = 17  # SaveAs2/FileFormat=17 (PDF)

def purge_gen_cache():
    try:
        p = os.path.join(os.environ.get("LOCALAPPDATA",""), "Temp", "gen_py", sys.winver)
        shutil.rmtree(p, ignore_errors=True)
    except:
        pass

def kill_winword():
    try:
        os.system("taskkill /F /IM WINWORD.EXE >NUL 2>&1")
    except:
        pass

def list_subfolders(root, recursive=True):
    """root 이하의 하위 폴더 목록(자기 자신 제외)"""
    subdirs = set()
    if not os.path.isdir(root):
        return []
    if recursive:
        for r, dirs, _ in os.walk(root):
            for d in dirs:
                subdirs.add(os.path.join(r, d))
    else:
        for name in os.listdir(root):
            p = os.path.join(root, name)
            if os.path.isdir(p):
                subdirs.add(p)
    subdirs.discard(root)
    return sorted(subdirs)

def collect_docs_in_folder(folder):
    """폴더 안의 .doc/.docx 파일 리스트 (임시/숨김(~$) 제외)"""
    exts = {".doc", ".docx"}
    out = []
    for f in os.listdir(folder):
        if f.startswith("~$"):
            continue
        p = os.path.join(folder, f)
        if os.path.isfile(p) and os.path.splitext(f)[1].lower() in exts:
            out.append(p)
    return sorted(out, key=lambda p: (os.path.splitext(os.path.basename(p))[0].lower(), p.lower()))

def ensure_unique_path(dest_path):
    """OVERWRITE=False일 때 이름 충돌 방지 (_1, _2...)"""
    if not os.path.exists(dest_path):
        return dest_path
    root, ext = os.path.splitext(dest_path)
    idx = 1
    while True:
        candidate = f"{root}_{idx}{ext}"
        if not os.path.exists(candidate):
            return candidate
        idx += 1

def convert_group_to_pdf(word, folder, pdf_root):
    """
    folder 내 .doc/.docx -> pdf_root에 PDF 저장
    - 성공/실패 수 반환
    - 실패한 파일만 개별 로그 출력
    """
    files = collect_docs_in_folder(folder)
    if not files:
        return 0, 0

    ok, fail = 0, 0
    for src in files:
        base = os.path.splitext(os.path.basename(src))[0]
        dest_pdf = os.path.join(pdf_root, base + ".pdf")
        dest_pdf = os.path.abspath(dest_pdf)

        if not OVERWRITE and os.path.exists(dest_pdf):
            dest_pdf = ensure_unique_path(dest_pdf)

        try:
            doc = word.Documents.Open(
                FileName=os.path.abspath(src),
                ConfirmConversions=False,
                ReadOnly=True,
                AddToRecentFiles=False,
                Revert=False,
                Visible=False
            )
        except Exception as e:
            print(f"    FAIL: {os.path.relpath(src, REPORT_ROOT)} — OPEN 실패: {e}")
            fail += 1
            continue

        try:
            # ExportAsFixedFormat 우선
            try:
                doc.ExportAsFixedFormat(
                    OutputFileName=dest_pdf,
                    ExportFormat=wdExportFormatPDF,
                    OpenAfterExport=False,
                    OptimizeFor=0,           # wdExportOptimizeForPrint
                    Range=0,                 # wdExportAllDocument
                    From=1, To=1,
                    Item=0,                  # wdExportDocumentContent
                    IncludeDocProps=True,
                    KeepIRM=True,
                    CreateBookmarks=0,       # wdExportCreateNoBookmarks
                    DocStructureTags=True,
                    BitmapMissingFonts=True,
                    UseISO19005_1=False
                )
            except Exception:
                # 폴백
                doc.SaveAs2(dest_pdf, FileFormat=wdExportFormatPDF)
            ok += 1
        except Exception as e:
            print(f"    FAIL: {os.path.relpath(src, REPORT_ROOT)} — PDF 저장 실패: {e}")
            fail += 1
        finally:
            try:
                doc.Close(False)
            except:
                pass
    return ok, fail

def main():
    purge_gen_cache()
    kill_winword()

    # 출력 폴더: BASE_DIR/pdf (고정)
    pdf_root = os.path.join(BASE_DIR, "pdf")
    os.makedirs(pdf_root, exist_ok=True)

    if not os.path.isdir(REPORT_ROOT):
        print(f"'보고서' 폴더가 없습니다: {REPORT_ROOT}")
        sys.exit(1)

    # 처리 대상: REPORT_ROOT 아래의 하위 폴더들
    targets = list_subfolders(REPORT_ROOT, RECURSIVE)
    if not targets:
        print("보고서/ 아래에 처리할 하위 폴더가 없습니다.")
        sys.exit(0)

    pythoncom.CoInitialize()
    word = None
    total_ok = total_fail = 0
    try:
        word = win32.Dispatch("Word.Application")
        word.Visible = WORD_VISIBLE
        try: word.DisplayAlerts = 0
        except: pass
        try: word.AutomationSecurity = 3   # msoAutomationSecurityForceDisable
        except: pass

        print(f"{len(targets)}개 폴더 순회 변환 시작 (저장 위치: {pdf_root})\n")
        for idx, folder in enumerate(targets, 1):
            rel_name = os.path.relpath(folder, REPORT_ROOT)
            ok, fail = convert_group_to_pdf(word, folder, pdf_root)
            print(f"[{idx}/{len(targets)}] {rel_name} | 성공 {ok} | 실패 {fail}")
            total_ok  += ok
            total_fail+= fail

        print(f"\n전체 완료 | 성공 {total_ok} | 실패 {total_fail}")
        print(f"PDF 저장 위치: {pdf_root}")
    finally:
        if word:
            try: word.Quit()
            except: pass
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    main()
