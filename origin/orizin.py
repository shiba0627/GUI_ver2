import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

class MyApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("GUI_for_gaze input")
        self.geometry('1275x765')
        self.configure(bg='white')

        # シンボル画像を読み込み
        self.img_start = ImageTk.PhotoImage(Image.open('start.png').resize((200, 200)))
        self.img_finish = ImageTk.PhotoImage(Image.open('finish_letter.png').resize((150, 100)))
        self.img_helper = ImageTk.PhotoImage(Image.open('helper.png').resize((200, 100)))
        self.img_user = ImageTk.PhotoImage(Image.open("user.png").resize((200, 100)))
        self.img_forward = ImageTk.PhotoImage(Image.open('forward_joy.png').resize((130, 105)))
        self.img_back = ImageTk.PhotoImage(Image.open('back_joy.png').resize((130, 105)))
        self.img_stop = ImageTk.PhotoImage(Image.open('stop_joy.png').resize((202, 102)))

        self.create_menu_frame()

    def create_menu_frame(self):
        """メニュー画面のフレームを作成する"""
        self.menu_frame = ttk.Frame(self, style='TFrame')
        self.menu_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure('TFrame', background='white')

        # 走行開始ボタン
        btn_start = ttk.Button(self.menu_frame, image=self.img_start, command=self.start_running)
        btn_start.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        # 終了ボタン
        btn_finish = ttk.Button(self.menu_frame, image=self.img_finish, command=self.Finish)
        btn_finish.place(relx=0.9, rely=0.9, anchor=tk.CENTER)
        
        # 介助者操縦モードボタン
        btn_helper = ttk.Button(self.menu_frame, image=self.img_helper, command=self.helper)
        btn_helper.place(relx=0.2, rely=0.9, anchor=tk.CENTER)

        self.menu_frame.tkraise()
    
    def create_control_frame(self, mode):
        """操縦画面のフレームを作成する"""
        control_frame = ttk.Frame(self, style='TFrame')
        control_frame.grid(row=0, column=0, sticky="nsew")
        
        # 停止ボタン
        btn_stop = ttk.Button(control_frame, image=self.img_stop, command=self.stop)
        btn_stop.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 前進ボタン
        btn_forward = ttk.Button(control_frame, image=self.img_forward, command=self.forward)
        btn_forward.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        # 後退ボタン
        btn_back = ttk.Button(control_frame, image=self.img_back, command=self.back)
        btn_back.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        # メニューに戻るボタン
        btn_menu = ttk.Button(control_frame, text="メニュー", command=self.menu)
        btn_menu.place(relx=0.1, rely=0.9, anchor=tk.CENTER)

        if mode == "helper":
            # ユーザ操縦モードボタン
            btn_user = ttk.Button(control_frame, image=self.img_user, command=self.user)
            btn_user.place(relx=0.9, rely=0.1, anchor=tk.CENTER)

        control_frame.tkraise()

    # --- 操縦コマンドと画面遷移のロジックを模倣 ---
    def start_running(self):
        print("走行開始")
        self.create_control_frame("user")

    def forward(self):
        print("前進")

    def back(self):
        print("後退")

    def stop(self):
        print("停止")
        self.create_menu_frame()

    def helper(self):
        print("介助者操縦モード")
        self.create_control_frame("helper")

    def user(self):
        print("ユーザ操縦モード")
        self.create_control_frame("user")

    def menu(self):
        print("メニューに戻る")
        self.create_menu_frame()
    
    def Finish(self):
        print("終了")
        self.destroy()

if __name__ == "__main__":
    root = MyApp()
    root.mainloop()