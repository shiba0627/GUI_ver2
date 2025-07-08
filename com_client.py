#障害物情報を送信するテストサーバー
import socket
import threading
import time, pickle
from config import HOST, OBJECT_PORT, COMMAND_PORT, CONFIG_PORT
def run_test_server():
    import random
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, OBJECT_PORT))
    server_socket.listen(1)
    print(f"テストサーバーが {HOST}:{OBJECT_PORT} で待機中...")
    
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
def main():
    run_test_server()

if __name__ =='__main__':
    main()