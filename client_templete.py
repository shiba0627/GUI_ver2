import socket
import threading
import time
from collections import deque # メッセージキューのためにdequeを使用

class SocketClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.connected = False
        self.send_queue = deque() # 送信するメッセージを格納するキュー
        self.receive_thread = None
        self.running = False

    def connect(self):
        """サーバーに接続を試みる"""
        if self.connected:
            print("既に接続済みです。")
            return True
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            self.running = True
            print(f"IPアドレス：{self.host}, ポート番号：{self.port} に接続しました。")
            
            # 受信スレッドを開始
            self.receive_thread = threading.Thread(target=self._receive_data_loop)
            self.receive_thread.daemon = True # メインスレッド終了時に終了するように設定
            self.receive_thread.start()
            
            return True
        except ConnectionRefusedError:
            print(f"エラー: サーバー {self.host}:{self.port} への接続が拒否されました。サーバーが起動しているか確認してください。")
            self.connected = False
            return False
        except Exception as e:
            print(f"接続エラーが発生しました: {e}")
            self.connected = False
            return False

    def send_message(self, message):
        """メッセージをキューに追加し、送信を試みる"""
        if not self.connected:
            print("エラー: サーバーに接続していません。")
            return
        
        # メッセージをキューに追加
        self.send_queue.append(message)
        # キューからメッセージを送信する処理は別スレッドで行う
        # ここでは、GUIからの呼び出しが頻繁に発生しても、すぐに戻るようにする

    def _send_data_from_queue(self):
        """キューからメッセージを送信する内部メソッド"""
        while self.running and self.connected:
            if self.send_queue:
                message = self.send_queue.popleft() # キューの先頭から取り出す
                try:
                    self.client_socket.sendall(message.encode('utf-8'))
                    print(f"送信: '{message}'")
                except (ConnectionResetError, BrokenPipeError) as e:
                    print(f"送信エラー (接続切断): {e}")
                    self.disconnect()
                    break
                except Exception as e:
                    print(f"送信エラー: {e}")
            time.sleep(0.01) # キューが空でもCPUを使いすぎないように少し待つ

    def _receive_data_loop(self):
        """サーバーからのデータを受信し続ける内部メソッド"""
        # 受信ループ中に送信処理も継続的に行うために、送信スレッドを開始
        self.send_thread = threading.Thread(target=self._send_data_from_queue)
        self.send_thread.daemon = True
        self.send_thread.start()

        while self.running and self.connected:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    print("サーバーが切断しました。")
                    self.disconnect()
                    break
                received_response = data.decode('utf-8')
                print(f"受信: '{received_response}'")
                # ここで受信したデータをGUIに渡す処理などを追加できる
                # 例: self.on_data_received_callback(received_response)
            except (ConnectionResetError, OSError) as e: # OSErrorは接続が閉じられた場合に発生
                print(f"受信エラー (接続切断): {e}")
                self.disconnect()
                break
            except Exception as e:
                print(f"受信エラー: {e}")
                self.disconnect()
                break
        print("受信スレッドを終了しました。")


    def disconnect(self):
        """サーバーから切断する"""
        if self.connected:
            self.running = False # ループを停止
            if self.client_socket:
                try:
                    self.client_socket.shutdown(socket.SHUT_RDWR) # 送受信を停止
                    self.client_socket.close()
                except OSError as e:
                    print(f"ソケットクローズ中にエラー: {e}")
                finally:
                    self.client_socket = None
            self.connected = False
            print("サーバーから切断しました。")
        
        # スレッドが終了するのを待つ (デーモンスレッドなので厳密には不要だが、明示的に)
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1) # 少し待つ
        if self.send_thread and self.send_thread.is_alive():
            self.send_thread.join(timeout=1)

# モジュールが直接実行された場合のテストコード
if __name__ == "__main__":
    print("--- クライアントモジュールのテスト実行 ---")
    TEST_HOST = '127.0.0.1'
    TEST_PORT = 12345
    
    my_client = SocketClient(TEST_HOST, TEST_PORT)
    if my_client.connect():
        # 少し待ってからメッセージを送信
        time.sleep(1) 
        my_client.send_message("Hello from test!")
        my_client.send_message("Another message.")
        
        # ユーザー入力を待つループ（GUIがない場合のテスト用）
        try:
            while my_client.connected:
                msg = input("メッセージを入力 ('exit' で終了): ")
                if msg.lower() == 'exit':
                    break
                my_client.send_message(msg)
                time.sleep(0.1) # 送信頻度を調整
        except KeyboardInterrupt:
            pass # Ctrl+Cで終了

        my_client.disconnect()
    print("--- テスト実行終了 ---")