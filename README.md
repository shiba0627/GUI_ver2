### 仮想環境使い方メモ

仮想環境名:"venv_gui"
```bash
#仮想環境の作成
python -m venv venv_gui 
#コマンドプロンプトでアクティベート
venv_gui\Scripts\activate.bat 
# PowerShellでアクティベート
.\venv_gui\Scripts\activate 
deactivate # 仮想環境を終了
python -m pip freeze > requirements.txt #パッケージ一覧の作成
python -m pip install -r requirements.txt #一括ダウンロード
```
