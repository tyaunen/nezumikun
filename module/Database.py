import sqlite3
import json
from module.WeatherNews import WeatherNews
import datetime

class Database:
    """
    Database クラス
    永続化データを扱う
    何もかもをここにまとめているので肥大化しやすいが、シンプルなのでこのままにしている
    なにか処理を追加するときは、ファイルを分割できないかを同時に検討すること
    """
    def __init__(self, db_path="save.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._setup()

    def _setup(self):
        cursor = self.conn.cursor()
        # テーブル作成
        cursor.executescript("""
             CREATE TABLE IF NOT EXISTS message_history
             (
                 message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 channel_id INTEGER,
                 message TEXT
             );

             CREATE TABLE IF NOT EXISTS nezumi_equipment
             (
                 channel_id INTEGER PRIMARY KEY,
                 weapon TEXT,
                 armor TEXT,
                 job TEXT,
                 fullness INTEGER
             );
         """)
        self.conn.commit()


    def load_message_history(self, channel_id):
        """
        指定チャンネルのmessage_historyを取得（デフォルトは直近5件）
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT message
            FROM message_history
            WHERE channel_id = ?
            ORDER BY message_id ASC
        """, [channel_id])

        results = cursor.fetchall()
        return [json.loads(row['message']) for row in results]


    def _trim_message_history(self, channel_id, keep=7):
        """
        メッセージ履歴を一定数に保つために古いメッセージを削除
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE
            FROM message_history
            WHERE channel_id = ?
                AND message_id NOT IN (
                    SELECT message_id
                    FROM message_history
                    WHERE channel_id = ?
                    ORDER BY message_id DESC
                LIMIT ?
            )
        """, [channel_id, channel_id, keep])

    def add_message_history(self, channel_id, role, message):
        """
        1つのメッセージをmessage_historyに追加
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO message_history (channel_id, message)
            VALUES (?, ?)
        """, [channel_id, json.dumps({'role': role, 'content': message})])

        # 古いメッセージを削除して一定数に保つ
        self._trim_message_history(channel_id, keep=7)
        self.conn.commit()

    def reset_message_history(self, channel_id):
        """
        特定チャンネルのメッセージ履歴を全て削除
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM message_history WHERE channel_id = ?", [channel_id])
        self.conn.commit()


    def set_weapon(self, channel_id, weapon):
        """
        指定したチャンネルに武器を登録
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO nezumi_equipment (channel_id, weapon)
        VALUES (?, ?) ON CONFLICT(channel_id) 
        DO
        UPDATE SET weapon = ?
        """, [channel_id, weapon, weapon])
        self.conn.commit()

    def get_weapon(self, channel_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT weapon FROM nezumi_equipment WHERE channel_id = ?", [channel_id])
        result = cursor.fetchone()
        if result:
            return result['weapon']
        return None

    def set_armor(self, channel_id, armor):
        """
        指定したチャンネルに防具を登録
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nezumi_equipment (channel_id, armor)
            VALUES (?, ?) ON CONFLICT(channel_id) 
            DO
            UPDATE SET armor = ?
            """, [channel_id, armor, armor])
        self.conn.commit()

    def get_armor(self, channel_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT armor FROM nezumi_equipment WHERE channel_id = ?", [channel_id])
        result = cursor.fetchone()
        if result:
            return result['armor']
        return None

    def set_job(self, channel_id, job):
        """
        指定したチャンネルに職業を登録
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nezumi_equipment (channel_id, job)
            VALUES (?, ?) ON CONFLICT(channel_id) 
            DO
            UPDATE SET job = ?
            """, [channel_id, job, job])
        self.conn.commit()

    def get_job(self, channel_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT job FROM nezumi_equipment WHERE channel_id = ?", [channel_id])
        result = cursor.fetchone()
        if result:
            return result['job']
        return None

    def set_fullness(self, channel_id, fullness):
        fullness = max(0, min(100, fullness))
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO nezumi_equipment (channel_id, fullness)
            VALUES (?, ?) ON CONFLICT(channel_id) 
            DO
            UPDATE SET fullness = ?
            """, [channel_id, fullness, fullness])
        self.conn.commit()

    def add_fullness(self, channel_id, add):
        current = self.get_fullness(channel_id)
        if current is None:
            current = 0
        self.set_fullness(channel_id, current + add)

    def dec_fullness(self, channel_id, dec):
        current = self.get_fullness(channel_id)
        if current is None:
            current = 0
        self.set_fullness(channel_id, current - dec)

    def get_fullness(self, channel_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT fullness FROM nezumi_equipment WHERE channel_id = ?", [channel_id])
        result = cursor.fetchone()
        if result and result['fullness'] is not None:
            return result['fullness']
        return 0

    def get_habitat_channel_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT channel_id FROM nezumi_equipment")
        results = cursor.fetchall()
        return [row['channel_id'] for row in results]

    def add_habitat_channel_id(self, channel_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO nezumi_equipment (channel_id, weapon, armor, job, fullness)
            VALUES (?, ?, ?, ?, ?)
        """, [channel_id, "なし", "なし", "ただのネズミ", 100])
        self.conn.commit()

    def delete_habitat_channel_id(self, channel_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE
            FROM nezumi_equipment
            WHERE channel_id = ?
        """, [channel_id])
        self.conn.commit()

    def get_props(self, channel_id):
        weatherNews = self.get_weather()

        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        datetimeText = now.strftime('%Y/%m/%d %H:%M:%S')

        cursor = self.conn.cursor()
        cursor.execute("SELECT weapon, armor, job, fullness FROM nezumi_equipment WHERE channel_id = ?", [channel_id])
        result = cursor.fetchone()
        if result:
            return {
                "job": result["job"],
                "weapon": result["weapon"],
                "armor": result["armor"],
                "fullness": result["fullness"],
                "weatherNews": weatherNews,
                "datetime": datetimeText
            }
        return None

    def get_weather(self):
        weatherNews = WeatherNews()
        return weatherNews.get_weather()

    def close(self):
        self.conn.close()