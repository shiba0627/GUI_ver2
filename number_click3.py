'''
アークがボタンの上には表示さえれないことが問題点
'''
import tkinter as tk
import time

class NumberGridApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Number Click Game')
        self.state('zoomed')

        self.update_idletasks()  # 画面サイズを正しく取得するため
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.next_number = 1
        self.hover_start_times = {}
        self.hover_duration = 1000  # ms

        # アーク描画用キャンバス（先に作っておくが最後に配置）
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.arc_id = None
        self.arc_radius = 30

        # 数字配置
        self.numbers = [
            [1, 3, 5],
            [2, 7, 6],
            [9, 4, 8]
        ]

        # ボタンサイズと中央整列用オフセット
        button_size = 250
        grid_width = 3 * button_size
        grid_height = 3 * button_size
        offset_x = (screen_width - grid_width) // 2
        offset_y = (screen_height - grid_height) // 2

        self.buttons = []
        for i in range(3):
            for j in range(3):
                num = self.numbers[i][j]
                btn = tk.Button(self, text=str(num), font=("Arial", 100), width=5, height=2, relief=tk.SOLID)
                btn.place(x=offset_x + j*button_size, y=offset_y + i*button_size, width=button_size, height=button_size)
                btn.config(command=lambda n=num, b=btn: self.on_button_click(n, b))
                btn.bind("<Enter>", lambda e, b=btn, n=num: self.on_hover_enter(b, n))
                btn.bind("<Leave>", lambda e, b=btn: self.on_hover_leave(b))
                self.buttons.append(btn)

        # 最後にCanvasを配置（最背面）
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.canvas.lower(self)  # canvasを一番下に配置

        self.check_hover()

    def on_hover_enter(self, button, number):
        self.hover_start_times[button] = (time.time(), number)

    def on_hover_leave(self, button):
        if button in self.hover_start_times:
            del self.hover_start_times[button]
        self.clear_arc()

    def check_hover(self):
        now = time.time()
        for button, (start_time, number) in list(self.hover_start_times.items()):
            elapsed = now - start_time
            percent = min(100, (elapsed / (self.hover_duration / 1000)) * 100)

            x = self.winfo_pointerx() - self.winfo_rootx()
            y = self.winfo_pointery() - self.winfo_rooty()

            self.draw_arc(x + 40, y, percent)

            if elapsed >= self.hover_duration / 1000:
                self.on_button_click(number, button)
                del self.hover_start_times[button]
                self.clear_arc()
        self.after(50, self.check_hover)

    def draw_arc(self, x, y, percent):
        self.clear_arc()
        angle = percent * 3.6
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius,
            x + self.arc_radius, y + self.arc_radius,
            start=90, extent=-angle, style="pieslice",
            fill="black", outline="black"
        )

    def clear_arc(self):
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None

    def on_button_click(self, number, button):
        if not button.winfo_exists():
            return
        if self.next_number == number:
            button.config(text="")
            self.next_number += 1
        if self.next_number > 9:
            self.show_clear_message()

    def show_clear_message(self):
        label = tk.Label(self, text="クリア！", font=("Comic Sans MS", 100), fg="green")
        label.place(x=200, y=100)
        for btn in self.buttons:
            btn.destroy()
        self.clear_arc()
        exit_button = tk.Button(self, text="終了", font=("Comic Sans Ms", 50), command=self.quit)
        exit_button.place(x=1000, y=620)

if __name__ == "__main__":
    app = NumberGridApp()
    app.mainloop()
