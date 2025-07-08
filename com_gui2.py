import os
import tkinter as tk
from PIL import Image, ImageTk
import time
import socket
import threading
import queue
import pickle
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
from config import HOST, OBJECT_PORT, COMMAND_PORT, CONFIG_PORT

class BaseButton:
    def __init__(self, canvas, img_path, active_path, lock_path, attention_path, area, cmd):
        self.canvas = canvas
        width, height = int(area[2] - area[0]), int(area[3] - area[1])
        
        try:
            self.img = ImageTk.PhotoImage(Image.open(img_path).resize((width, height)))
            self.img_active = ImageTk.PhotoImage(Image.open(active_path).resize((width, height)))
            self.img_attention = ImageTk.PhotoImage(Image.open(attention_path).resize((width, height)))
            self.img_lock = ImageTk.PhotoImage(Image.open(lock_path).resize((width, height)))
        except FileNotFoundError:
            print(f"警告: 画像ファイルが見つかりません。'{img_path}' または関連ファイルを確認してください。")
            dummy_img = ImageTk.PhotoImage(Image.new('RGB', (width, height), 'gray'))
            self.img = self.img_active = self.img_attention = self.img_lock = dummy_img
        except Exception as e:
            print(f"画像読み込み中にエラーが発生しました: {e}")
            return

        self.my_cmd = cmd
        self.area = area
        self.stay_time = HOVER_TIME
        self.enter_time = None
        self.arc_id = None
        self.arc_radius = ARC_RADIUS
        self.locked = False
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
        if self.locked:
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None
            self.enter_time = None
            return None, None

        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:
            if self.enter_time is None:
                self.enter_time = time.time()
            elapsed = time.time() - self.enter_time
            percent = min(elapsed / self.stay_time * 100, 100)
            self.draw_arc(cursor_x + 40, cursor_y, percent)
            if elapsed >= self.stay_time:
                if self.arc_id:
                    self.canvas.delete(self.arc_id)
                    self.arc_id = None
                return self.my_cmd, self.my_cmd
            else:
                return self.my_cmd, None
        else:
            self.enter_time = None
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None
            return None, None

class JoyButton(BaseButton):
    def update(self, cursor_x, cursor_y, active_button, attention_button):
        if self.locked:
            image_to_show = self.img_lock
        elif self.my_cmd == active_button:
            image_to_show = self.img_active
        elif self.my_cmd == attention_button:
            image_to_show = self.img_attention
        else:
            image_to_show = self.img
            
        self.canvas.itemconfig(self.image_id, image=image_to_show)
        return self._handle_hover(cursor_x, cursor_y)

class GUIApp:
    def __init__(self):
        # 障害物情報。Trueは障害物ありを意味する
        self.str = [False] * 10 

        self.active_button = 's'
        self.attention_button = None

        self.root = tk.Tk()
        self.root.title("通信機能テスト")
        self.root.state("zoomed")
        self.root.update_idletasks()
        self.width, self.height = self.root.winfo_width(), self.root.winfo_height()
        self.canvas = tk.Canvas(self.root, bg="white", width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        
        # ### 変更点 ###
        # 1. スレッド間でのデータ受け渡しのためにキューを作成
        self.msg_q = queue.Queue()
        # 2. ソケットをインスタンス変数として保持
        self.client_socket = None
        # 3. 障害物情報を受信するスレッドを開始
        #    daemon=Trueに設定すると、メインプログラム終了時にスレッドも自動的に終了する
        self.network_thread = threading.Thread(target=self._receive_laser_data_thread, daemon=True)
        self.network_thread.start()
        # 4. ウィンドウが閉じられた時の処理を登録
        self.root.protocol("WM_DELETE_WINDOW", self._cleanup)

        button_list = [
            (FORWARD, FORWARD_ACTIVE, FORWARD_LOCK, FORWARD_ATTENTION, 2/4, 1/6, 'w'),
            (CCW, CCW_ACTIVE, CCW_LOCK, CCW_ATTENTION, 1/4, 3/6, 'a'),
            (CW, CW_ACTIVE, CW_LOCK, CW_ATTENTION, 3/4, 3/6, 'd'),
            (STOP, STOP_ACTIVE, STOP_LOCK, STOP_ATTENTION, 2/4, 3/6, 's'),
            (BACK, BACK_ACTIVE, BACK_LOCK, BACK_ATTENTION, 2/4, 5/6, 'z')
        ]

        self.buttons = []
        for img_path, active_path, lock_path, attention_path, center_x_ratio, center_y_ratio, cmd in button_list:
            center_x, center_y = center_x_ratio * self.width, center_y_ratio * self.height
            area = (center_x - BUTTON_SIZE/2, center_y - BUTTON_SIZE/2, center_x + BUTTON_SIZE/2, center_y + BUTTON_SIZE/2)
            self.buttons.append(JoyButton(self.canvas, img_path, active_path, lock_path, attention_path, area, cmd))

        self.check_cursor()

    # ### 変更点 ###
    # 障害物情報を受信するためのメソッド（スレッドで実行される）
    def _receive_laser_data_thread(self):
        """サーバーに接続し、継続的に障害物データを受信してキューに入れる"""
        while True:
            try:
                print("サーバーに接続試行中...")
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((SERVER_HOST, SERVER_PORT))
                print("サーバーに接続しました。")
                
                while True:
                    # データを受信
                    received_data = self.client_socket.recv(1024)
                    if not received_data:
                        # サーバーが接続を切断した場合
                        print("サーバーとの接続が切れました。")
                        break
                    
                    # 受信したデータをデシリアライズ（元のPythonオブジェクトに戻す）
                    array = pickle.loads(received_data)
                    # キューに最新データを入れる
                    self.msg_q.put(array)
            
            except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError) as e:
                print(f"接続エラー: {e}。5秒後に再接続します。")
                if self.client_socket:
                    self.client_socket.close()
                time.sleep(5) # 5秒待ってから再接続を試みる
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {e}")
                if self.client_socket:
                    self.client_socket.close()
                break # ループを終了

    def check_cursor(self):
        # ### 変更点 ###
        # キューから新しい障害物情報を取得する
        try:
            # get_nowait()でキューにデータがなければ即座に例外を発生させる
            new_str = self.msg_q.get_nowait()
            self.str = new_str
            # print(f"障害物情報を更新: {self.str}") # デバッグ用
        except queue.Empty:
            # キューが空の場合は何もしない
            pass

        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()

        for button in self.buttons:
            button.locked = False

        if self.str[1]:
            for button in self.buttons:
                if button.my_cmd == 'w': button.locked = True; break
        if self.str[3]:
            for button in self.buttons:
                if button.my_cmd == 'd': button.locked = True; break
        if self.str[6]:
            for button in self.buttons:
                if button.my_cmd == 'z': button.locked = True; break
        if self.str[9]:
            for button in self.buttons:
                if button.my_cmd == 'a': button.locked = True; break
        
        new_attention = None
        new_active = None
        for button in self.buttons:
            attention, active = button.update(x, y, self.active_button, self.attention_button)
            if attention: new_attention = attention
            if active: new_active = active

        self.attention_button = new_attention

        if new_active and new_active != self.active_button:
            self.active_button = new_active
            print(f'active_button updated: {self.active_button}')

        self.root.after(20, self.check_cursor)

    # ### 変更点 ###
    # アプリケーション終了時に呼び出されるクリーンアップ処理
    def _cleanup(self):
        """ソケットを閉じてからウィンドウを破棄する"""
        print("アプリケーションを終了します。")
        if self.client_socket:
            self.client_socket.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = GUIApp()
    app.run()
