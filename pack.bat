@echo off
chcp 65001 >nul
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv_pack"

echo [1/5] 检查虚拟环境...
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo    创建虚拟环境...
    python -m venv "%VENV_DIR%"
)

echo [2/5] 安装依赖...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install openai pyinstaller --quiet

echo [3/5] 开始打包 (请耐心等待)...
if not exist "build" mkdir build
pyinstaller --clean --onefile --noconsole --icon=resources/myicon.ico --add-data "resources/myicon.ico;resources" --name "AIOrganizerAssistant" --workpath "./build" --distpath "./dist" --exclude torch --exclude numpy --exclude pandas --exclude scipy --exclude matplotlib --exclude jupyter --exclude notebook main.py

if exist "dist\AIOrganizerAssistant.exe" (
    echo [4/5] 整理文件...
    if exist "AIOrganizerAssistant.exe" del /f /q "AIOrganizerAssistant.exe"
    move /Y "dist\AIOrganizerAssistant.exe" "."
    rd /s /q build dist 2>nul
    del /f /q "AIOrganizerAssistant.spec" 2>nul
    echo [5/5] 完成！新的可执行文件: AIOrganizerAssistant.exe
) else (
    echo [错误] 打包失败，请检查上方错误信息。
)
pause
