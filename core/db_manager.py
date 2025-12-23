import sqlite3
import threading
import logging
import csv
import os
from datetime import datetime

class DBManager:
    def __init__(self, db_file, exe_dir):
        self.db_file = db_file
        self.exe_dir = exe_dir
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_table()
        self.lock = threading.Lock()

    def init_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                action TEXT,
                item_type TEXT,
                filename TEXT,
                source_path TEXT,
                dest_path TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()

    def log(self, action, item_type, filename, src, dst, status="SUCCESS"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            try:
                self.cursor.execute('''
                    INSERT INTO history (timestamp, action, item_type, filename, source_path, dest_path, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (now, action, item_type, filename, src, dst, status))
                self.conn.commit()
            except Exception as e:
                logging.error(f"数据库写入失败: {e}")

    def cleanup_old_logs(self, retention_count):
        """保留最近的 retention_count 条记录，删除其余记录"""
        if retention_count <= 0:
            return
            
        with self.lock:
            try:
                # 获取需要保留的最小 ID
                self.cursor.execute(f'''
                    SELECT id FROM history 
                    ORDER BY id DESC 
                    LIMIT 1 OFFSET {retention_count - 1}
                ''')
                result = self.cursor.fetchone()
                
                if result:
                    min_id_to_keep = result[0]
                    self.cursor.execute('DELETE FROM history WHERE id < ?', (min_id_to_keep,))
                    self.conn.commit()
                    logging.info(f"已清理旧日志，保留最近 {retention_count} 条记录")
            except Exception as e:
                logging.error(f"清理旧日志失败: {e}")

    def export_csv(self):
        csv_file = os.path.join(self.exe_dir, f"整理记录导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with self.lock:
            try:
                self.cursor.execute("SELECT * FROM history")
                rows = self.cursor.fetchall()
                
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', '时间', '操作', '类型', '文件名', '源路径', '目标路径', '状态'])
                    writer.writerows(rows)
                return csv_file
            except Exception as e:
                logging.error(f"导出 CSV 失败: {e}")
                return None

    def close(self):
        self.conn.close()
