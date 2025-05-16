### 仮想環境使い方メモ
以下、カレントディレクトリを"C:\Users\tonegawa\program\GUI_ver2"とする

仮想環境名:"venv_gui"
```bash
python -m venv venv_gui #仮想環境の作成
venv_gui\Scripts\activate.bat #コマンドプロンプトでアクティベート
.\venv_gui\Scripts\activate # VScodeのターミナルでアクティベート
deactivate # 仮想環境を終了
python -m pip freeze > requirements.txt #パッケージ一覧の作成
python -m pip install -r requirements.txt #一括ダウンロード
```
