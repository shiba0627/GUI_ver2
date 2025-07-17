'''
通信機能付きGUI
ロボットの状態を受信し、UIを更新
serverと接続, このコードはクライアント
'''
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
from config import HOST, OBJECT_PORT, COMMAND_PORT, CONFIG_PORT, CONFIG_PATH, STATE_PORT
from config import CAM_ID_1, CAM_ID_2

class BaseButton:
    '''
    ボタンの基底クラス
    '''
    def __init__(self, canvas:tk.Canvas, 
        img_path:str, active_path:str, lock_path:str, attention_path:str, 
        area:tuple[float, float, float, float], cmd:str
        ):
        '''
        canvas        : キャンバス
        img_path      : デフォルト画像パス
        active_path   : 選択中画像パス
        lock_path     : ロック画像パス
        attention_path: 滞留中画像パス
        area          : ボタンの領域
        cmd           : コマンド
        '''
        self.canvas = canvas
        width, height = int(area[2] - area[0]), int(area[3] - area[1])
        
        try:
            self.img = ImageTk.PhotoImage(Image.open(img_path).resize((width, height)))
            self.img_active = ImageTk.PhotoImage(Image.open(active_path).resize((width, height)))
            self.img_attention = ImageTk.PhotoImage(Image.open(attention_path).resize((width, height)))
            self.img_lock = ImageTk.PhotoImage(Image.open(lock_path).resize((width, height)))
        except FileNotFoundError:
            print(f"画像ファイル読み込みエラー'{img_path}'が読み込めません")
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
        '''
        アークを描画

        Args:
            x: アークの中心のx座標
            y: アークの中心のy座標
            percent: アークの長さのパーセント
        '''
        if self.arc_id:#アークが存在するなら
            self.canvas.delete(self.arc_id)#アークを削除, 被らないように
        angle = percent * 3.6#アークの角度を計算
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius, 
            x + self.arc_radius, y + self.arc_radius,
            start=90, extent=-angle, style='pieslice',
            outline='white', fill='black'
        )

    def _handle_hover(self, cursor_x, cursor_y):
        '''
        マウスカーソルの座標がボタン領域内部にあるかチェック
        領域内部に入った時間をチェック, 一定以上ならactive, 一定以下ならattention

        Args:
            cursor_x: マウスカーソルのx座標
            cursor_y: マウスカーソルのy座標

        Returns:
            attention, active
            attention: 滞留中なら自分のコマンド, それ以外はNone
            active: 選択状態なら自分のコマンド, それ以外はNone
        '''
        if self.locked:#ロック状態なら
            if self.arc_id:#アークが存在するなら
                self.canvas.delete(self.arc_id)
                self.arc_id = None
            self.enter_time = None
            return None, None

        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:#カーソルが領域内部にあるなら
            if self.enter_time is None:#領域内部に入った瞬間の時刻を記録
                self.enter_time = time.time()
            elapsed = time.time() - self.enter_time#領域内部に入ってからの経過時間を計算
            percent = min(elapsed / self.stay_time * 100, 100)#経過時間をパーセントに変換
            self.draw_arc(cursor_x + 40, cursor_y, percent)#カーソルの右側にアークを描画
            if elapsed >= self.stay_time:#経過時間が一定以上なら
                if self.arc_id:#アークが存在するなら
                    self.canvas.delete(self.arc_id)#アークを削除
                    self.arc_id = None
                return self.my_cmd, self.my_cmd
            else:
                return self.my_cmd, None
        else:#カーソルが領域外部なら
            self.enter_time = None
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None
            return None, None

class JoyButton(BaseButton):
    '''
    操作ボタンのクラス
    '''
    def update(self, cursor_x, cursor_y, active_button, attention_button):
        '''
        ボタンの状態を管理

        Args:
            cursor_x: マウスカーソルのx座標
            cursor_y: マウスカーソルのy座標
            active_button: 選択中ボタンのコマンド
            attention_button: 滞留中ボタンのコマンド

        Returns:
            attention, active
            attention: 滞留中なら自分のコマンド, それ以外はNone
            active: 選択状態なら自分のコマンド, それ以外はNone
        '''
        if self.locked:#最優先でロック状態かチェック
            image_to_show = self.img_lock
        elif self.my_cmd == active_button:#自分が選択中なら
            image_to_show = self.img_active
        elif self.my_cmd == attention_button:#自分が滞留中なら
            image_to_show = self.img_attention
        else:
            image_to_show = self.img#それ以外はデフォルト画像
            
        self.canvas.itemconfig(self.image_id, image=image_to_show)
        return self._handle_hover(cursor_x, cursor_y)


class GUIApp:
    def __init__(self):
        # アプリケーション起動時に設定ファイルを送信
        self._send_config(CONFIG_PATH, HOST, CONFIG_PORT)

        self.str = [False] * 10 
        self.active_button = 's'
        self.attention_button = None

        #緊急停止表示用
        self.state_q = queue.Queue() # 状態受信用キュー
        self.emergency_stopped = False # 緊急停止フラグ

        # 状態受信用スレッドのセットアップと開始
        self.state_thread = threading.Thread(target=self._receive_state_data_thread, daemon=True)
        self.state_thread.start()

        self.root = tk.Tk()
        self.root.title("コマンド送信・カメラ映像テスト")
        self.root.state("zoomed")
        self.root.update_idletasks()
        self.width, self.height = self.root.winfo_width(), self.root.winfo_height()
        
        self.canvas = tk.Canvas(self.root, bg="black", width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        
        # 障害物情報受信用スレッドのセットアップ
        self.msg_q = queue.Queue()
        self.obstacle_socket = None
        self.obstacle_thread = threading.Thread(target=self._receive_obstacle_data_thread, daemon=True)
        self.obstacle_thread.start()
        
        # カメラを初期化
        self.capture = cv2.VideoCapture(CAM_ID_1)
        if not self.capture.isOpened():
            print(f"エラー: カメラ {CAM_ID_1} を開けませんでした。")
        
        self._update_camera_image()

        # ウィンドウが閉じられた時の処理を登録
        self.root.protocol("WM_DELETE_WINDOW", self._cleanup)

        button_list = [
            (FORWARD, FORWARD_ACTIVE, FORWARD_LOCK, FORWARD_ATTENTION, 2/4, 1/6, 'w'),
            (CCW, CCW_ACTIVE, CCW_LOCK, CCW_ATTENTION, 1/4, 3/6, 'a'),
            (CW, CW_ACTIVE, CW_LOCK, CW_ATTENTION, 3/4, 3/6, 'd'),
            (STOP, STOP_ACTIVE, STOP_LOCK, STOP_ATTENTION, 2/4, 3/6, 's'),
            (BACK, BACK_ACTIVE, BACK_LOCK, BACK_ATTENTION, 2/4, 5/6, 'x')
        ]

        self.buttons = []
        for img_path, active_path, lock_path, attention_path, center_x_ratio, center_y_ratio, cmd in button_list:
            center_x, center_y = center_x_ratio * self.width, center_y_ratio * self.height
            area = (center_x - BUTTON_SIZE/2, center_y - BUTTON_SIZE/2, center_x + BUTTON_SIZE/2, center_y + BUTTON_SIZE/2)
            self.buttons.append(JoyButton(self.canvas, img_path, active_path, lock_path, attention_path, area, cmd))

        self.check_cursor()
        self._check_robot_state() # 修正点1: 状態チェックを開始

    def _send_config(self, file_path, host, port):
        """設定ファイルをサーバーに送信する"""
        try:
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
        """サーバーに接続し、障害物データを受信する"""
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

    def _receive_state_data_thread(self):
        """サーバーに接続し、ロボットの状態データを受信する"""
        while True:
            try:
                print("ロボット状態サーバーに接続試行中...")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((HOST, STATE_PORT))
                    print("ロボット状態サーバーに接続しました。")
                    while True:
                        received_data = sock.recv(1024)
                        if not received_data:
                            print("ロボット状態サーバーとの接続が切れました。")
                            break
                        state = received_data.decode("utf-8")
                        print(f"ロボットの状態を受信: {state}")
                        self.state_q.put(state)
            except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError) as e:
                print(f"接続エラー(状態): {e}。5秒後に再接続します。")
                time.sleep(5)
            except Exception as e:
                print(f"予期せぬエラー(状態): {e}")
                break

    def _send_command(self, command):
        """指定されたコマンドをサーバーに送信する"""
        print(f"コマンド '{command}' を送信中...")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((HOST, COMMAND_PORT))
                sock.sendall(command.encode("utf-8"))
                print(f"コマンド '{command}' の送信完了。")
        except ConnectionRefusedError:
            print(f"エラー: コマンドサーバー({HOST}:{COMMAND_PORT})に接続できません。")
        except Exception as e:
            print(f"コマンド送信中にエラーが発生しました: {e}")

    def _update_camera_image(self):
        """カメラからフレームを取得し、キャンバスの背景として表示する"""
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(cv_image)
                pil_image = pil_image.resize((self.width, self.height), Image.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(image=pil_image)
                if not hasattr(self, 'bg_canvas_id'):
                    self.bg_canvas_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')
                else:
                    self.canvas.itemconfig(self.bg_canvas_id, image=self.bg_image)
                self.canvas.lower(self.bg_canvas_id)
        self.root.after(33, self._update_camera_image)

    # このメソッドを追加
    def _check_robot_state(self):
        """ロボットの状態キューをチェックし、GUIに反映する"""
        try:
            state = self.state_q.get_nowait()
            if state == "EG_stop" and not self.emergency_stopped:
                self.emergency_stopped = True
                print("緊急停止信号を検出.UIをロックします。")
                self.canvas.create_rectangle(0, 0, self.width, self.height, fill="red", stipple="gray50", tag="eg_stop_overlay")
                self.canvas.create_text(self.width/2, self.height/2, text="緊急停止", font=("MS Gothic", 100, "bold"), fill="white", tag="eg_stop_text")
                self.canvas.tag_raise("eg_stop_overlay")
                self.canvas.tag_raise("eg_stop_text")
            elif state == "stop":
                print("停止信号を検出。")
                #self.active_button = 's'
                #self._send_command('s')
        except queue.Empty:
            pass
        self.root.after(100, self._check_robot_state)

    def check_cursor(self):
        if self.emergency_stopped: return # 修正点2: 緊急停止中は処理を中断
        
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
            self._send_command(self.active_button)

        self.root.after(20, self.check_cursor)

    def _cleanup(self):
        """ソケットとカメラを解放し、ウィンドウを破棄する"""
        print("アプリケーションを終了します。")
        if self.obstacle_socket:
            self.obstacle_socket.close()
        if self.capture.isOpened():
            self.capture.release()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = GUIApp()
    app.run()
