"""
AIOrganizerAssistant - 核心业务逻辑封装
将配置管理、数据库操作、整理与还原逻辑封装在一起，便于 CLI 和 GUI 共享
"""
import logging
from typing import Callable, Optional, Dict, Any
from datetime import datetime

from .config_manager import ConfigManager, get_paths, migrate_old_data
from .db_manager import DBManager
from .organizer import Organizer
from .restorer import Restorer


class AppCore:
    """应用程序核心逻辑控制器"""
    
    def __init__(self, paths: Optional[Dict[str, str]] = None, log_callback: Optional[Callable[[str], None]] = None):
        """
        初始化应用核心
        
        Args:
            paths: 路径字典，如不提供则自动生成
            log_callback: 日志回调函数
        """
        self.log_callback = log_callback
        self._setup_paths(paths)
        self._setup_managers()
        
    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        
        if self.log_callback:
            self.log_callback(message)
        else:
            print(log_message)
            
    def _setup_paths(self, paths: Optional[Dict[str, str]]):
        """设置应用路径"""
        if paths is None:
            self.paths = get_paths()
            migrate_old_data(self.paths)
        else:
            self.paths = paths
            
    def _setup_managers(self):
        """初始化各类管理器"""
        self.cm = ConfigManager(self.paths)
        self.db = DBManager(self.paths["DB_FILE"], self.paths["EXE_DIR"])
        
    def reload_config(self):
        """重新加载配置和规则"""
        self.cm.config = self.cm.load_config()
        self.cm.rules = self.cm.load_rules()
        self._log("配置已重新加载")
        
    def run_organize(self, 
                     api_key: Optional[str] = None, 
                     dry_run: bool = False,
                     source_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        执行整理任务
        
        Args:
            api_key: API 密钥，如不提供则使用配置文件中的值
            dry_run: 预演模式
            source_dir: 源目录，如不提供则使用 EXE_DIR
            
        Returns:
            执行结果字典，包含状态和统计信息
        """
        result = {
            'success': False,
            'message': '',
            'items_processed': 0
        }
        
        try:
            # 确保使用最新的规则
            self.reload_config()
            
            # 获取 API Key
            api_key = api_key if api_key else self.cm.config.get('SETTINGS', 'API_KEY', fallback='').strip()
            
            # 创建 Organizer 实例
            organizer = Organizer(
                paths=self.paths,
                config=self.cm.config,
                rules=self.cm.rules,
                db=self.db,
                log_callback=self.log_callback,
                api_key=api_key,
                dry_run=dry_run
            )
            
            # 如果指定了源目录，覆盖默认值
            if source_dir:
                import os
                original_exe_dir = self.paths["EXE_DIR"]
                self.paths["EXE_DIR"] = source_dir
            
            # 执行整理
            self._log("=== 开始整理 ===")
            self._log(f"工作目录: {self.paths['EXE_DIR']}")
            if dry_run:
                self._log("--- 预演模式 ---")
            
            organizer.run()
            
            # 恢复原始路径
            if source_dir:
                self.paths["EXE_DIR"] = original_exe_dir
                
            result['success'] = True
            result['message'] = '整理完成'
            
        except Exception as e:
            error_msg = f"整理任务失败: {e}"
            self._log(error_msg)
            result['message'] = error_msg
            logging.error(error_msg, exc_info=True)
            
        return result
        
    def run_restore(self, source_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        执行还原任务
        
        Args:
            source_dir: 源目录，如不提供则使用 EXE_DIR
            
        Returns:
            执行结果字典，包含状态和统计信息
        """
        result = {
            'success': False,
            'message': '',
            'items_restored': 0
        }
        
        try:
            # 如果指定了源目录，覆盖默认值
            if source_dir:
                original_exe_dir = self.paths["EXE_DIR"]
                self.paths["EXE_DIR"] = source_dir
            
            # 创建 Restorer 实例
            restorer = Restorer(
                paths=self.paths,
                config=self.cm.config,
                rules=self.cm.rules,
                db=self.db,
                log_callback=self.log_callback
            )
            
            # 执行还原
            self._log("=== 开始还原 ===")
            restorer.run()
            
            # 恢复原始路径
            if source_dir:
                self.paths["EXE_DIR"] = original_exe_dir
                
            result['success'] = True
            result['message'] = '还原完成'
            
        except Exception as e:
            error_msg = f"还原任务失败: {e}"
            self._log(error_msg)
            result['message'] = error_msg
            logging.error(error_msg, exc_info=True)
            
        return result
        
    def export_log(self) -> Optional[str]:
        """
        导出日志为 CSV
        
        Returns:
            导出文件的路径，失败返回 None
        """
        return self.db.export_csv()
        
    def save_config(self, settings_dict: Dict[str, Any]) -> bool:
        """
        保存配置
        
        Args:
            settings_dict: 配置字典
            
        Returns:
            是否保存成功
        """
        try:
            self.cm.save_config(settings_dict)
            self._log("配置已保存")
            return True
        except Exception as e:
            self._log(f"保存配置失败: {e}")
            return False
            
    def save_rules(self, rules_dict: Dict[str, Any]) -> bool:
        """
        保存规则
        
        Args:
            rules_dict: 规则字典
            
        Returns:
            是否保存成功
        """
        try:
            self.cm.save_rules(rules_dict)
            self._log("规则已保存")
            return True
        except Exception as e:
            self._log(f"保存规则失败: {e}")
            return False
            
    def close(self):
        """关闭数据库连接"""
        self.db.close()
        self._log("应用已关闭")
