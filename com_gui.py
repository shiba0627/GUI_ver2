import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import tkinter as tk
from PIL import Image, ImageTk
import time
from config import CW, CW_ACTIVE, CW_ATTENTION, CW_LOCK
from config import CCW, CCW_ACTIVE, CCW_ATTENTION, CCW_LOCK
from config import FORWARD, FORWARD_ACTIVE, FORWARD_ATTENTION, FORWARD_LOCK
from config import BACK, BACK_ACTIVE, BACK_ATTENTION, BACK_LOCK
from config import STOP, STOP_ACTIVE, STOP_ATTENTION,STOP_LOCK
from config import BUTTON_SIZE, HOVER_TIME, ARC_RADIUS
from config import HOST, OBJECT_PORT

class BaseButton:
    def __init__(self, canvas, img_path, active_path, lock_path, attention_path, area, cmd):
        self.canvas = canvas
        width, height = int(area[2] - area[0]), int(area[3] - area[1])
        
        self.img = ImageTk.PhotoImage(Image.open(img_path).resize((width, height)))
        self.img_active = ImageTk.PhotoImage(Image.open(active_path).resize((width, height)))
        self.img_attention = ImageTk.PhotoImage(Image.open(attention_path).resize((width, height)))
        self.img_lock = ImageTk.PhotoImage(Image.open(lock_path).resize((width, height)))

        self.my_cmd    = cmd#自分は何ボタンか
        self.area       = area
        self.active = False#自分は押されているか
        self.locked = False#自分はロックされているか
        self.stay_time  = HOVER_TIME
        self.enter_time = None
        self.arc_id     = None
        self.arc_radius = ARC_RADIUS
        self.image_id = self.canvas.create_image(area[0], area[1], image=self.img, anchor="nw")
        self.image_to_show = self.img#表示する画像
        
        self.image_id = self.canvas.create_image(area[0], area[1], image=self.img, anchor="nw")

    def draw_arc(self, x, y, percent):
        if self.arc_id:
            self.canvas.delete(self.arc_id)
        angle = percent * 3.6
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius, 
            x + self.arc_radius, y + self.arc_radius,
            start=90, extent=-angle, style='pieslice',
            outline='white', fill='black'
        )

    def _handle_hover(self, cursor_x, cursor_y):
        if self.locked:#自分がロックされているなら、何もしない
            if self.arc_id: # もしアークが表示されていれば消す
                self.canvas.delete(self.arc_id)
                self.arc_id = None
            self.enter_time = None
            return None, None
        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:#カーソルが領域内部なら
            if self.enter_time is None:
                self.enter_time = time.time()
            elapsed = time.time() - self.enter_time
            percent = min(elapsed / self.stay_time * 100, 100)
            self.draw_arc(cursor_x + 40, cursor_y, percent)#アークを描画
            if elapsed >= self.stay_time:#一定時間滞留したら
                if self.arc_id:#アークがあるなら
                    self.canvas.delete(self.arc_id)#アークを消す
                    self.arc_id = None
                return self.my_cmd, self.my_cmd#滞留している, コマンド
            else:
                return self.my_cmd, None
        else:#カーソルが領域外部なら
            self.enter_time = None
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None
        return None, None#滞留していない, 何も選択されていないor選択に変更がないのでNoneを

class JoyButton(BaseButton):
    def update(self, cursor_x, cursor_y, active_button, attention_button):
        if self.locked:
            image_to_show = self.img_lock
        elif self.my_cmd == active_button:
            image_to_show = self.img_active
        elif self.my_cmd == attention_button:
            image_to_show = self.img_attention
        else:
            image_to_show = self.img#default画像

        self.canvas.itemconfig(self.image_id, image=image_to_show)
        return self._handle_hover(cursor_x, cursor_y)

class GUIApp:
    def __init__(self):

        self.str = [False] * 10 # 前回の障害物情報、初期値は周りに障害物なしとみなす
        self.str[1] = False # 前方に障害物あり
        self.str[3] = False # 右に障害物あり
        self.str[6] = True # 後ろに障害物あり
        self.str[9] = True # 左に障害物あり

        self.active_button = 's'
        self.attention_button = None

        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.update_idletasks()
        self.width, self.height = self.root.winfo_width(), self.root.winfo_height()
        self.canvas = tk.Canvas(self.root, bg="white", width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)

        button_list = [
            (FORWARD, FORWARD_ACTIVE, FORWARD_LOCK, FORWARD_ATTENTION, 2/4, 1/6, 'w'),
            (CCW    , CCW_ACTIVE    , CCW_LOCK    , CCW_ATTENTION    , 1/4, 3/6, 'a'),
            (CW     , CW_ACTIVE     , CW_LOCK     , CW_ATTENTION     , 3/4, 3/6, 'd'),
            (STOP   , STOP_ACTIVE   , STOP_LOCK   , STOP_ATTENTION   , 2/4, 3/6, 's'),
            (BACK   , BACK_ACTIVE   , BACK_LOCK   , BACK_ATTENTION   , 2/4, 5/6, 'z')
        ]

        self.buttons = []
        for img_path, active_path, lock_path, attention_path, center_x_ratio, center_y_ratio, cmd in button_list:
            center_x, center_y = center_x_ratio * self.width, center_y_ratio * self.height
            area = (center_x - BUTTON_SIZE/2, center_y - BUTTON_SIZE/2, center_x + BUTTON_SIZE/2, center_y + BUTTON_SIZE/2)
            self.buttons.append(JoyButton(self.canvas, img_path, active_path, lock_path, attention_path, area, cmd))

        self.check_cursor()
    def check_cursor(self):
        
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()

        #まず、障害物情報をチェックする
        for button in self.buttons:
            button.locked = False
        if self.str[1]:
            for button in self.buttons:
                if button.my_cmd == 'w':
                    button.locked = True
                    break
        if self.str[3]:
            for button in self.buttons:
                if button.my_cmd == 'd':
                    button.locked = True
                    break
        if self.str[6]:
            for button in self.buttons:
                if button.my_cmd == 'z':
                    button.locked = True
                    break
        if self.str[9]:
            for button in self.buttons:
                if button.my_cmd == 'a':
                    button.locked = True
                    break

        #ボタン状態の更新
        new_attention = None
        new_active = None
        for button in self.buttons:
            attention, active = button.update(x, y, self.active_button, self.attention_button)
            if attention:
                new_attention = attention
            if active:
                new_active = active

        self.attention_button = new_attention

        #if new_active:
            #self.active_button = new_active

        if new_active and new_active != self.active_button:
            self.active_button = new_active
            print(f'active_button updated: {self.active_button}')

        self.root.after(20, self.check_cursor)
    def run(self):
        self.root.mainloop()
if __name__ == '__main__':
    app = GUIApp()
    app.run()
