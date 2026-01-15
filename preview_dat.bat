@echo off
chcp 65001 >nul
echo 启动炎龙骑士团II DAT文件图像预览工具...
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python。请确保已安装Python并将其添加到PATH环境变量中。
    pause
    exit /b 1
)

REM 检查必要的依赖
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到tkinter库。请确保Python安装包含了tkinter。
    pause
    exit /b 1
)

python -c "from PIL import Image, ImageTk" >nul 2>&1
if errorlevel 1 (
    echo 警告: 未找到PIL库。正在尝试安装...
    python -m pip install pillow
    if errorlevel 1 (
        echo 错误: 无法安装PIL库，请手动运行 'pip install pillow'
        pause
        exit /b 1
    )
)

REM 启动预览工具
echo 启动预览工具...
python preview_gui.py

pause