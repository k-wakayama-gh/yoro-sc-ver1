# logs.py

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


# FILE_PATH = Path("logs.json")


env_mount = "WEBSITES_ENABLE_APP_SERVICE_STORAGE"


if env_mount in os.environ:
    log_dir = Path("/home/log_dir/")
else:
    log_dir = Path(".")


log_file = log_dir / "logs.json"


# if log_dir != "":
#     if not os.path.exists(log_dir):
#         os.makedirs(log_dir)


log_dir.mkdir(parents=True, exist_ok=True)


def add_log(user_name: str, user_tel: str, user_address: str,
            lesson_number: int, lesson_title: str, action: str,
            file_path: Path = log_file):
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

