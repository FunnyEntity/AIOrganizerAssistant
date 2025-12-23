# AIOrganizerAssistant (AI Organizer Assistant)

🚀 **AIOrganizerAssistant** 是一款基于人工智能的文件自动化分类工具。它能够智能识别文件类型与内容，将您散乱的桌面、下载文件夹或任何目录瞬间变得井井有条。

---

## ✨ 主要功能

- 🖥️ **双模式运行**：支持图形界面 (GUI) 和命令行 (CLI) 两种使用方式。
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
- 🎨 **现代化集成界面**：采用标签页布局，将"整理控制"与"高级设置"完美融合，操作直观便捷。

---

## 🚀 快速开始

### 1. 获取并运行

#### GUI 模式（图形界面）
- **直接运行**：下载发布的 `AIOrganizerAssistant.exe`，双击即可启动图形界面。
- **源码运行**：
  ```bash
  git clone https://github.com/FunnyEntity/AIOrganizerAssistant.git
  cd AIOrganizerAssistant
  pip install -r requirements.txt
  python main.py
  ```

#### CLI 模式（命令行）
```bash
# 执行整理
AIOrganizerAssistant.exe --action organize

# 预演模式整理（不实际移动文件）
AIOrganizerAssistant.exe --action organize --dry-run

# 执行还原
AIOrganizerAssistant.exe --action restore

# 指定 API 密钥（优先级高于配置文件）
AIOrganizerAssistant.exe --action organize --api-key YOUR_API_KEY

# 指定要整理的源目录
AIOrganizerAssistant.exe --action organize --source-dir "C:\Downloads"
```

> **CLI 模式说明**：当以命令行参数启动时，程序会自动使用 CLI 模式。

### 2. 配置 AI (可选但推荐)
1. 点击 **"高级设置"** 标签页。
2. 在 **"基础配置"** 中填写您的 `API_KEY`（推荐使用 DeepSeek API）。
3. 点击 **"保存所有设置"**。

### 3. 开始整理
1. 回到 **"整理控制"** 标签页。
2. (可选) 勾选 **"预演模式"** 进行测试。
3. 点击 **"开始整理"**，静候 AI 为您效劳。

---

## 🛠️ 技术栈

- **语言**：Python 3.x
- **界面**：Tkinter (ttk)
- **AI 引擎**：DeepSeek API (兼容 OpenAI 格式)
- **数据库**：SQLite3
- **打包**：PyInstaller
- **设计模式**：策略模式（用于文件分类）

---

## 📂 项目结构

- `main.py`: 程序入口，支持 GUI 和 CLI 两种模式。
- `core/`:
  - `app_core.py`: 核心业务逻辑封装（AppCore 类）。
  - `ai_client.py`: AI 客户端。
  - `config_manager.py`: 配置管理器。
  - `db_manager.py`: 数据库管理器。
  - `organizer.py`: 文件整理器（支持策略模式）。
  - `restorer.py`: 文件还原器。
- `ui/`: 界面组件模块。
- `resources/`: 资源文件夹。
  - `myicon.ico`: 程序图标。
- `pack.bat`: 一键打包脚本。

---

## 🔧 打包说明

运行 `pack.bat` 即可自动打包为单文件 EXE。打包后的文件名为 `AIOrganizerAssistant.exe`。

**打包依赖**：
- Python 3.x
- openai
- pyinstaller

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
