### 仮想環境使い方メモ

仮想環境名:"venv_gui"
```bash
# 仮想環境の作成
python -m venv venv_gui 
py -3.13 -m venv venv_gui #バージョン指定

# コマンドプロンプトでアクティベート
venv_gui\Scripts\activate.bat 
# PowerShellでアクティベート
.\venv_gui\Scripts\activate 
# 仮想環境を終了
deactivate 
# パッケージ一覧の作成
python -m pip freeze > requirements.txt 
# 一括ダウンロード
python -m pip install -r requirements.txt 
```
