import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from PIL import Image, ImageTk
import random
import sys
import time

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

FONT_NAME = "Pretendard black"
FONT_SIZE_LARGE = 50
FONT_SIZE_XLARGE = 60
FONT_STYLE_BOLD = "bold"
bg_color = "#99D9EA"
fg_color = "#FFFFFF"

names = []
current_team_index = 0
team_order_window = None
roulette_duration = 5  # 룰렛 애니메이션 지속 시간 (초)

def read_colors_from_file():
    global bg_color, fg_color
    try:
        file_path = os.path.join(application_path, "디자인", "colors.txt")
        with open(file_path, "r") as file:
            lines = file.readlines()
            bg_color = lines[0].strip()
            fg_color = lines[1].strip()
    except FileNotFoundError:
        print("colors.txt 파일을 찾을 수 없습니다. 기본 색상으로 설정됩니다.")
    except Exception as e:
        print("파일 읽기 오류:", e)

def load_excel_file():
    global names, current_team_index
    current_team_index = 0
    file_path = filedialog.askopenfilename(filetypes=[('Excel Files', '*.xlsx')])
    if file_path:
        df = pd.read_excel(file_path)
        names = df.iloc[:, 0].dropna().tolist()
        random.shuffle(names)

read_colors_from_file()

root = tk.Tk()
root.title("발표 순서 정하기 프로그램")
root.state('zoomed')

bg_image = os.path.join(application_path, "디자인", "image.png")
bg_img = Image.open(bg_image)
bg_photo = ImageTk.PhotoImage(bg_img)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

frame = tk.Frame(root, width=450, height=330, bg=bg_color)
frame.place(x=720, y=430)

def create_solid_color_image(color, width, height):
    image = Image.new("RGB", (width, height), color)
    return image

solid_color_image = create_solid_color_image(bg_color, 450, 330)
photo = ImageTk.PhotoImage(solid_color_image)
frame_label = tk.Label(frame, image=photo, bg=bg_color)
frame_label.place(x=0, y=0, relwidth=1, relheight=1)

button_load_file = tk.Button(frame, text="엑셀 파일 열기", command=load_excel_file,
                             font=(FONT_NAME, FONT_SIZE_LARGE, FONT_STYLE_BOLD),
                             bg=bg_color, fg=fg_color)
button_load_file.grid(row=1, column=0, columnspan=3, pady=25, sticky='ew')

def set_next_team_order():
    global team_order_window
    if not names:
        tk.messagebox.showinfo("오류", "엑셀 파일에서 팀을 불러오지 않았습니다.")
        return

    if team_order_window:
        team_order_window.destroy()
    team_order_window = TeamOrderWindow()

button_show_order = tk.Button(frame, text="발표 순서 보기", command=set_next_team_order,
                              font=(FONT_NAME, FONT_SIZE_LARGE, FONT_STYLE_BOLD),
                              bg=bg_color, fg=fg_color)
button_show_order.grid(row=3, column=0, columnspan=3, pady=25, sticky='ew')

class TeamOrderWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("다음 발표자 보기")
        self.state('zoomed')
        self.config(bg=bg_color)

        self.teams = [""] * len(names)
        self.is_roulette_running = False

        self.roulette_label = tk.Label(self, text="", font=(FONT_NAME, FONT_SIZE_XLARGE),
                                       bg=bg_color, fg=fg_color)
        self.roulette_label.place(relx=0.5, rely=0.1, anchor='center')

        self.button_next_team = tk.Button(self, text="다음 발표자 설정", command=self.start_roulette_animation,
                                          font=(FONT_NAME, FONT_SIZE_LARGE, FONT_STYLE_BOLD),
                                          bg=bg_color, fg=fg_color)
        self.button_next_team.place(relx=0.5, rely=0.225, anchor='center')

        self.team_number_label_a = tk.Label(self, text="", font=(FONT_NAME, FONT_SIZE_XLARGE),
                                            bg=bg_color, fg=fg_color, justify='left')
        self.team_number_label_a.place(relx=0.075, rely=0.325, anchor='n')

        self.team_number_label_b = tk.Label(self, text="", font=(FONT_NAME, FONT_SIZE_XLARGE),
                                            bg=bg_color, fg=fg_color, justify='left')
        self.team_number_label_b.place(relx=0.575, rely=0.325, anchor='n')

        self.team_name_label_a = tk.Label(self, text="", font=(FONT_NAME, FONT_SIZE_XLARGE),
                                          bg=bg_color, fg=fg_color, justify='left', anchor='w')
        self.team_name_label_a.place(relx=0.115, rely=0.325, anchor='nw')

        self.team_name_label_b = tk.Label(self, text="", font=(FONT_NAME, FONT_SIZE_XLARGE),
                                          bg=bg_color, fg=fg_color, justify='left', anchor='w')
        self.team_name_label_b.place(relx=0.615, rely=0.325, anchor='nw')

        self.update_team_order()

    def start_roulette_animation(self):
        if not self.is_roulette_running:
            self.is_roulette_running = True
            self.button_next_team.config(state='disabled')
            start_time = time.time()
            self.update_roulette(start_time, roulette_duration, start_time)

    def update_roulette(self, start_time, duration, initial_time):
        elapsed = time.time() - start_time
        if elapsed < duration:
            available_teams = [team for team in names if team not in self.teams]
            next_team_index = random.randint(0, len(available_teams) - 1)
            self.roulette_label.config(text=available_teams[next_team_index])
            # 처음에는 느리게 시작하고 점차 빨라지도록 딜레이 설정
            delay = int(min(300, 50 + (1000 * (elapsed / duration))))
            self.after(delay, self.update_roulette, initial_time, duration, initial_time)
        else:
            self.finalize_team_selection()
            self.is_roulette_running = False
            if "" in self.teams:
                self.button_next_team.config(state='normal')




    def finalize_team_selection(self):
        selected_team = self.roulette_label.cget("text")
        if selected_team not in self.teams:
            self.teams[self.teams.index("")] = selected_team
            self.update_team_order()

        # 마지막 팀 자동 선택
        if self.teams.count("") == 1:
            last_team = [team for team in names if team not in self.teams][0]
            self.teams[self.teams.index("")] = last_team
            self.update_team_order()
            self.button_next_team.config(state='disabled')

    def update_team_order(self):
        team_number_str_a = ""
        team_name_str_a = ""
        team_number_str_b = ""
        team_name_str_b = ""
        for i in range(0, len(self.teams), 2):
            team_number_str_a += f"{i+1:02d}.\n"
            team_name_str_a += f"{self.teams[i]}\n"
            if i + 1 < len(self.teams):
                team_number_str_b += f"{i+2:02d}.\n"
                team_name_str_b += f"{self.teams[i+1]}\n"

        self.team_number_label_a.config(text=team_number_str_a)
        self.team_name_label_a.config(text=team_name_str_a)
        self.team_number_label_b.config(text=team_number_str_b)
        self.team_name_label_b.config(text=team_name_str_b)

root.mainloop()
