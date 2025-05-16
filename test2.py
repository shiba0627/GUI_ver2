# cd C:\Users\tonegawa\program\mygui
import tkinter as tk
from PIL import Image, ImageTk
import time
import pyautogui
class MyApp:
    def __init__(self, stay_time_required=1):
        self.root = tk.Tk()
        self.root.state('zoomed')
        self.stay_time_required = stay_time_required#滞留時間
        self.enter_time = None # マウスが領域に入った時間計測用
        self.clicked = False  # クリック済みのフラグ
        self.arc_id = None#円形バーのID
        self.arc_radius = 30#円形バーの半径

        #ウィンドウサイズを取得
        self.root.update_idletasks()#ウィンドウサイズ情報を更新
        self.screen_width = self.root.winfo_width()#幅
        self.screen_height = self.root.winfo_height()#高さ
        print(self.screen_width, self.screen_height)
        #canvasの作成
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height)
        self.canvas.pack(fill="both", expand=True)
        
        size = 500#ボタンのサイズ
        #ボタン1
        one_width, one_height = (size, size)
        xone_1 = self.screen_width/2 - size/2
        yone_1 = self.screen_height/4 - size/2
        one_image_path = "./img/forward_3d.png"
        one_image = Image.open(one_image_path)
        one_image = one_image.resize((one_width, one_height))
        self.one_photo = ImageTk.PhotoImage(one_image)
        self.canvas.create_image(xone_1,yone_1,image = self.one_photo, anchor="nw")
        
        one_image_path_dark = './img/forward_3d_dark.png'
        one_image_dark = Image.open(one_image_path_dark)
        one_image_dark = one_image_dark.resize((one_width, one_height))
        self.one_photo_dark = ImageTk.PhotoImage(one_image_dark)
        #ボタン1の領域
        #xone_1 = 490
        #yone_1 = 100
        xone_2 = xone_1 + size
        yone_2 = yone_1 + size
        self.one_area = (xone_1, yone_1, xone_2, yone_2)

        #ボタン2
        two_width, two_height = (size, size)
        xtwo_1 = self.screen_width*1/4 - size/2
        ytwo_1 = self.screen_height*2/5 - size/2         
        two_image_path = "./img/ccw_3d.png"
        two_image = Image.open(two_image_path)
        two_image = two_image.resize((two_width, two_height))
        self.two_photo = ImageTk.PhotoImage(two_image)
        self.canvas.create_image(xtwo_1,ytwo_1,image = self.two_photo, anchor="nw")
        
        two_image_path_dark = './img/ccw_3d_dark.png'
        two_image_dark = Image.open(two_image_path_dark)
        two_image_dark = two_image_dark.resize((two_width, two_height))
        self.two_photo_dark = ImageTk.PhotoImage(two_image_dark)
        #ボタン2の領域
        xtwo_2 = xtwo_1 + size
        ytwo_2 = ytwo_1 + size
        self.two_area = (xtwo_1, ytwo_1, xtwo_2, ytwo_2)
        
        #ボタン3
        three_width, three_height = (size, size)
        xthree_1 = self.screen_width/2 - size/2
        ythree_1 = self.screen_height*2/3 - size/2
        three_image_path = "./img/stop_3d.png"
        three_image = Image.open(three_image_path)
        three_image = three_image.resize((three_width, three_height))
        self.three_photo = ImageTk.PhotoImage(three_image)
        self.canvas.create_image(xthree_1,ythree_1,image = self.three_photo, anchor="nw")
        
        three_image_path_dark = './img/stop_3d_dark.png'
        three_image_dark = Image.open(three_image_path_dark)
        three_image_dark = three_image_dark.resize((three_width, three_height))
        self.three_photo_dark = ImageTk.PhotoImage(three_image_dark)

        #ボタン3の領域
        xthree_2 = xthree_1 + size
        ythree_2 = ythree_1 + size
        self.three_area = (xthree_1, ythree_1, xthree_2, ythree_2)

        #ボタン4
        four_width, four_height = (size, size)
        xfour_1 = self.screen_width*3/4 - size/2
        yfour_1 = self.screen_height*2/5 - size/2
        four_image_path = "./img/cw_3d.png"
        four_image = Image.open(four_image_path)
        four_image = four_image.resize((four_width, four_height))
        self.four_photo = ImageTk.PhotoImage(four_image)
        self.canvas.create_image(xfour_1,yfour_1,image = self.four_photo, anchor="nw")
        
        four_image_path_dark = './img/cw_3d_dark.png'
        four_image_dark = Image.open(four_image_path_dark)
        four_image_dark = four_image_dark.resize((four_width, four_height))
        self.four_photo_dark = ImageTk.PhotoImage(four_image_dark)
        #ボタン4の領域
        xfour_2 = xfour_1 + size
        yfour_2 = yfour_1 + size
        self.four_area = (xfour_1, yfour_1, xfour_2, yfour_2)
        self.check_cursor()
        self.run()
    def draw_circular_bar(self, x, y, percent):
        if self.arc_id:
            self.canvas.delete(self.arc_id)# 既存の円形バーを削除
        angle = percent * 3.6
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius,#円の外接矩形の左上
            x + self.arc_radius, y + self.arc_radius,#円の外接矩形の右下
            start=90, extent=-angle, style='pieslice',#開始角度90度、-angle度まで
            outline='black', fill = 'black'#色
        )
    def check_cursor(self):
        # マウスカーソルの位置を取得
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()

        # ボタン1の領域
        b1_x1, b1_y1, b1_x2, b1_y2 = self.one_area

        if b1_x1 <= x <= b1_x2 and b1_y1 <= y <= b1_y2:
            if not self.clicked:#クリックフラグがFalseのとき
                if self.enter_time is None:
                    self.enter_time = time.time()
                elapsed = time.time() - self.enter_time
                percent = min(elapsed / self.stay_time_required * 100, 100)
                self.draw_circular_bar(x + 40, y, percent)

                if elapsed >= self.stay_time_required:
                    print("Button 1 clicked")
                    pyautogui.click()#クリック判定
                    self.canvas.create_image(b1_x1,b1_y1,image = self.one_photo_dark, anchor="nw")
                    self.clicked = True
                    if self.arc_id:
                        self.canvas.delete(self.arc_id)
                        self.arc_id = None
        else:
            self.enter_time = None
            self.clicked = False
            self.canvas.create_image(b1_x1,b1_y1,image = self.one_photo, anchor="nw")
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None
        # ボタン2の領域
        b2_x1, b2_y1, b2_x2, b2_y2 = self.two_area
        if  b2_x1<= x <= b2_x2 and b2_y1 <= y <= b2_y2:
            if not self.clicked:
                if self.enter_time is None:
                    self.enter_time = time.time()
                elapsed = time.time() - self.enter_time
                percent = min(elapsed / self.stay_time_required * 100, 100)
                self.draw_circular_bar(x + 40, y, percent)

                if elapsed >= self.stay_time_required:
                    print("Button 2 clicked")
                    pyautogui.click()
                    self.canvas.create_image(b2_x1,b2_y1,image = self.two_photo_dark, anchor="nw")
                    self.clicked = True
                    if self.arc_id:
                        self.canvas.delete(self.arc_id)
                        self.arc_id = None
        else:
            self.enter_time = None
            self.clicked = False
            self.canvas.create_image(b2_x1,b2_y1,image = self.two_photo, anchor="nw")
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None

        # ボタン3の領域
        b3_x1, b3_y1, b3_x2, b3_y2 = self.three_area

        if b3_x1 <= x <= b3_x2 and b3_y1 <= y <= b3_y2:
            if not self.clicked:
                if self.enter_time is None:
                    self.enter_time = time.time()
                elapsed = time.time() - self.enter_time
                percent = min(elapsed / self.stay_time_required * 100, 100)
                self.draw_circular_bar(x + 40, y, percent)

                if elapsed >= self.stay_time_required:
                    print("Button 3 clicked")
                    self.canvas.create_image(b3_x1,b3_y1,image = self.three_photo_dark, anchor="nw")
                    self.clicked = True
                    if self.arc_id:
                        self.canvas.delete(self.arc_id)
                        self.arc_id = None
        else:
            self.enter_time = None
            self.clicked = False
            self.canvas.create_image(b3_x1,b3_y1,image = self.three_photo, anchor="nw")
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None

        # ボタン4の領域
        b4_x1, b4_y1, b4_x2, b4_y2 = self.four_area
        if b4_x1 <= x <= b4_x2 and b4_y1 <= y <= b4_y2:
            if not self.clicked:
                if self.enter_time is None:
                    self.enter_time = time.time()
                elapsed = time.time() - self.enter_time
                percent = min(elapsed / self.stay_time_required * 100, 100)
                self.draw_circular_bar(x + 40, y, percent)

                if elapsed >= self.stay_time_required:
                    print("Button 4 clicked")
                    pyautogui.click()
                    self.canvas.create_image(b4_x1,b4_y1,image = self.four_photo_dark, anchor="nw")
                    self.clicked = True
                    if self.arc_id:
                        self.canvas.delete(self.arc_id)
                        self.arc_id = None
        else:
            self.enter_time = None
            self.clicked = False
            self.canvas.create_image(b4_x1,b4_y1,image = self.four_photo, anchor="nw")
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None   
        self.root.after(20, self.check_cursor)# 50msごとにcheck_cursorを呼び出す
    def  run(self):
        self.root.mainloop()
        
def main():
    app = MyApp()
    app.run()

if __name__ == "__main__":
    main()
