'''障害物情報を送信するテストサーバー'''
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))#親ディレクトリの絶対パスを追加
from config import HOST, OBJECT_PORT, COMMAND_PORT, CONFIG_PORT
import socket
import threading
import random
import time, pickle
def run_test_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#IPv4, TCPを定義
    server_socket.bind((HOST, OBJECT_PORT))#ホストとポートを指定
    server_socket.listen(1)#接続待ち、最大接続数は1
    print(f"テストサーバーが {HOST}:{OBJECT_PORT} で待機中...")
    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"{addr} から接続がありました。")
            try:
                while True:
                    # ランダムな障害物情報リストを作成（10個のTrue/False）
                    obstacle_data = [random.choice([True, False]) for _ in range(10)]
                    print(f"送信データ: {obstacle_data}")
                    
                    # データをシリアライズ（バイト列に変換）して送信
                    serialized_data = pickle.dumps(obstacle_data)
                    conn.sendall(serialized_data)
                    time.sleep(3) # 3秒待機
            except (ConnectionResetError, BrokenPipeError):
                print(f"{addr} との接続が切れました。")
            finally:
                conn.close()
    except KeyboardInterrupt:
        print("サーバーを終了します。")
        server_socket.close()
        sys.exit(0)
def main():
    run_test_server()

if __name__ =='__main__':
    main()