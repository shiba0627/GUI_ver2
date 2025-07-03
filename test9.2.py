#ソケット通信の機能を追加
import tkinter as tk
from PIL import Image, ImageTk
import time
from config import CCW, CCW_LOCK, CCW_DARK, CCW_ATTENTION, CCW_ACTIVE
from config import CW, CW_DARK, CW_LOCK, CW_ATTENTION, CW_ACTIVE
from config import FORWARD, FORWARD_DARK, FORWARD_LOCK, FORWARD_ATTENTION, FORWARD_ACTIVE
from config import STOP, STOP_DARK,STOP_LOCK, STOP_ATTENTION, STOP_ACTIVE
from config import BACK, BACK_DARK, BACK_LOCK, BACK_ATTENTION, BACK_ACTIVE
from config import BUTTON_SIZE, HOVER_TIME, ARC_RADIUS
from config import SERVER_HOST, SERVER_PORT
import client_templete as client

class makeButton:
    def __init__(self, canvas, img_path, dark_path, lock_path, attention_path, area, cmd, client_instance):
        self.canvas = canvas
        self.client = client_instance

        #self.root = tk.Tk()
        #self.canvas = tk.Canvas(self.root, width=500, height=500)
        
        width = int(area[2] - area[0])
        height = int(area[3]-area[1])
        self.img           = ImageTk.PhotoImage(Image.open(img_path).resize((width, height)))
        self.img_dark      = ImageTk.PhotoImage(Image.open(dark_path).resize((width, height)))
        self.img_lock      = ImageTk.PhotoImage(Image.open(lock_path).resize((width, height)))
        self.img_attention = ImageTk.PhotoImage(Image.open(attention_path).resize((width, height)))
        
        self.area = area
        self.stay_time  = HOVER_TIME#滞留時間
        self.enter_time = None#領域内にカーソルが入った時刻
        self.clicked    = False#クリック状態か
        self.locked     = False#ロック状態か
        self.arc_id     = None#アークのキャンパスID
        self.arc_radius = ARC_RADIUS#半径
        self.cmd        = cmd#コマンド(半角一文字)

        self.image_id = self.canvas.create_image(area[0], area[1], image = self.img, anchor="nw")#描画
    
    def reset(self):
        #ボタンを初期状態にする
        self.enter_time = None
        self.clicked    = False#ボタンがクリックされているか
        self.locked     = False
        self.canvas.itemconfig(self.image_id, image=self.img)
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None
    
    def set_dark_state(self):
        #ボタンをclickedにする
        self.enter_time = None
        self.clicked = True
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None
        self.canvas.itemconfig(self.image_id, image=self.img_dark)
        
    def draw_arc(self, x, y, percent):
        if self.arc_id:
            self.canvas.delete(self.arc_id)
        angle = percent * 3.6
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius,
            x + self.arc_radius, y + self.arc_radius,
            start = 90, extent=-angle, style = 'pieslice',
            outline = 'black', fill = 'black'
        )

    def update(self, cursor_x, cursor_y):
        '''カーソル位置を取得、ボタンを更新
            クリックされたらコマンドを, それ以外はNoneをreturn'''
        if self.clicked:#clicked状態なら、なにもしない
            return None
        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:
            #if not self.clicked:#クリック状態でないなら(滞留中なら)
            if self.enter_time is None:
                self.enter_time = time.time()
            elapsed = time.time() - self.enter_time#滞留時間
            percent = min(elapsed / self.stay_time * 100, 100)
            self.draw_arc(cursor_x + 40, cursor_y, percent)
            #self.canvas.itemconfig(self.image_id, image = self.img_attention)
            if elapsed >= self.stay_time:#滞留時間が一定以上なら、clicked
                #print(f'{self.cmd}')
                self.client.send_message(self.cmd)
                self.set_dark_state()
                return self.cmd
            else:#滞留中かつ、滞留時間が一定以上でないなら
                self.canvas.itemconfig(self.image_id, image = self.img_attention)
        else:#カーソルが領域外なら
            self.reset()
        return None
            


class GUIApp():
    def __init__(self):
        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.update_idletasks()#ウィンドウ準備完了を待つ
        self.width  = self.root.winfo_width()
        self.height = self.root.winfo_height()

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)#canvas = window

        self.socket_client = client.SocketClient(SERVER_HOST, SERVER_PORT)
        self.socket_client.connect()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        #ボタンの設定(通常, dark, ロック, 中心X, 中心Y)
        button_list = [
            (FORWARD, FORWARD_ACTIVE, FORWARD_LOCK, FORWARD_ATTENTION, 2/4, 1/6, 'w'),
            (CCW    , CCW_ACTIVE    , CCW_LOCK    , CCW_ATTENTION    , 1/4, 3/6, 'a'),
            (CW     , CW_ACTIVE     , CW_LOCK     , CW_ATTENTION     , 3/4, 3/6, 'd'),
            (STOP   , STOP_ACTIVE   , STOP_LOCK   , STOP_ATTENTION   , 2/4, 3/6, 's'),
            (BACK   , BACK_ACTIVE   , BACK_LOCK   , BACK_ATTENTION   , 2/4, 5/6, 'z')
        ]
        
        self.buttons = []
        for img_path, dark_path, lock_path, attention_path, center_x_ratio, center_y_ratio, char in button_list:
            center_x = center_x_ratio * self.width
            center_y = center_y_ratio * self.height
            area     = self.calc_area(center_x, center_y)
            self.buttons.append(makeButton(self.canvas, img_path, dark_path, lock_path, attention_path, area, char, self.socket_client))
        
        self.last_activated_button = None        
        self.check_cursor()

    def calc_area(self, center_x, center_y):
        half = BUTTON_SIZE / 2
        return (center_x - half, center_y - half, center_x + half, center_y + half)

    def check_cursor(self):
        """
        カーソル位置を定期的に取得
        """
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()

        activated_button_this_frame = None # 今回のフレームでクリックされたボタンを一時的に保持

        for button in self.buttons:#すべてのボタンオブジェクトについて
            clicked_cmd = button.update(x, y) # makeButtonのupdateを呼び出し、クリックされたかを確認
            if clicked_cmd is not None:#クリックされたボタンがあるなら
                activated_button_this_frame = button # クリックされたボタンのオブジェクトを保存

        # 全てのボタンのチェックが完了した後、全体の状態を管理
        if activated_button_this_frame: # 今回、いずれかのボタンがクリックされた場合
            # 前回クリックされたボタンがあり、それが今回クリックされたボタンとは異なる場合
            if self.last_activated_button and self.last_activated_button != activated_button_this_frame:
                self.last_activated_button.reset() # 前回のボタンを通常状態に戻す

            # 最後にアクティブになったボタンを更新
            self.last_activated_button = activated_button_this_frame
        else: #今回クリックされたボタンがない場合、前回のボタンはdark状態のまま維持される
            pass
        self.root.after(20, self.check_cursor)

    def on_closing(self):
        print("GUIアプリケーションを終了します。ソケットを切断します。")
        self.socket_client.disconnect() # ソケットを切断
        self.root.destroy() # GUIを破棄
    
    def run(self):
        self.root.mainloop()
    
def main():
    app = GUIApp()
    app.run()
if __name__ == '__main__':
    main()
