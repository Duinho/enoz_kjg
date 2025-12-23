# 결과보고서매크로.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox

import 이름O처리          # 이름 O 처리 모듈
import 구글폼응답_대상    # 만족도조사(대상) 모듈
import 구글폼응답_폼      # 만족도조사(폼) 모듈
import 학교알리미         # 학교알리미 모듈


# 메인 윈도우 생성
root = tk.Tk()
root.title("업무자동화 도구")
root.geometry("900x900")

# 제목 레이블
title_label = tk.Label(root, text="업무자동화 도구", font=("Arial", 16))
title_label.pack(pady=10)

# 프레임 생성 (1~6)
frame1 = tk.LabelFrame(root, text="1. 이름 O 처리",       font=("Arial", 14), padx=10, pady=10)
frame2 = tk.LabelFrame(root, text="2. 구글폼 응답(대상)",  font=("Arial", 14), padx=10, pady=10)
frame3 = tk.LabelFrame(root, text="3. 구글폼 응답(폼)",    font=("Arial", 14), padx=10, pady=10)
frame4 = tk.LabelFrame(root, text="4. 학교알리미",        font=("Arial", 14), padx=10, pady=10)
frame5 = tk.LabelFrame(root, text="5",                    font=("Arial", 14), padx=10, pady=10)
frame6 = tk.LabelFrame(root, text="6",                    font=("Arial", 14), padx=10, pady=10)

frame1.place(x=0,   y=50,  width=300, height=200)
frame2.place(x=300, y=50,  width=300, height=200)
frame3.place(x=600, y=50,  width=300, height=200)
frame4.place(x=0,   y=250, width=300, height=200)
frame5.place(x=300, y=250, width=300, height=200)
frame6.place(x=600, y=250, width=300, height=200)


# =========================
#  1. 이름 O 처리
# =========================
def run_name_o_process():
    filepath = filedialog.askopenfilename(
        title="이름 O 처리할 엑셀 파일 선택",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if not filepath:
        return

    저장_경로 = filedialog.asksaveasfilename(
        title="결과를 저장할 위치 선택",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile="이름O처리_결과.xlsx"
    )
    if not 저장_경로:
        return

    try:
        이름O처리.process_names_in_excel(filepath, 저장_경로)
        messagebox.showinfo("완료", "이름 O 처리가 완료되었습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"이름 O 처리 중 오류가 발생했습니다:\n{e}")


btn_noc_download = tk.Button(
    frame1,
    text="이름 O 처리 양식 받기",
    width=30, height=2,
    command=이름O처리.download_template_noc
)
btn_noc_upload = tk.Button(
    frame1,
    text="이름 O 처리 파일 올리기",
    width=30, height=2,
    command=run_name_o_process
)
btn_noc_download.pack(pady=10)
btn_noc_upload.pack(pady=10)


# =========================
#  2. 만족도조사(대상)
# =========================
def run_satisfaction_target():
    filepath = filedialog.askopenfilename(
        title="구글폼 응답(대상) 양식 엑셀 선택",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if not filepath:
        return

    try:
        구글폼응답_대상.run_from_excel(filepath)
        messagebox.showinfo("완료", "구글폼 응답(대상) 자동화가 완료되었습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"구글폼 응답(대상) 자동화 중 오류가 발생했습니다:\n{e}")


btn_satis_target_tpl = tk.Button(
    frame2,
    text="구글폼 응답(대상) 양식 받기",
    width=30, height=2,
    command=구글폼응답_대상.download_template_iloom
)
btn_satis_target_run = tk.Button(
    frame2,
    text="구글폼 응답(대상) 자동화 실행",
    width=30, height=2,
    command=run_satisfaction_target
)
btn_satis_target_tpl.pack(pady=10)
btn_satis_target_run.pack(pady=10)


# =========================
#  3. 만족도조사(폼)
# =========================
def run_satisfaction_form():
    filepath = filedialog.askopenfilename(
        title="구글폼 응답(폼) 양식 엑셀 선택",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if not filepath:
        return

    try:
        # 만족도조사_폼 모듈의 메인 실행 함수 이름에 맞게 수정
        구글폼응답_폼.run_from_excel_form(filepath)
        messagebox.showinfo("완료", "구글폼 응답(폼) 자동화가 완료되었습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"구글폼 응답(폼) 자동화 중 오류가 발생했습니다:\n{e}")


btn_satis_form_tpl = tk.Button(
    frame3,
    text="구글폼 응답(폼) 양식 받기",
    width=30, height=2,
    # 여기도 download_template_form 으로 수정
    command=구글폼응답_폼.download_template_form
)
btn_satis_form_run = tk.Button(
    frame3,
    text="구글폼 응답(폼) 자동화 실행",
    width=30, height=2,
    command=run_satisfaction_form
)
btn_satis_form_tpl.pack(pady=10)
btn_satis_form_run.pack(pady=10)

# =========================
#  4. 학교알리미
# =========================
def run_school_alert():
    filepath = filedialog.askopenfilename(
        title="학교알리미 양식 파일 선택",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if not filepath:
        return

    try:
        학교알리미.run_from_excel(filepath)
        messagebox.showinfo("완료", "학교알리미 자동화가 완료되었습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"학교알리미 실행 중 오류가 발생했습니다:\n{e}")


btn_school_template = tk.Button(
    frame4,
    text="학교알리미 양식 받기",
    width=30, height=2,
    command=학교알리미.download_template_school
)
btn_school_run = tk.Button(
    frame4,
    text="학교알리미 실행",
    width=30, height=2,
    command=run_school_alert
)
btn_school_template.pack(pady=10)
btn_school_run.pack(pady=10)


# 5, 6은 비워둔 상태 (추가 기능용)

# 메인 루프
root.mainloop()
