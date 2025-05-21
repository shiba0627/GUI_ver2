import tkinter as tk
import time
from datetime import datetime

class NumberGridApp(tk.Tk):
    def __init__(self):
        super().__init__()  # tkinter.Tkの初期化
        self.title('Number Click Game')
        self.state('zoomed')  # 全画面表示

        self.next_number = 1
        self.hover_start_times = {}  # ボタンIDと滞留開始時刻を記録
        self.hover_duration = 1000  # ms 単位（= 1秒）

        # パターンの選択
        self.ptn = 1
        if self.ptn == 1:
            self.numbers = [
                [1, 3, 5],
                [2, 7, 6],
                [9, 4, 8]
            ]
        elif self.ptn == 2:
            self.numbers = [
                [4, 9, 1],
                [5, 2, 3],
                [8, 6, 7]
            ]
        elif self.ptn == 3:
            self.numbers = [
                [4, 8, 5],
                [1, 6, 3],
                [9, 2, 7]
            ]
        
        self.buttons = []
        for i in range(3):
            for j in range(3):
                number = self.numbers[i][j]
                button = tk.Button(self, text=str(number), font=("Arial", 100), width=5, height=2, relief=tk.SOLID)
                button.place(x=250 + j*250, y=i*250, width=250, height=250)
                button.config(command=lambda num=number, b=button: self.on_button_click(num, b))

                # マウスイベント追加
                button.bind("<Enter>", lambda e, b=button, n=number: self.on_hover_enter(b, n))
                button.bind("<Leave>", lambda e, b=button: self.on_hover_leave(b))

                self.buttons.append(button)

        # 定期的に滞留チェック
        self.check_hover()

    def on_hover_enter(self, button, number):
        # 現在の時刻を記録
        self.hover_start_times[button] = (time.time(), number)

    def on_hover_leave(self, button):
        # 滞留記録を削除
        if button in self.hover_start_times:
            del self.hover_start_times[button]

    def check_hover(self):
        current_time = time.time()
        for button, (start_time, number) in list(self.hover_start_times.items()):
            if current_time - start_time >= self.hover_duration / 1000:
                self.on_button_click(number, button)
                del self.hover_start_times[button]  # 一度だけ処理
        self.after(100, self.check_hover)

    def on_button_click(self, number, button):
        if not button.winfo_exists():
            return
        if self.next_number == number:
            button.config(text='')
            self.next_number += 1
        if self.next_number > 9:
            self.show_clear_message()
        
    def show_clear_message(self):
        label = tk.Label(self, text=f"クリア！", font=("Comic Sans MS", 100), fg="green")
        label.place(x=200, y=100)
        for btn in self.buttons:
            btn.destroy()
        exit_button = tk.Button(self, text="終了", font=("Comic Sans Ms", 50), command=self.quit, relief=tk.SOLID)
        exit_button.place(x=1000, y=620)

if __name__ == "__main__":
    app = NumberGridApp()
    app.mainloop()
