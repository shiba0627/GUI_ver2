import tkinter as tk
from PIL import Image, ImageTk
import time
import pyautogui

class HoverButton:
    def __init__(self, canvas, img_path, img_dark_path, area, stay_time=1):
        self.canvas = canvas
        size = 400
        self.img = ImageTk.PhotoImage(Image.open(img_path).resize((size, size)))
        self.img_dark = ImageTk.PhotoImage(Image.open(img_dark_path).resize((size, size)))
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
                    print("Button clicked!")
                    pyautogui.click()
                    self.canvas.itemconfig(self.image_id, image=self.img_dark)
                    self.clicked = True
                    if self.arc_id:
                        self.canvas.delete(self.arc_id)
                        self.arc_id = None
        else:
            self.reset()

class GUIApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.update_idletasks()
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)

        size = 500
        self.buttons = [
            HoverButton(self.canvas, "./img/forward_3d.png", "./img/forward_3d_dark.png",
                        self._calc_area(self.width/2, self.height/4, size)),
            HoverButton(self.canvas, "./img/ccw_3d.png", "./img/ccw_3d_dark.png",
                        self._calc_area(self.width*1/4, self.height*2/5, size)),
            HoverButton(self.canvas, "./img/stop_3d.png", "./img/stop_3d_dark.png",
                        self._calc_area(self.width/2, self.height*2/3, size)),
            HoverButton(self.canvas, "./img/cw_3d.png", "./img/cw_3d_dark.png",
                        self._calc_area(self.width*3/4, self.height*2/5, size)),
        ]

        self.check_cursor()

    def _calc_area(self, center_x, center_y, size):
        half = size / 2
        return (center_x - half, center_y - half, center_x + half, center_y + half)

    def check_cursor(self):
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()
        for btn in self.buttons:
            btn.update(x, y)
        self.root.after(20, self.check_cursor)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GUIApp()
    app.run()
