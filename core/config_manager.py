import os
import sys
import configparser
import json
import shutil
import logging

# --- 路径与常量定义 ---
def get_paths(target_name_from_config=None):
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    app_data_dir = os.path.join(os.getenv('APPDATA'), 'AIOrganizerHelper')
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)

    return {
        "EXE_DIR": exe_dir,
        "APP_DATA_DIR": app_data_dir,
        "CONFIG_FILE": os.path.join(app_data_dir, "config.ini"),
        "RULES_FILE": os.path.join(app_data_dir, "rules.json"),
        "LOG_FILE": os.path.join(app_data_dir, "system.log"),
        "DB_FILE": os.path.join(app_data_dir, "history.db")
    }

class ConfigManager:
    def __init__(self, paths):
        self.paths = paths
        self.config = self.load_config()
        self.rules = self.load_rules()

    def load_config(self):
        config = configparser.ConfigParser()
        if not os.path.exists(self.paths["CONFIG_FILE"]):
            self.create_default_config()
        config.read(self.paths["CONFIG_FILE"], encoding='utf-8')
        return config

    def create_default_config(self):
        config_content = """[SETTINGS]
API_KEY = 
BASE_URL = https://api.deepseek.com
MODEL = deepseek-chat
TARGET_NAME = 归档文件夹
DRY_RUN = False
LOG_RETENTION_COUNT = 100
"""
        with open(self.paths["CONFIG_FILE"], 'w', encoding='utf-8') as f:
            f.write(config_content)

    def load_rules(self):
        if os.path.exists(self.paths["RULES_FILE"]):
            try:
                with open(self.paths["RULES_FILE"], 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass

        if getattr(sys, 'frozen', False):
            internal_rules_path = os.path.join(sys._MEIPASS, "整理规则.json")
            if os.path.exists(internal_rules_path):
                try:
                    with open(internal_rules_path, 'r', encoding='utf-8') as f:
                        rules = json.load(f)
                    with open(self.paths["RULES_FILE"], 'w', encoding='utf-8') as f_out:
                        json.dump(rules, f_out, ensure_ascii=False, indent=4)
                    return rules
                except: pass

        default_rules = {
            "01_安装程序": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", "Setup", "installer", "Update"],
            "02_安卓应用": [".apk", ".xapk", ".apkm", ".obb"],
            "03_压缩文件": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".z", ".ace"],
            "04_系统镜像": [".iso", ".img", ".vmdk", ".vhd", ".vhdx", ".wim", ".gho"],
            "05_办公文档": [".doc", ".docx", ".pages", ".odt", ".rtf", "简历", "合同", "说明书"],
            "06_电子表格": [".xls", ".xlsx", ".csv", ".numbers", ".ods", "报表", "清单"],
            "07_演示文稿": [".ppt", ".pptx", ".key", ".odp", "课件", "汇报"],
            "08_PDF文档": [".pdf"],
            "09_纯文本": [".txt", ".md", ".log", ".xml", ".json", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".toml"],
            "10_电子书刊": [".epub", ".mobi", ".azw3", ".chm", ".djvu", ".cbr", ".cbz", "漫画", "小说"],
            "11_图片照片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".heic", ".raw", "截图", "照片", "DCIM"],
            "12_设计素材": [".psd", ".ai", ".cdr", ".svg", ".eps", ".sketch", ".fig", ".indd", "素材", "工程"],
            "13_字体文件": [".ttf", ".otf", ".woff", ".woff2", ".eot", ".ttc"],
            "14_音频音乐": [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma", ".ape", "录音", "歌曲"],
            "15_视频影视": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".rmvb", "电影", "剧集", "录屏"],
            "16_源代码": [".py", ".js", ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".ts", ".vue", ".jsx", ".tsx"],
            "17_网页文件": [".html", ".htm", ".css", ".asp", ".aspx", ".jsp"],
            "18_数据库": [".sql", ".db", ".sqlite", ".mdb", ".accdb"],
            "19_游戏文件": [".osz", ".osk", ".minecraft", ".jar", ".pak", ".unitypackage", "Steam", "Epic", "Game", "游戏", "补丁", "Mod", "地图"],
            "20_备份存档": [".bak", ".old", ".tmp", ".swp", ".sav", "backup", "存档"],
            "21_其他杂项": []
        }
        try:
            with open(self.paths["RULES_FILE"], 'w', encoding='utf-8') as f:
                json.dump(default_rules, f, ensure_ascii=False, indent=4)
        except: pass
        return default_rules

    def save_config(self, settings_dict):
        if 'SETTINGS' not in self.config:
            self.config['SETTINGS'] = {}
        for k, v in settings_dict.items():
            self.config['SETTINGS'][k] = str(v)
        with open(self.paths["CONFIG_FILE"], 'w', encoding='utf-8') as f:
            self.config.write(f)

    def save_rules(self, rules_dict):
        try:
            with open(self.paths["RULES_FILE"], 'w', encoding='utf-8') as f:
                json.dump(rules_dict, f, ensure_ascii=False, indent=4)
            # 同步更新内存中的 rules
            self.rules = rules_dict
        except Exception as e:
            logging.error(f"保存规则文件失败: {e}")
            raise e

def migrate_old_data(paths):
    old_files = {
        "整理工具配置.ini": paths["CONFIG_FILE"],
        "整理规则.json": paths["RULES_FILE"],
        "整理记录.db": paths["DB_FILE"]
    }
    for old_name, new_path in old_files.items():
        old_path = os.path.join(paths["EXE_DIR"], old_name)
        if os.path.exists(old_path):
            try:
                if not os.path.exists(new_path):
                    shutil.move(old_path, new_path)
                else:
                    os.rename(old_path, old_path + ".bak")
            except: pass
