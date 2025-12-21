import os
import shutil
import sys
import logging
from .ai_client import AIClient

class Organizer:
    def __init__(self, paths, config, rules, db, log_callback=None, api_key=None, dry_run=False):
        self.paths = paths
        self.config = config
        self.rules = rules
        self.db = db
        self.log_callback = log_callback
        self.dry_run = dry_run
        
        # 初始化 AI 客户端
        api_key = api_key if api_key else self.config.get('SETTINGS', 'API_KEY', fallback='').strip()
        base_url = self.config.get('SETTINGS', 'BASE_URL', fallback='https://api.deepseek.com').strip()
        model = self.config.get('SETTINGS', 'MODEL', fallback='deepseek-chat').strip()
        self.ai_client = AIClient(api_key, base_url, model, log_callback)

    def print_log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def get_unique_path(self, dest_dir, filename, suffix=""):
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        dest_path = os.path.join(dest_dir, new_filename)
        while os.path.exists(dest_path):
            insert_str = f"_{suffix}{counter}" if suffix else f"_{counter}"
            new_filename = f"{base}{insert_str}{ext}"
            dest_path = os.path.join(dest_dir, new_filename)
            counter += 1
        return dest_path

    def get_category(self, filename, is_dir=False):
        # 1. 扩展名匹配
        if not is_dir:
            ext = os.path.splitext(filename)[1].lower()
            for category, patterns in self.rules.items():
                if ext in patterns: return category
        
        # 2. 关键词匹配
        for category, patterns in self.rules.items():
            for pattern in patterns:
                if pattern.lower() in filename.lower(): return category

        # 3. AI 识别
        ai_cat = self.ai_client.ask_ai(filename, self.rules.keys(), is_dir)
        if ai_cat: return ai_cat
            
        return "21_其他杂项"

    def run(self):
        source_dir = self.paths["EXE_DIR"]
        target_name = self.config.get('SETTINGS', 'TARGET_NAME', fallback='归档文件夹')
        
        self.print_log(f"=== 开始整理 ===")
        self.print_log(f"工作目录: {source_dir}")
        if self.dry_run: self.print_log("--- 预演模式 ---")

        exclude_paths = [
            os.path.abspath(sys.argv[0]),
            os.path.abspath(self.paths["CONFIG_FILE"]),
            os.path.abspath(self.paths["RULES_FILE"]),
            os.path.abspath(self.paths["LOG_FILE"]),
            os.path.abspath(self.paths["DB_FILE"])
        ]
        if getattr(sys, 'frozen', False):
            exclude_paths.append(os.path.abspath(sys.executable))
        
        if target_name != 'NONE':
            exclude_paths.append(os.path.abspath(os.path.join(source_dir, target_name)))
        
        for cat in self.rules.keys():
            exclude_paths.append(os.path.abspath(os.path.join(source_dir, cat)))
            if target_name != 'NONE':
                exclude_paths.append(os.path.abspath(os.path.join(source_dir, target_name, cat)))

        items_processed = 0
        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            abs_path = os.path.abspath(source_path)
            
            if abs_path in exclude_paths: continue
            if item in self.rules.keys() or item == target_name: continue

            is_dir = os.path.isdir(source_path)
            item_type = "文件夹" if is_dir else "文件"

            category = self.get_category(item, is_dir)
            
            if target_name == 'NONE':
                dest_dir = os.path.join(source_dir, category)
            else:
                dest_dir = os.path.join(source_dir, target_name, category)

            if is_dir and os.path.abspath(dest_dir).startswith(abs_path):
                self.print_log(f"跳过: {item} (目标在源文件夹内部)")
                continue

            if self.dry_run:
                self.print_log(f"[预演] {item_type} '{item}' -> '{category}'")
            else:
                if not os.path.exists(dest_dir): os.makedirs(dest_dir)
                dest_path = self.get_unique_path(dest_dir, item)
                try:
                    shutil.move(source_path, dest_path)
                    self.print_log(f"移动: {item} -> {category}")
                    self.db.log("整理", item_type, item, source_path, dest_path, "SUCCESS")
                    items_processed += 1
                except Exception as e:
                    self.print_log(f"移动失败 {item}: {e}")
                    self.db.log("整理", item_type, item, source_path, dest_path, f"FAIL: {e}")

        self.print_log(f"整理完成，共处理 {items_processed} 个项目。")
        
        # 自动清理旧日志
        retention_count = self.config.getint('SETTINGS', 'LOG_RETENTION_COUNT', fallback=100)
        self.db.cleanup_old_logs(retention_count)
