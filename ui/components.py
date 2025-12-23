import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

class SettingsPanel(ttk.Frame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.cm = config_manager
        self.config = self.cm.config
        self.rules = self.cm.rules
        self.current_cat = None # 记录当前正在编辑的分类
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: 基础配置
        tab_config = ttk.Frame(notebook)
        notebook.add(tab_config, text="基础配置")
        self.create_config_tab(tab_config)

        # Tab 2: 规则管理
        tab_rules = ttk.Frame(notebook)
        notebook.add(tab_rules, text="规则管理")
        self.create_rules_tab(tab_rules)

        # 底部按钮
        frame_btns = ttk.Frame(self)
        frame_btns.pack(fill="x", padx=10, pady=10)
        
        # 保存按钮在最右侧
        ttk.Button(frame_btns, text="保存所有设置", command=self.save_all).pack(side="right")
        
        # GitHub 链接在按钮左侧
        link_github = tk.Label(
            frame_btns, 
            text="GitHub", 
            fg="blue", 
            cursor="hand2", 
            font=("TkDefaultFont", 9, "underline")
        )
        link_github.pack(side="right", padx=20)
        link_github.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/FunnyEntity/AIOrganizerAssistant"))
        
        # 悬停效果
        link_github.bind("<Enter>", lambda e: link_github.config(fg="darkblue"))
        link_github.bind("<Leave>", lambda e: link_github.config(fg="blue"))

    def create_config_tab(self, parent):
        grid_frame = ttk.Frame(parent, padding=20)
        grid_frame.pack(fill="both", expand=True)
        self.config_entries = {}
        row = 0
        # 配置项列表，包含显示名称和内部键名
        config_items = [
            ("API Key (API_KEY)", "API_KEY"),
            ("API 基础地址 (BASE_URL)", "BASE_URL"),
            ("模型名称 (MODEL)", "MODEL"),
            ("归档文件夹名 (TARGET_NAME)", "TARGET_NAME"),
            ("日志保留数量 (LOG_RETENTION_COUNT)", "LOG_RETENTION_COUNT")
        ]
        
        for label_text, key in config_items:
            ttk.Label(grid_frame, text=label_text + ":").grid(row=row, column=0, sticky="w", pady=5)
            entry = ttk.Entry(grid_frame, width=50)
            entry.grid(row=row, column=1, sticky="w", padx=10)
            
            val = ""
            if 'SETTINGS' in self.config and key in self.config['SETTINGS']:
                val = self.config['SETTINGS'][key]
            elif key == "LOG_RETENTION_COUNT":
                val = "100" # 默认值
                
            entry.insert(0, val)
            self.config_entries[key] = entry
            row += 1
            
        ttk.Label(grid_frame, text="说明: 修改后需重启程序生效。日志保留数量设为 0 则不清理。").grid(row=row+1, column=0, columnspan=2, pady=20)

    def create_rules_tab(self, parent):
        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左侧分类列表 - 固定宽度
        frame_left = ttk.LabelFrame(container, text="分类列表")
        frame_left.pack(side="left", fill="both", expand=False, padx=(0, 5))
        
        scrollbar = ttk.Scrollbar(frame_left)
        scrollbar.pack(side="right", fill="y")
        
        # 设置固定宽度 25，显式设置颜色以防主题干扰
        self.list_cats = tk.Listbox(
            frame_left, 
            yscrollcommand=scrollbar.set, 
            width=25, 
            exportselection=False,
            bg="white",
            fg="black",
            selectbackground="#0078d7"
        )
        self.list_cats.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=self.list_cats.yview)
        self.list_cats.bind("<<ListboxSelect>>", self.on_cat_select)
        
        # 右侧规则编辑 - 自动扩展
        frame_right = ttk.LabelFrame(container, text="规则编辑 (逗号分隔)")
        frame_right.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        self.text_rules = tk.Text(
            frame_right, 
            height=15, 
            width=40, 
            undo=True,
            bg="white",
            fg="black",
            insertbackground="black"
        )
        self.text_rules.pack(fill="both", expand=True, padx=5, pady=5)
        
        frame_tools = ttk.Frame(frame_right)
        frame_tools.pack(fill="x", pady=5, padx=5)
        ttk.Button(frame_tools, text="更新当前分类", command=self.update_current_cat).pack(side="left", fill="x", expand=True)
        ttk.Button(frame_tools, text="删除分类", command=self.delete_cat).pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        frame_add = ttk.LabelFrame(parent, text="新增分类", padding=5)
        frame_add.pack(fill="x", padx=10, pady=5)
        self.entry_new_cat = ttk.Entry(frame_add, width=30)
        self.entry_new_cat.pack(side="left", padx=5)
        ttk.Button(frame_add, text="添加分类", command=self.add_cat).pack(side="left")

        if self.rules:
            for cat in self.rules.keys():
                self.list_cats.insert(tk.END, cat)
            
            if self.list_cats.size() > 0:
                self.list_cats.selection_set(0)
                self.on_cat_select(None)

    def on_cat_select(self, event):
        # 1. 尝试保存上一个分类的修改
        if self.current_cat:
            content = self.text_rules.get("1.0", tk.END).strip()
            content = content.replace('\n', ',')
            rules_list = [r.strip() for r in content.split(',') if r.strip()]
            self.rules[self.current_cat] = rules_list

        # 2. 加载新选中的分类
        selection = self.list_cats.curselection()
        if selection:
            self.current_cat = self.list_cats.get(selection[0])
            rules = self.rules.get(self.current_cat, [])
            self.text_rules.delete("1.0", tk.END)
            self.text_rules.insert("1.0", ", ".join(rules))

    def delete_cat(self):
        selection = self.list_cats.curselection()
        if selection:
            cat = self.list_cats.get(selection[0])
            if messagebox.askyesno("确认", f"确定要删除分类 '{cat}' 吗？"):
                del self.rules[cat]
                self.list_cats.delete(selection[0])
                self.text_rules.delete("1.0", tk.END)

    def add_cat(self):
        new_cat = self.entry_new_cat.get().strip()
        if new_cat:
            if new_cat in self.rules:
                messagebox.showerror("错误", "分类已存在")
                return
            self.rules[new_cat] = []
            self.list_cats.insert(tk.END, new_cat)
            self.entry_new_cat.delete(0, tk.END)

    def save_all(self):
        try:
            # 自动保存当前正在编辑的分类
            self.update_current_cat(show_info=False)
            
            # 保存配置
            settings = {k: v.get().strip() for k, v in self.config_entries.items()}
            self.cm.save_config(settings)
            
            # 保存规则
            self.cm.save_rules(self.rules)
            
            messagebox.showinfo("成功", "设置已保存！")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def update_current_cat(self, show_info=True):
        selection = self.list_cats.curselection()
        if selection:
            cat = self.list_cats.get(selection[0])
            content = self.text_rules.get("1.0", tk.END).strip()
            # 解析规则：支持逗号、换行符分隔
            content = content.replace('\n', ',')
            rules_list = [r.strip() for r in content.split(',') if r.strip()]
            self.rules[cat] = rules_list
            if show_info:
                messagebox.showinfo("提示", f"分类 '{cat}' 已更新")
