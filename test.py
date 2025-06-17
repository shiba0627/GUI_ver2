import tkinter as tk
import time
import pyautogui
from PIL import Image, ImageTk

class MyApp:
    def __init__(self, stay_time_required=1):
        self.root = tk.Tk()
        self.root.state('zoomed')#全画面表示

        self.stay_time_required = stay_time_required#滞留時間
        self.enter_time = None # マウスが領域に入った時間計測用
        self.clicked = False  # クリック済みのフラグ

        self.root.update_idletasks()#ウィンドウサイズ情報を更新
        self.screen_width = self.root.winfo_width()#ウィンドウの幅を取得
        self.screen_height = self.root.winfo_height()#ウィンドウの高さを取得

        area_width, area_height = (200,200)#ボタン１のサイズ
        x1 = self.screen_width  // 2#小数点以下切り捨ての除算, 左上X
        y1 = self.screen_height // 2#左上Y
        x2 = x1 + area_width#右下X
        y2 = y1 + area_height#右下Y
        self.target_area = (x1, y1, x2, y2)#ボタン1領域

        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height)#全画面キャンパス
        self.canvas.pack(fill="both", expand=True)#ウィンドウにキャンパスを追加
        self.rect_id = self.canvas.create_rectangle(*self.target_area, fill="lightblue")#ボタン1の領域を描画

        self.arc_id = None#円形バーのID
        self.arc_radius = 30#円形バーの半径

        self.check_cursor()#下で定義している関数

    def draw_circular_bar(self, x, y, percent):
        if self.arc_id:
            self.canvas.delete(self.arc_id)# 既存の円形バーを削除

        angle = percent * 3.6   #0-100%を360度に変換
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius,#円の外接矩形の左上
            x + self.arc_radius, y + self.arc_radius,#円の外接矩形の右下
            start=90, extent=-angle, style='pieslice',#開始角度90度、-angle度まで
            outline='red', fill = 'red'#色
        )

    def check_cursor(self):
        # マウスカーソルの位置を取得
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()
        x1, y1, x2, y2 = self.target_area#ボタン1の領域

        if x1 <= x <= x2 and y1 <= y <= y2:#マウスカーソルがボタン1の領域内にいるか
            if not self.clicked:#クリックフラグがFaulseのとき
                if self.enter_time is None:
                    self.enter_time = time.time()# マウスカーソルが始めて領域に入った時間を記録
                elapsed = time.time() - self.enter_time#滞在時間
                percent = min(elapsed / self.stay_time_required * 100, 100)#滞在時間をパーセントに変換
                self.draw_circular_bar(x + 40, y, percent)#円形バーを描画

                if elapsed >= self.stay_time_required:#一定時間を超えたら
                    print("クリック！")
                    #pyautogui.click()#クリック判定
                    self.canvas.itemconfig(self.rect_id, fill="red")#判定領域の色を赤に
                    self.clicked = True  # クリックフラグをTrueに
                    if self.arc_id:
                        self.canvas.delete(self.arc_id)# 円形バーを削除
                        self.arc_id = None
        else:
            self.enter_time = None# 領域外に出たら時間をリセット
            self.clicked = False  #  領域外に出たら再クリック許可
            self.canvas.itemconfig(self.rect_id, fill="lightblue")# 領域の色を元に戻す
            if self.arc_id:
                self.canvas.delete(self.arc_id)# 円形バーを削除
                self.arc_id = None

        self.root.after(50, self.check_cursor)# 50msごとにcheck_cursorを呼び出す

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MyApp()
    app.run()

