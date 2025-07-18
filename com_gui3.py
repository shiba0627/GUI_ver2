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
import cv2
from config import CW, CW_ACTIVE, CW_ATTENTION, CW_LOCK
from config import CCW, CCW_ACTIVE, CCW_ATTENTION, CCW_LOCK
from config import FORWARD, FORWARD_ACTIVE, FORWARD_ATTENTION, FORWARD_LOCK
from config import BACK, BACK_ACTIVE, BACK_ATTENTION, BACK_LOCK
from config import STOP, STOP_ACTIVE, STOP_ATTENTION,STOP_LOCK
from config import BUTTON_SIZE, HOVER_TIME, ARC_RADIUS
from config import HOST, OBJECT_PORT, COMMAND_PORT, CONFIG_PORT, CONFIG_PATH
from config import CAM_ID_1, CAM_ID_2

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
    # (変更なし)
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
        # アプリケーション起動時に設定ファイルを送信
        self._send_config(CONFIG_PATH, HOST, CONFIG_PORT)

        self.str = [False] * 10 
        self.active_button = 's'
        self.attention_button = None

        self.root = tk.Tk()
        self.root.title("コマンド送信・カメラ映像テスト")
        self.root.state("zoomed")
        self.root.update_idletasks()
        self.width, self.height = self.root.winfo_width(), self.root.winfo_height()
        # ### 変更点 ###
        # キャンバスの背景を黒にして、カメラ映像がない場合でも見やすくする
        self.canvas = tk.Canvas(self.root, bg="black", width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        
        # 障害物情報受信用スレッドのセットアップ
        self.msg_q = queue.Queue()
        self.obstacle_socket = None
        self.obstacle_thread = threading.Thread(target=self._receive_obstacle_data_thread, daemon=True)
        self.obstacle_thread.start()
        
        # ### 変更点 ###
        # 1. カメラを初期化
        self.capture = cv2.VideoCapture(CAM_ID_1)
        if not self.capture.isOpened():
            print(f"エラー: カメラ {CAM_ID_1} を開けませんでした。")
        # 2. カメラ映像表示用のループを開始
        self._update_camera_image()

        # ウィンドウが閉じられた時の処理を登録
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

    def _send_config(self, file_path, host, port):
        """設定ファイルをサーバーに送信する"""
        try:
            # ファイルの存在をチェック
            if not os.path.exists(file_path):
                print(f"エラー: 設定ファイル '{file_path}' が見つかりません。")
                return

            print(f"設定ファイル '{file_path}' を {host}:{port} に送信します...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, port))
                with open(file_path, 'rb') as f:
                    sock.sendall(f.read())
            print("設定ファイルの送信が完了しました。")

        except ConnectionRefusedError:
            print(f"エラー: 設定サーバー({host}:{port})に接続できません。サーバーが起動しているか確認してください。")
        except Exception as e:
            print(f"設定ファイル送信中に予期せぬエラーが発生しました: {e}")
            
    def _receive_obstacle_data_thread(self):
        """(旧:_receive_laser_data_thread) サーバーに接続し、障害物データを受信する"""
        while True:
            try:
                print("障害物情報サーバーに接続試行中...")
                self.obstacle_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.obstacle_socket.connect((HOST, OBJECT_PORT))
                print("障害物情報サーバーに接続しました。")
                
                while True:
                    received_data = self.obstacle_socket.recv(1024)
                    if not received_data:
                        print("障害物情報サーバーとの接続が切れました。")
                        break
                    array = pickle.loads(received_data)
                    self.msg_q.put(array)
            
            except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError) as e:
                print(f"接続エラー(障害物): {e}。5秒後に再接続します。")
                if self.obstacle_socket:
                    self.obstacle_socket.close()
                time.sleep(5)
            except Exception as e:
                print(f"予期せぬエラー(障害物): {e}")
                if self.obstacle_socket:
                    self.obstacle_socket.close()
                break
    
    # ### 変更点 ###
    # 3. コマンドを送信するためのメソッドを追加
    def _send_command(self, command):
        """指定されたコマンドをサーバーに送信する"""
        print(f"コマンド '{command}' を送信中...")
        try:
            # 毎回新しくソケットを作成し、接続・送信・切断を行う
            # これにより、サーバー側が常時待ち受けでなくても対応しやすい
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((HOST, COMMAND_PORT))
                sock.sendall(command.encode("utf-8"))
                print(f"コマンド '{command}' の送信完了。")
        except ConnectionRefusedError:
            print(f"エラー: コマンドサーバー({HOST}:{COMMAND_PORT})に接続できません。")
        except Exception as e:
            print(f"コマンド送信中にエラーが発生しました: {e}")

    # ### 変更点 ###
    # 4. カメラ映像を更新し、キャンバスの背景として表示するメソッド
    def _update_camera_image(self):
        """カメラからフレームを取得し、キャンバスの背景として表示する"""
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                # BGRからRGBに変換し、Pillow Imageオブジェクトに変換
                cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(cv_image)
                
                # キャンバスのサイズにリサイズ
                pil_image = pil_image.resize((self.width, self.height), Image.LANCZOS)
                
                # PhotoImageオブジェクトに変換
                self.bg_image = ImageTk.PhotoImage(image=pil_image)
                
                # 背景画像として設定（なければ作成、あれば更新）
                if not hasattr(self, 'bg_canvas_id'):
                    self.bg_canvas_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')
                else:
                    self.canvas.itemconfig(self.bg_canvas_id, image=self.bg_image)
                
                # 全ての他の要素（ボタンなど）より背面にする
                self.canvas.lower(self.bg_canvas_id)

        # 33ミリ秒後（約30fps）に再度このメソッドを呼び出す
        self.root.after(33, self._update_camera_image)


    def check_cursor(self):
        try:
            new_str = self.msg_q.get_nowait()
            self.str = new_str
        except queue.Empty:
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
            # ### 変更点 ###
            # 5. active_buttonが更新されたタイミングでコマンドを送信する
            self._send_command(self.active_button)

        self.root.after(20, self.check_cursor)

    def _cleanup(self):
        """ソケットとカメラを解放し、ウィンドウを破棄する"""
        print("アプリケーションを終了します。")
        if self.obstacle_socket:
            self.obstacle_socket.close()
        # ### 変更点 ###
        # 6. カメラリソースを解放
        if self.capture.isOpened():
            self.capture.release()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = GUIApp()
    app.run()
