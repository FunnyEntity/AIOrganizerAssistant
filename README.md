# AI整理助手 (AI Organizer Assistant)

🚀 **AI整理助手** 是一款基于人工智能的文件自动化分类工具。它能够智能识别文件类型与内容，将您散乱的桌面、下载文件夹或任何目录瞬间变得井井有条。

---

## ✨ 主要功能

- 🤖 **智能分类识别**：结合文件扩展名、关键词匹配以及强大的 **DeepSeek AI** 识别技术，精准判断文件所属类别。
- 🔍 **预演模式 (Dry Run)**：在实际移动文件前进行模拟运行，通过日志预览整理结果，确保万无一失。
- ⏪ **一键还原**：整理后悔了？只需点击一下，即可将所有已移动的文件撤回至原始位置。
- ⚙️ **高度可自定义**：
  - **规则管理**：自由编辑分类规则，支持扩展名和关键词自定义。
  - **灵活配置**：在软件内直接配置 API Key、模型名称、目标文件夹名等。
- 📊 **操作日志管理**：
  - 自动记录所有移动/还原操作。
  - 支持将历史记录导出为 CSV 文件。
  - **自动清理**：可设置日志保留数量，防止数据库无限膨胀。
- 🎨 **现代化集成界面**：采用标签页布局，将“整理控制”与“高级设置”完美融合，操作直观便捷。

---

## 🚀 快速开始

### 1. 获取并运行
- **直接运行**：下载发布的 `AI整理助手.exe`，双击即可启动。
- **源码运行**：
  ```bash
  git clone https://github.com/FunnyEntity/AIOrganizerAssistant.git
  cd AI整理助手
  pip install -r requirements.txt
  python main.py
  ```

### 2. 配置 AI (可选但推荐)
1. 点击 **“高级设置”** 标签页。
2. 在 **“基础配置”** 中填写您的 `API_KEY`（推荐使用 DeepSeek API）。
3. 点击 **“保存所有设置”**。

### 3. 开始整理
1. 回到 **“整理控制”** 标签页。
2. (可选) 勾选 **“预演模式”** 进行测试。
3. 点击 **“开始整理”**，静候 AI 为您效劳。

---

## 🛠️ 技术栈

- **语言**：Python 3.x
- **界面**：Tkinter (ttk)
- **AI 引擎**：DeepSeek API (兼容 OpenAI 格式)
- **数据库**：SQLite3
- **打包**：PyInstaller

---

## 📂 项目结构

- `main.py`: 程序入口，负责 GUI 逻辑。
- `core/`: 核心逻辑模块（AI 客户端、数据库管理、整理/还原引擎、配置管理）。
- `ui/`: 界面组件模块。
- `myicon.ico`: 程序图标。
- `pack.bat`: 一键打包脚本。

---

## 🤝 贡献与支持

如果您在使用过程中遇到问题，或有更好的建议，欢迎通过以下方式参与：
- 提交 [Issue](https://github.com/FunnyEntity/AIOrganizerAssistant/issues)
- 提交 Pull Request
- 访问项目主页：[GitHub 仓库](https://github.com/FunnyEntity/AIOrganizerAssistant)

---

## 📄 许可证

本项目采用 **[Apache-2.0 License](LICENSE)** 许可证开源。

---
