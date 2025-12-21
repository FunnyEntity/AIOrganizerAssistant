import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# 导入自定义模块
from core.config_manager import get_paths, ConfigManager, migrate_old_data
from core.db_manager import DBManager
from core.organizer import Organizer
from core.restorer import Restorer
from ui.components import SettingsPanel

# ==================== 用户配置区域 ====================
# API 设置
DEFAULT_API_KEY = ""                           # 留空则使用配置文件中的值
DEFAULT_BASE_URL = "https://api.deepseek.com"  # API 基础地址
DEFAULT_MODEL = "deepseek-chat"                # 使用的模型

# 整理行为
DEFAULT_TARGET_NAME = "归档文件夹"             # 总文件夹名称，填 "NONE" 则散放
DEFAULT_DRY_RUN = False                        # 预演模式（只显示不移动）

# 界面配置
WINDOW_TITLE = "AI整理助手"
WINDOW_SIZE = "750x650"
# ======================================================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # 初始化路径与数据迁移
        self.paths = get_paths()
        
        # 设置窗口图标
        try:
            # 尝试多种路径定位图标
            icon_candidates = [
                os.path.join(self.paths["EXE_DIR"], "myicon.ico"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "myicon.ico"),
                "myicon.ico"
            ]
            for icon_path in icon_candidates:
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    break
        except Exception as e:
            print(f"无法加载图标: {e}")

        migrate_old_data(self.paths)
        
        # 初始化管理器
        self.cm = ConfigManager(self.paths)
        self.db = DBManager(self.paths["DB_FILE"], self.paths["EXE_DIR"])
        
        self.create_widgets()
        
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # --- 标签页 1: 整理控制 ---
        self.tab_control = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_control, text="整理控制")

        # 1. 配置区域
        frame_config = ttk.LabelFrame(self.tab_control, text="快捷设置", padding=10)
        frame_config.pack(fill="x", padx=10, pady=5)
        
        self.var_dry_run = tk.BooleanVar()
        dry_run = DEFAULT_DRY_RUN or self.cm.config.getboolean('SETTINGS', 'DRY_RUN', fallback=False)
        self.var_dry_run.set(dry_run)
            
        ttk.Checkbutton(frame_config, text="预演模式 (只打印不移动)", variable=self.var_dry_run).grid(row=0, column=0, sticky="w", pady=5)

        # 2. 操作区域
        frame_action = ttk.Frame(self.tab_control, padding=10)
        frame_action.pack(fill="x", padx=10)
        
        self.btn_organize = ttk.Button(frame_action, text="开始整理", command=self.start_organize)
        self.btn_organize.pack(side="left", fill="x", expand=True, padx=5)
        
        self.btn_restore = ttk.Button(frame_action, text="一键还原", command=self.start_restore)
        self.btn_restore.pack(side="left", fill="x", expand=True, padx=5)
        
        self.btn_export = ttk.Button(frame_action, text="导出日志", command=self.export_log)
        self.btn_export.pack(side="left", fill="x", expand=True, padx=5)

        # 3. 日志区域
        frame_log = ttk.LabelFrame(self.tab_control, text="运行日志", padding=10)
        frame_log.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.text_log = scrolledtext.ScrolledText(frame_log, height=20, state='disabled')
        self.text_log.pack(fill="both", expand=True)

        # --- 标签页 2: 高级设置 ---
        self.tab_settings = SettingsPanel(self.notebook, self.cm)
        self.notebook.add(self.tab_settings, text="高级设置")

    def log(self, message):
        self.text_log.config(state='normal')
        self.text_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.text_log.see(tk.END)
        self.text_log.config(state='disabled')

    def toggle_buttons(self, state):
        for btn in [self.btn_organize, self.btn_restore, self.btn_export]:
            btn.config(state=state)

    def start_organize(self):
        # 从配置中读取 API Key
        api_key = self.cm.config.get('SETTINGS', 'API_KEY', fallback='').strip()
        dry_run = self.var_dry_run.get()
        self.toggle_buttons("disabled")
        self.log("正在启动整理任务...")
        
        # 确保使用最新的规则
        self.cm.rules = self.cm.load_rules()
        
        def task():
            try:
                organizer = Organizer(
                    paths=self.paths,
                    config=self.cm.config,
                    rules=self.cm.rules,
                    db=self.db,
                    log_callback=self.log,
                    api_key=api_key,
                    dry_run=dry_run
                )
                organizer.run()
            except Exception as e:
                self.log(f"错误: {e}")
            finally:
                self.root.after(0, lambda: self.toggle_buttons("normal"))
        threading.Thread(target=task, daemon=True).start()

    def start_restore(self):
        self.toggle_buttons("disabled")
        self.log("正在启动还原任务...")
        def task():
            try:
                restorer = Restorer(
                    paths=self.paths,
                    config=self.cm.config,
                    rules=self.cm.rules,
                    db=self.db,
                    log_callback=self.log
                )
                restorer.run()
            except Exception as e:
                self.log(f"错误: {e}")
            finally:
                self.root.after(0, lambda: self.toggle_buttons("normal"))
        threading.Thread(target=task, daemon=True).start()

    def export_log(self):
        path = self.db.export_csv()
        if path:
            messagebox.showinfo("导出成功", f"日志已导出至:\n{path}")
        else:
            messagebox.showerror("导出失败", "导出日志时发生错误")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
