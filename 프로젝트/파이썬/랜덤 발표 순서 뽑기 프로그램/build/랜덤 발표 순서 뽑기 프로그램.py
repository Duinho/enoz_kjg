import os
import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import random
from PIL import Image, ImageTk
import sys

if getattr(sys, 'frozen', False):
    # 실행 파일 모드일 경우
    application_path = os.path.dirname(sys.executable)
else:
    # 개발 모드일 경우
    application_path = os.path.dirname(os.path.abspath(__file__))


# 전역 변수로 폰트와 글자 크기 설정
FONT_NAME = "Pretendard black"
FONT_SIZE_LARGE = 50
FONT_SIZE_XLARGE = 60
FONT_STYLE_BOLD = "bold"

bg_color = "#99D9EA" # 기본색상
fg_color = "#FFFFFF"

names = []

def read_colors_from_file():   # 디자인 폴더에 colors.txt 파일을 열어 색상 값을 가져오는 코드
    global bg_color, fg_color, FONT_NAME, FONT_SIZE_LARGE, FONT_SIZE_XLARGE, FONT_STYLE_BOLD
    try:
        #application_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(application_path, "디자인", "colors.txt")
        with open(file_path, "r") as file:
            lines = file.readlines()
            bg_color = lines[0].strip()
            fg_color = lines[1].strip()
    except FileNotFoundError:
        print("colors.txt 파일을 찾을 수 없습니다. 기본 색상으로 설정됩니다.")
    except Exception as e:
        print("파일 읽기 오류:", e)    

def random_order():  # 발표 순서를 랜덤으로 정하는 함수
    global names
    if not names:
        tk.messagebox.showinfo("오류", "엑셀 파일에서 팀을 불러오지 않았습니다.")
        return
    
    random.shuffle(names)
    team_order_window = TeamOrderWindow(names)
    team_order_window.mainloop()

def create_solid_color_image(color, width, height):
    image = Image.new("RGB", (width, height), color)
    return image

read_colors_from_file()

def load_excel_file():
    global names
    file_path = filedialog.askopenfilename(filetypes=[('Excel Files', '*.xlsx')])
    if file_path:
        df = pd.read_excel(file_path)
        names = df.iloc[:, 0].dropna().tolist()

current_directory = os.path.dirname(os.path.abspath(__file__))
bg_image = os.path.join(application_path, "디자인", "image.png")

root = tk.Tk()
root.title("발표 순서 정하기 프로그램")
root.state('zoomed')  # 메인 윈도우를 최대화 상태로 시작

bg_img = Image.open(bg_image)
bg_photo = ImageTk.PhotoImage(bg_img)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

frame = tk.Frame(root, width=450, height=330, bg=bg_color)
frame.place(x=720, y=430)

solid_color_image = create_solid_color_image(bg_color, 450, 330)
photo = ImageTk.PhotoImage(solid_color_image)
frame_label = tk.Label(frame, image=photo, bg=bg_color)
frame_label.place(x=0, y=0, relwidth=1, relheight=1)

button_load_file = tk.Button(frame, text="엑셀 파일 열기", command=load_excel_file,
                             font=(FONT_NAME, FONT_SIZE_LARGE, FONT_STYLE_BOLD),
                             bg=bg_color, fg=fg_color)
button_load_file.grid(row=1, column=0, columnspan=3, pady=25, sticky='ew')

button_random_order = tk.Button(frame, text="발표 순서 보기", command=random_order,
                                font=(FONT_NAME, FONT_SIZE_LARGE, FONT_STYLE_BOLD),
                                bg=bg_color, fg=fg_color)
button_random_order.grid(row=3, column=0, columnspan=3, pady=25, sticky='ew')


class TeamOrderWindow(tk.Toplevel):
    global bg_color, fg_color, FONT_NAME, FONT_SIZE_LARGE, FONT_SIZE_XLARGE, FONT_STYLE_BOLD
    def __init__(self, teams):
        super().__init__()
        self.title("랜덤 발표 순서")
        self.state('zoomed')  # 새로운 창을 최대화 상태로 시작
        self.config(bg=bg_color)

        self.teams = teams

        self.team_label_a = tk.Label(self, text="", font=(FONT_NAME, FONT_SIZE_XLARGE),
                                     bg=bg_color, fg=fg_color, justify='left')
        self.team_label_a.place(x=100, y=30)

        self.team_label_b = tk.Label(self, text="", font=(FONT_NAME, FONT_SIZE_XLARGE),
                                     bg=bg_color, fg=fg_color, justify='left')
        self.team_label_b.place(x=1000, y=30)

        self.show_team_order()

    def show_team_order(self):
        team_order_str_a = ""
        team_order_str_b = ""
        for i, team in enumerate(self.teams):
            team_str = f"{i+1:02d}. {team}\n"
            if i % 2 == 0:
                team_order_str_a += team_str
            else:
                team_order_str_b += team_str

        self.team_label_a.config(text=team_order_str_a)
        self.team_label_b.config(text=team_order_str_b)

root.mainloop()
