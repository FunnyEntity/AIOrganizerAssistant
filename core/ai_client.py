from openai import OpenAI
import logging

class AIClient:
    def __init__(self, api_key, base_url, model, log_callback=None):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.log_callback = log_callback
        self.client = None
        self.init_client()

    def init_client(self):
        if self.api_key and self.api_key != "在此处填入你的 API_KEY":
            try:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                if self.log_callback:
                    self.log_callback("AI 客户端初始化成功")
            except Exception as e:
                logging.error(f"AI 客户端初始化失败: {e}")

    def ask_ai(self, filename, rules_keys, is_dir=False):
        if not self.client:
            return None
            
        type_str = "文件夹" if is_dir else "文件"
        if self.log_callback:
            self.log_callback(f"正在请求 AI 识别: {filename} ...")
            
        categories = ", ".join(rules_keys)
        prompt = f"请将{type_str} '{filename}' 归类到以下类别之一：[{categories}]。只返回类别名称。"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                timeout=10
            )
            result = response.choices[0].message.content.strip()
            for cat in rules_keys:
                if cat in result:
                    return cat
        except Exception as e:
            logging.error(f"AI 调用失败: {e}")
            if self.log_callback:
                self.log_callback(f"AI 调用失败: {e}")
        return None
