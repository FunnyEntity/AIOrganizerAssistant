"""
Organizer - 文件整理核心模块
支持多种分类策略，便于扩展
"""
import os
import shutil
import sys
import logging
from abc import ABC, abstractmethod
from .ai_client import AIClient


class ClassificationStrategy(ABC):
    """分类策略抽象基类"""
    
    @abstractmethod
    def classify(self, filename: str, rules: dict, is_dir: bool = False) -> str:
        """
        对文件/文件夹进行分类
        
        Args:
            filename: 文件名
            rules: 分类规则字典
            is_dir: 是否为文件夹
            
        Returns:
            分类名称，无法分类返回 None
        """
        pass


class ExtensionStrategy(ClassificationStrategy):
    """扩展名匹配策略"""
    
    def classify(self, filename: str, rules: dict, is_dir: bool = False) -> str:
        """通过文件扩展名进行分类"""
        if is_dir:
            return None
            
        ext = os.path.splitext(filename)[1].lower()
        for category, patterns in rules.items():
            if ext in patterns:
                return category
        return None


class KeywordStrategy(ClassificationStrategy):
    """关键词匹配策略"""
    
    def classify(self, filename: str, rules: dict, is_dir: bool = False) -> str:
        """通过文件名中的关键词进行分类"""
        for category, patterns in rules.items():
            for pattern in patterns:
                if pattern.lower() in filename.lower():
                    return category
        return None


class AIStrategy(ClassificationStrategy):
    """AI 分类策略"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        
    def classify(self, filename: str, rules: dict, is_dir: bool = False) -> str:
        """通过 AI 进行分类"""
        if not self.ai_client:
            return None
            
        ai_cat = self.ai_client.ask_ai(filename, rules.keys(), is_dir)
        return ai_cat


class DefaultStrategy(ClassificationStrategy):
    """默认分类策略（兜底）"""
    
    DEFAULT_CATEGORY = "21_其他杂项"
    
    def classify(self, filename: str, rules: dict, is_dir: bool = False) -> str:
        """返回默认分类"""
        return self.DEFAULT_CATEGORY


class Organizer:
    """文件整理器 - 支持多种分类策略"""
    
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
        
        # 初始化分类策略链（按优先级顺序）
        self.strategies = [
            ExtensionStrategy(),      # 1. 扩展名匹配
            KeywordStrategy(),        # 2. 关键词匹配
            AIStrategy(self.ai_client),  # 3. AI 识别
            DefaultStrategy()         # 4. 默认分类
        ]
    
    def print_log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def get_unique_path(self, dest_dir, filename, suffix=""):
        """生成唯一的目标路径，处理重名冲突"""
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
        """
        使用策略链获取文件分类
        
        Args:
            filename: 文件名
            is_dir: 是否为文件夹
            
        Returns:
            分类名称
        """
        # 依次尝试各个策略，返回第一个匹配的结果
        for strategy in self.strategies:
            category = strategy.classify(filename, self.rules, is_dir)
            if category:
                return category
        
        # 所有策略都失败，返回默认值
        return DefaultStrategy.DEFAULT_CATEGORY

    def add_strategy(self, strategy: ClassificationStrategy, position: int = -1):
        """
        添加新的分类策略
        
        Args:
            strategy: 分类策略实例
            position: 插入位置，-1 表示添加到末尾（在默认策略之前）
        """
        if position < 0 or position >= len(self.strategies):
            # 添加到默认策略之前
            self.strategies.insert(len(self.strategies) - 1, strategy)
        else:
            self.strategies.insert(position, strategy)

    def run(self):
        """执行整理任务"""
        source_dir = self.paths["EXE_DIR"]
        target_name = self.config.get('SETTINGS', 'TARGET_NAME', fallback='归档文件夹')
        
        self.print_log(f"=== 开始整理 ===")
        self.print_log(f"工作目录: {source_dir}")
        if self.dry_run: 
            self.print_log("--- 预演模式 ---")

        # 构建排除路径列表
        exclude_paths = [
            os.path.abspath(sys.argv[0]),
            os.path.abspath(self.paths["CONFIG_FILE"]),
            os.path.abspath(self.paths["RULES_FILE"]),
            os.path.abspath(self.paths["LOG_FILE"]),
            os.path.abspath(self.paths["DB_FILE"])
        ]
        if getattr(sys, 'frozen', False):
            exclude_paths.append(os.path.abspath(sys.executable))
        
        # 排除归档文件夹及其子目录
        if target_name != 'NONE':
            exclude_paths.append(os.path.abspath(os.path.join(source_dir, target_name)))
        
        for cat in self.rules.keys():
            exclude_paths.append(os.path.abspath(os.path.join(source_dir, cat)))
            if target_name != 'NONE':
                exclude_paths.append(os.path.abspath(os.path.join(source_dir, target_name, cat)))

        # 遍历并处理文件/文件夹
        items_processed = 0
        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            abs_path = os.path.abspath(source_path)
            
            # 跳过排除的路径
            if abs_path in exclude_paths: 
                continue
            if item in self.rules.keys() or item == target_name: 
                continue

            is_dir = os.path.isdir(source_path)
            item_type = "文件夹" if is_dir else "文件"

            # 获取分类
            category = self.get_category(item, is_dir)
            
            # 确定目标目录
            if target_name == 'NONE':
                dest_dir = os.path.join(source_dir, category)
            else:
                dest_dir = os.path.join(source_dir, target_name, category)

            # 防止循环移动（目标目录在源目录内部）
            if is_dir and os.path.abspath(dest_dir).startswith(abs_path):
                self.print_log(f"跳过: {item} (目标在源文件夹内部)")
                continue

            # 执行移动或预演
            if self.dry_run:
                self.print_log(f"[预演] {item_type} '{item}' -> '{category}'")
            else:
                # 确保目标目录存在
                if not os.path.exists(dest_dir): 
                    os.makedirs(dest_dir)
                # 获取唯一目标路径
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
