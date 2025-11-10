import openpyxl
import os
from playwright.sync_api import sync_playwright
import time
import random
from tkinter import filedialog, messagebox, simpledialog
import tkinter as tk
import pandas as pd
import 이름O처리  # 이름O처리 기능을 포함한 모듈
import 역량향상도평가  # 역량향상도평가 기능을 포함한 모듈
import 만족도조사
import 사전역량조사

# 메인 윈도우 생성
root = tk.Tk()
root.title("결과보고서 매크로")
root.geometry("900x900")

# 제목 레이블 생성
title_label = tk.Label(root, text="결과보고서 매크로", font=("Arial", 16))
title_label.pack(pady=10)

# 세 개의 프레임 생성
frame1 = tk.LabelFrame(root, text="이름 O 처리", font=("Arial", 14), padx=10, pady=10)
frame2 = tk.LabelFrame(root, text="역량향상도평가", font=("Arial", 14), padx=10, pady=10)
frame3 = tk.LabelFrame(root, text="만족도조사", font=("Arial", 14), padx=10, pady=10)
frame4 = tk.LabelFrame(root, text="사전역량조사", font=("Arial", 14), padx=10, pady=10)
frame5 = tk.LabelFrame(root, text="5", font=("Arial", 14), padx=10, pady=10)
frame6 = tk.LabelFrame(root, text="6", font=("Arial", 14), padx=10, pady=10)

frame1.place(x=0, y=50, width=300, height=200)
frame2.place(x=300, y=50, width=300, height=200)
frame3.place(x=600, y=50, width=300, height=200)
frame4.place(x=0, y=250, width=300, height=200)
frame5.place(x=300, y=250, width=300, height=200)
frame6.place(x=600, y=250, width=300, height=200)


# 기능 A: 이름 O 처리
def noc_excel():
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
    if filepath:
        if messagebox.askyesno("변환 확인", "선택한 파일의 B열 이름을 변환하고 저장하시겠습니까?"):
            저장_경로 = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile="이름O처리_결과.xlsx"
            )
            이름O처리.process_names_in_excel(filepath,저장_경로)


btn_noc_download = tk.Button(frame1, text="양식 엑셀 다운받기", width=30, height=2, command=이름O처리.download_template_noc)
btn_noc_upload = tk.Button(frame1, text="엑셀 파일 올리기", width=30, height=2, command=noc_excel)
btn_noc_download.pack(pady=15)
btn_noc_upload.pack(pady=15)

# 기능 B: 역량향상도 평가

def perform_yl():
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
    if filepath:
        error_rate = simpledialog.askfloat("오답률 설정", "문항당 오답률 입력 (예: 0.008)", initialvalue=0.008, minvalue=0.0, maxvalue=1.0)
        if error_rate is not None:
            역량향상도평가.동작(filepath, error_rate)
        else:
            messagebox.showerror("오류", "오답률이 설정되지 않았습니다.")

btn_yl_download = tk.Button(frame2, text="역량향상도평가 양식 다운받기", width=30, height=2, command=역량향상도평가.download_template_yl)
btn_yl_auto = tk.Button(frame2, text="역량향상도 평가 자동화 실행", width=30, height=2, command=perform_yl)
btn_yl_download.pack(pady=15)
btn_yl_auto.pack(pady=15)

# 기능 C: 만족도 조사
lbl_link = tk.Label(frame3, text="링크:")
lbl_link.grid(row=0, column=0, sticky='e')
entry_link = tk.Entry(frame3, width=20)
entry_link.grid(row=0, column=1, sticky='w')

lbl_repeat = tk.Label(frame3, text="반복횟수:")
lbl_repeat.grid(row=1, column=0, sticky='e')
entry_repeat = tk.Entry(frame3, width=20)
entry_repeat.grid(row=1, column=1, sticky='w')

lbl_evaluation_count = tk.Label(frame3, text="역량 향상 평가 문항 수:")
lbl_evaluation_count.grid(row=2, column=0, sticky='e')
entry_evaluation_count = tk.Entry(frame3, width=20)
entry_evaluation_count.grid(row=2, column=1, sticky='w')

lbl_satisfaction_count = tk.Label(frame3, text="만족도 조사 문항 수:")
lbl_satisfaction_count.grid(row=3, column=0, sticky='e')
entry_satisfaction_count = tk.Entry(frame3, width=20)
entry_satisfaction_count.grid(row=3, column=1, sticky='w')

# 추가 문구를 별도의 행에 배치
lbl_note = tk.Label(frame3, text="※ 9번 문항 필수 체크를 해제한 후 실행해주세요.", fg="red", font=("Arial", 10, "italic"))
lbl_note.grid(row=4, column=0, columnspan=2, pady=0)


def run_survey():
    link = entry_link.get()
    repeat = entry_repeat.get()
    evaluation_count = entry_evaluation_count.get()
    satisfaction_count = entry_satisfaction_count.get()
    if not link:
        messagebox.showerror("오류", "링크를 입력해주세요.")
        return
    if not repeat.isdigit() or int(repeat) <= 0:
        messagebox.showerror("오류", "유효한 반복 횟수를 입력해주세요.")
        return
    if not evaluation_count or not evaluation_count.isdigit() or int(evaluation_count) < 0:
        messagebox.showerror("오류", "유효한 역량 향상 평가 문항 수를 입력해주세요.")
        return
    if not satisfaction_count or not satisfaction_count.isdigit() or int(satisfaction_count) < 0:
        messagebox.showerror("오류", "유효한 만족도 조사 문항 수를 입력해주세요.")
        return
    
    만족도조사.mj(link, int(repeat), int(evaluation_count), int(satisfaction_count))
    messagebox.showinfo("실행 완료", "만족도 조사 작업이 완료되었습니다.")

btn_run_survey = tk.Button(frame3, text="실행", command=run_survey, width=15, height=2)
btn_run_survey.grid(row=5, column=0, columnspan=2, pady=8)
             

# 기능 4: 사전역량조사
def sajeon_excel():
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
    if filepath:
        if messagebox.askyesno("확인", "선택한 엑셀 파일을 사용하여 사전역량조사를 진행하시겠습니까?"):
            저장_경로 = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile="사전역량조사_결과.xlsx"
            )
            try:
                사전역량조사.동작(filepath, 저장_경로)  # 동작 함수에 filepath 전달
                messagebox.showinfo("완료", "사전역량조사가 완료되었습니다!")
            except Exception as e:
                messagebox.showerror("오류", f"사전역량조사 중 오류가 발생했습니다:\n{str(e)}")

btn_sajeon_download = tk.Button(frame4, text="사전역량조사 양식 다운받기", width=30, height=2, command=사전역량조사.download_template_sajeon)
btn_sajeon_upload = tk.Button(frame4, text="사전역량조사 자동화 실행", width=30, height=2, command=sajeon_excel)
btn_sajeon_download.pack(pady=15)
btn_sajeon_upload.pack(pady=15)

root.mainloop()

