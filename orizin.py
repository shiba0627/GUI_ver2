import tkinter as tk
from PIL import Image, ImageTk

class SimpleControlGUI(tk.Tk):
    """
    通信機能やカメラ機能を削除し、ボタン配置のみを再現したシンプルなGUIアプリケーションです。
    """
    def __init__(self):
        super().__init__()
        self.title("GUI Mockup")
        self.geometry('1275x765')

        # 白い背景のキャンバスを作成
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # PhotoImageオブジェクトがガベージコレクションされるのを防ぐためのリスト
        self.images = []

        # 表示するシンボル（ボタン）の情報を辞書で定義
        # key: コマンド名, value: (画像ファイルパス, x座標, y座標, リサイズ後のサイズ(幅, 高さ))
        symbol_definitions = {
            "forward": ('forward_joy.png', 637, 173, (130, 105)),
            "back": ('back_joy.png', 637, 450, (130, 105)),
            "right_diagonal_forward": ('right_diagonal_forward_joy.png', 784, 197, (130, 130)),
            "left_diagonal_forward": ('left_diagonal_forward_joy.png', 490, 197, (130, 130)),
            "cw_turn": ('cw_joy.png', 829, 314, (120, 120)),
            "ccw_turn": ('ccw_joy_bright.png', 447, 314, (120, 120)),
            "stop": ('stop_joy.png', 637, 312, (202, 102)),
            "finish": ('finish_letter.png', 1195, 720, (150, 100)),
        }

        # 定義に基づいてキャンバスにボタンを配置
        for command, (path, x, y, size) in symbol_definitions.items():
            self.create_symbol_button(command, path, x, y, size)

    def create_symbol_button(self, command, image_path, x, y, size):
        """
        指定された情報に基づいて、キャンバスに画像ボタンを作成します。
        """
        try:
            # 画像を開いてリサイズ
            img = Image.open(image_path).resize(size)
            photo_img = ImageTk.PhotoImage(img)
            
            # PhotoImageオブジェクトをリストに保持
            self.images.append(photo_img)

            # キャンバスに画像を作成
            button_id = self.canvas.create_image(x, y, image=photo_img, anchor=tk.CENTER)
            
            # 画像にクリックイベントを関連付け
            self.canvas.tag_bind(button_id, '<Button-1>', lambda event, cmd=command: self.on_button_click(cmd))

        except FileNotFoundError:
            print(f"警告: 画像ファイルが見つかりません: {image_path}")
            # ファイルがない場合は、代わりにテキストを表示
            text_id = self.canvas.create_text(x, y, text=command, font=("Arial", 12))
            self.canvas.tag_bind(text_id, '<Button-1>', lambda event, cmd=command: self.on_button_click(cmd))

    def on_button_click(self, command):
        """
        ボタンがクリックされたときに呼び出されるコールバック関数。
        クリックされたボタンのコマンド名をコンソールに出力します。
        """
        print(f"ボタン '{command}' がクリックされました。")
        # 終了ボタンが押されたらウィンドウを閉じる
        if command == "finish":
            self.destroy()

if __name__ == "__main__":
    app = SimpleControlGUI()
    app.mainloop()