#メニュー画面を追記
import tkinter as tk
from PIL import Image, ImageTk
import time
import pyautogui

# ====================
# ボタン生成クラス
# ====================
class makeButton:
    def __init__(self, canvas, img_path, img_dark_path, area, stay_time,com):
        self.com = com
        self.canvas = canvas
        width = int(area[2] - area[0])
        height = int(area[3] - area[1])
        self.img = ImageTk.PhotoImage(Image.open(img_path).resize((width, height)))
        self.img_dark = ImageTk.PhotoImage(Image.open(img_dark_path).resize((width, height)))
        self.area = area
        self.stay_time = stay_time
        self.enter_time = None
        self.clicked = False
        self.arc_id = None
        self.arc_radius = 30
        self.image_id = self.canvas.create_image(area[0], area[1], image=self.img, anchor="nw")

    def reset(self):
        self.enter_time = None
        self.clicked = False
        self.canvas.itemconfig(self.image_id, image=self.img)
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None

    def draw_arc(self, x, y, percent):
        if self.arc_id:
            self.canvas.delete(self.arc_id)
        angle = percent * 3.6
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius,
            x + self.arc_radius, y + self.arc_radius,
            start=90, extent=-angle, style='pieslice',
            outline='black', fill='black'
        )

    def update(self, cursor_x, cursor_y):
        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:
            if not self.clicked:
                if self.enter_time is None:
                    self.enter_time = time.time()
                elapsed = time.time() - self.enter_time
                percent = min(elapsed / self.stay_time * 100, 100)
                self.draw_arc(cursor_x + 40, cursor_y, percent)
                if elapsed >= self.stay_time:
                    print(f"{self.com} clicked!")
                    #pyautogui.click()#使ってないけどクリック判定
                    self.canvas.itemconfig(self.image_id, image=self.img_dark)
                    self.clicked = True
                    if self.arc_id:
                        self.canvas.delete(self.arc_id)
                        self.arc_id = None
        else:
            self.reset()


# ====================
# アプリ本体
# ====================
class GUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("視線入力GUI")
        self.state("zoomed")

        self.frames = {}

        # メニュー画面と操作画面を生成
        for F in (MenuScreen, ControlScreen):
            frame = F(self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(MenuScreen)

    def show_frame(self, screen):
        frame = self.frames[screen]
        frame.tkraise()


# ====================
# メニュー画面
# ====================
class MenuScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="lightblue")
        tk.Label(self, text="メニュー画面", font=("Arial", 30), bg="lightblue").pack(pady=100)
        tk.Button(self, text="操作画面へ", font=("Arial", 20),
                    command=lambda: master.show_frame(ControlScreen)).pack(pady=20)

# 操作画面（元の視線入力GUI）
class ControlScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.after(100, self.setup_buttons)

        tk.Button(self, text="メニューへ戻る", font=("Arial", 15),
                    command=lambda: master.show_frame(MenuScreen)).place(x=20, y=20)

    def setup_buttons(self):
        width = self.winfo_width()
        height = self.winfo_height()
        size = 450
        time1 = 1
        self.buttons = [
            makeButton(self.canvas, "./img/forward_3d.png", "./img/forward_3d_dark.png",
                        self._calc_area(width / 2, height / 4, size), time1,'w'),
            makeButton(self.canvas, "./img/ccw_3d.png", "./img/ccw_3d_dark.png",
                        self._calc_area(width * 1 / 4, height * 2 / 5, size), time1,'a'),
            makeButton(self.canvas, "./img/stop_3d.png", "./img/stop_3d_dark.png",
                        self._calc_area(width / 2, height * 2 / 3, size), time1,'s'),
            makeButton(self.canvas, "./img/cw_3d.png", "./img/cw_3d_dark.png",
                        self._calc_area(width * 3 / 4, height * 2 / 5, size), time1,'d'),
        ]

        self.check_cursor()

    def _calc_area(self, center_x, center_y, size):
        half = size / 2
        return (center_x - half, center_y - half, center_x + half, center_y + half)

    def check_cursor(self):
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
        for btn in self.buttons:
            btn.update(x, y)
        self.after(15, self.check_cursor)


# ====================
# 実行
# ====================
if __name__ == "__main__":
    app = GUIApp()
    app.mainloop()
