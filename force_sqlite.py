# force_sqlite.py

def force_sqlite():
    import sqlite3
    # SQLiteデータベースへの接続
    conn = sqlite3.connect('/home/db_dir/database.sqlite')
    cursor = conn.cursor()

    # version_numカラムの値を更新するSQLクエリ
    update_query = "UPDATE alembic_version SET version_num = '94d5d4ca5cb3'"

    # SQLクエリを実行してデータを更新
    cursor.execute(update_query)

    # 変更をコミットしてデータベースに反映
    conn.commit()

    # 接続をクローズ
    conn.close()

if __name__ == "__main__":
    force_sqlite()
