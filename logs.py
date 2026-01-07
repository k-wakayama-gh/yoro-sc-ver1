import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

FILE_PATH = Path("logs.json")

def add_log(user_name: str, user_tel: str, user_address: str,
            lesson_number: int, lesson_title: str, action: str,
            file_path: Path = FILE_PATH):
    """
    ログをJSONファイルに追記する関数

    Parameters
    ----------
    user_name : str
        ユーザーの名前
    user_tel : str
        ユーザーの電話番号
    user_address : str
        ユーザーの住所
    lesson_number : int
        レッスン番号
    lesson_title : str
        レッスン名
    action : str
        "apply" or "cancel" などのアクション名
    file_path : Path, optional
        ログを保存するファイルパス（デフォルトは "logs.json"）
    """
    # JSONファイルを読み込む
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    # JSTの現在時刻を取得
    jst = timezone(timedelta(hours=9))
    timestamp = datetime.now(jst).isoformat()

    # ログを追加
    logs.append({
        "user_name": user_name,
        "user_tel": user_tel,
        "user_address": user_address,
        "lesson_number": lesson_number,
        "lesson_title": lesson_title,
        "action": action,
        "timestamp": timestamp
    })

    # JSONファイルに書き込む
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
