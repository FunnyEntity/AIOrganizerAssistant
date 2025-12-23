#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIOrganizerAssistant - AI文件整理助手
支持 GUI 和 CLI 两种运行模式
"""
import os
import sys
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import Optional

# 跨平台控制台窗口处理
try:
    import ctypes
    from ctypes import wintypes
    
    # Windows API 定义
    kernel32 = ctypes.windll.kernel32
    
    def attach_console():
        """
        尝试挂载到父进程的控制台（仅 Windows）
        当从命令行启动时，输出会显示在父进程的窗口中
        当双击启动时，不会显示控制台窗口
        """
        try:
            if sys.platform == 'win32':
                # ATTACH_PARENT_PROCESS = -1
                if kernel32.AttachConsole(-1):
                    # 重新初始化标准输出/错误流，使其指向控制台
                    sys.stdout = open("CONOUT$", "w", encoding='utf-8')
                    sys.stderr = open("CONOUT$", "w", encoding='utf-8')
        except:
            pass
    
    def get_icon_path() -> Optional[str]:
        """获取图标文件路径"""
        # 1. PyInstaller 打包后的临时目录
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            icon_path = os.path.join(base_path, 'resources', 'myicon.ico')
            if os.path.exists(icon_path):
                return icon_path
        
        # 2. 源码运行时的相对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'resources', 'myicon.ico')
        if os.path.exists(icon_path):
            return icon_path
        
        # 3. 当前目录
        icon_path = os.path.join(os.getcwd(), 'myicon.ico')
        if os.path.exists(icon_path):
            return icon_path
        
        return None
    
except ImportError:
    # 非 Windows 平台的兼容处理
    def attach_console():
        """非 Windows 平台无需特殊处理"""
        pass
    
    def get_icon_path():
        """获取图标文件路径"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'resources', 'myicon.ico')
        if os.path.exists(icon_path):
            return icon_path
        icon_path = os.path.join(os.getcwd(), 'myicon.ico')
        if os.path.exists(icon_path):
            return icon_path
        return None

# 导入自定义模块
from core.app_core import AppCore
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
    """GUI 应用程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # 初始化 AppCore
        self.core = AppCore(log_callback=self.log)
        
        # 设置窗口图标
        try:
            icon_path = get_icon_path()
            if icon_path:
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"无法加载图标: {e}")

        self.create_widgets()
        
        # 窗口关闭时清理资源
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
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
        dry_run = DEFAULT_DRY_RUN or self.core.cm.config.getboolean('SETTINGS', 'DRY_RUN', fallback=False)
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
        self.tab_settings = SettingsPanel(self.notebook, self.core.cm)
        self.notebook.add(self.tab_settings, text="高级设置")

    def log(self, message):
        """GUI 日志回调"""
        self.text_log.config(state='normal')
        time_str = datetime.now().strftime('%H:%M:%S')
        self.text_log.insert(tk.END, f"[{time_str}] {message}\n")
        self.text_log.see(tk.END)
        self.text_log.config(state='disabled')

    def toggle_buttons(self, state):
        for btn in [self.btn_organize, self.btn_restore, self.btn_export]:
            btn.config(state=state)

    def start_organize(self):
        dry_run = self.var_dry_run.get()
        self.toggle_buttons("disabled")
        self.log("正在启动整理任务...")
        
        def task():
            result = self.core.run_organize(dry_run=dry_run)
            self.root.after(0, lambda: self.toggle_buttons("normal"))
            if not result['success']:
                self.log(f"错误: {result['message']}")
                
        import threading
        threading.Thread(target=task, daemon=True).start()

    def start_restore(self):
        self.toggle_buttons("disabled")
        self.log("正在启动还原任务...")
        def task():
            result = self.core.run_restore()
            self.root.after(0, lambda: self.toggle_buttons("normal"))
            if not result['success']:
                self.log(f"错误: {result['message']}")
                
        import threading
        threading.Thread(target=task, daemon=True).start()

    def export_log(self):
        path = self.core.export_log()
        if path:
            messagebox.showinfo("导出成功", f"日志已导出至:\n{path}")
        else:
            messagebox.showerror("导出失败", "导出日志时发生错误")

    def on_close(self):
        """窗口关闭时的清理"""
        self.core.close()
        self.root.destroy()


def run_cli():
    """命令行模式"""
    # 尝试挂载到父进程的控制台（仅 Windows）
    attach_console()
    
    parser = argparse.ArgumentParser(
        description='AI文件整理助手 - 命令行版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --action organize              # 执行整理
  %(prog)s --action organize --dry-run    # 预演模式整理
  %(prog)s --action restore               # 执行还原
  %(prog)s --action organize --api-key YOUR_KEY  # 指定API密钥
        """
    )
    
    parser.add_argument(
        '--action',
        choices=['organize', 'restore'],
        help='要执行的操作: organize(整理) 或 restore(还原)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预演模式（只显示不移动文件）'
    )
    parser.add_argument(
        '--api-key',
        help='临时指定API密钥（优先级高于配置文件）'
    )
    parser.add_argument(
        '--source-dir',
        help='指定要整理的源目录（默认为EXE所在目录）'
    )
    
    args = parser.parse_args()
    
    # 如果没有指定 action，显示帮助信息
    if not args.action:
        parser.print_help()
        return
    
    # CLI 日志回调函数（直接打印到控制台）
    def cli_log(message):
        time_str = datetime.now().strftime('%H:%M:%S')
        print(f"[{time_str}] {message}")
    
    # 初始化 AppCore
    core = AppCore(log_callback=cli_log)
    
    try:
        # 根据参数执行对应操作
        if args.action == 'organize':
            result = core.run_organize(
                api_key=args.api_key,
                dry_run=args.dry_run,
                source_dir=args.source_dir
            )
        elif args.action == 'restore':
            result = core.run_restore(source_dir=args.source_dir)
        else:
            result = {'success': False, 'message': '未知的操作'}
        
        # 输出最终结果
        if result['success']:
            print(f"\n✓ {result['message']}")
            sys.exit(0)
        else:
            print(f"\n✗ {result['message']}")
            sys.exit(1)
    finally:
        core.close()


def run_gui():
    """图形界面模式"""
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    # 检测是否有命令行参数
    # 特殊处理：PyInstaller 打包后的第一个参数可能是脚本路径
    if len(sys.argv) > 1 and (not sys.argv[0].endswith('main.py') or sys.argv[1] in ['--help', '-h', '--action']):
        # 有参数，运行 CLI 模式
        run_cli()
    else:
        # 无参数，运行 GUI 模式
        run_gui()
