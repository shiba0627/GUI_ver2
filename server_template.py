import socket

HOST = '127.0.0.1'
PORT = 12345

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        print(f"サーバーを起動中... {HOST}:{PORT}")
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        
        print("クライアントからの接続を待機中...")
        
        # サーバーは一度に一つのクライアントからの接続を受け付ける
        client_socket, client_address = server_socket.accept()
        print(f"クライアントが接続しました: {client_address}")
        
        with client_socket:
            while True:
                try:
                    # クライアントからデータを受信する
                    # recv()はデータが到着するまでブロックする
                    data = client_socket.recv(1024)
                    if not data:
                        # データがなければ、クライアントが切断したと判断
                        print("クライアントが切断しました。")
                        break # ループを抜けて接続を閉じる
                    
                    received_message = data.decode('utf-8')
                    print(f"受信： '{received_message}'")
                    
                    #エコーバックの文章を作る
                    response_message = f'Received:{received_message}'
                    client_socket.sendall(response_message.encode('utf-8'))
                    print(f"'{response_message}'をエコーバック")

                except ConnectionResetError:
                    # クライアントが強制的に切断した場合に発生
                    print("クライアントが予期せず切断しました。")
                    break
                except Exception as e:
                    print(f"サーバー側でエラーが発生しました: {e}")
                    break
        print("クライアントとの通信が終了しました。")

if __name__ == "__main__":
    run_server()