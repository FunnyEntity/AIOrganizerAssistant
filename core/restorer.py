import os
import shutil
import logging

class Restorer:
    def __init__(self, paths, config, rules, db, log_callback=None):
        self.paths = paths
        self.config = config
        self.rules = rules
        self.db = db
        self.log_callback = log_callback

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

    def run(self):
        self.print_log(f"=== 开始还原 ===")
        exe_dir = self.paths["EXE_DIR"]
        target_name = self.config.get('SETTINGS', 'TARGET_NAME', fallback='归档文件夹')
        folders_to_check = []

        if target_name != 'NONE':
            target_path = os.path.join(exe_dir, target_name)
            if os.path.exists(target_path):
                for item in os.listdir(target_path):
                    path = os.path.join(target_path, item)
                    if os.path.isdir(path): folders_to_check.append(path)
            else:
                for category in self.rules.keys():
                    cat_path = os.path.join(exe_dir, category)
                    if os.path.exists(cat_path): folders_to_check.append(cat_path)
        else:
            for category in self.rules.keys():
                cat_path = os.path.join(exe_dir, category)
                if os.path.exists(cat_path): folders_to_check.append(cat_path)

        if not folders_to_check:
            self.print_log("未发现需要还原的文件夹。")
            return

        items_restored = 0
        for folder_path in folders_to_check:
            self.print_log(f"正在扫描: {os.path.basename(folder_path)}")
            for item in os.listdir(folder_path):
                src_path = os.path.join(folder_path, item)
                is_dir = os.path.isdir(src_path)
                item_type = "文件夹" if is_dir else "文件"
                dest_path = self.get_unique_path(exe_dir, item, "还原")
                try:
                    shutil.move(src_path, dest_path)
                    self.print_log(f"还原: {item}")
                    self.db.log("还原", item_type, item, src_path, dest_path, "SUCCESS")
                    items_restored += 1
                except Exception as e:
                    self.print_log(f"还原失败 {item}: {e}")
                    self.db.log("还原", item_type, item, src_path, dest_path, f"FAIL: {e}")

            try:
                if not os.listdir(folder_path):
                    os.rmdir(folder_path)
            except: pass

        if target_name != 'NONE':
            target_path = os.path.join(exe_dir, target_name)
            if os.path.exists(target_path) and not os.listdir(target_path):
                try: os.rmdir(target_path)
                except: pass

        self.print_log(f"还原完成，共还原 {items_restored} 个项目。")
        
        # 自动清理旧日志
        retention_count = self.config.getint('SETTINGS', 'LOG_RETENTION_COUNT', fallback=100)
        self.db.cleanup_old_logs(retention_count)
