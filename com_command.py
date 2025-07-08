# コマンドを受信するテストサーバー
import socket
import threading
import time, pickle
from config import HOST, CONFIG_PORT, OBJECT_PORT, COMMAND_PORT
def run_command_server():
    """送信されたコマンドを受信して表示するテストサーバー"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, COMMAND_PORT))
    server_socket.listen(1)
    print(f"コマンドテストサーバーが {HOST}:{COMMAND_PORT} で待機中...")

    while True:
        conn, addr = server_socket.accept()
        # print(f"コマンドクライアント {addr} から接続がありました。")
        try:
            data = conn.recv(1024)
            if data:
                print(f"--- 受信コマンド: {data.decode('utf-8')} ---")
        except Exception as e:
            print(f"コマンド受信エラー: {e}")
        finally:
            conn.close()

def main():
    run_command_server()

if __name__ =='__main__':
    main()