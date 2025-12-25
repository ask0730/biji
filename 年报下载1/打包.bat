@echo off
chcp 65001 >nul
echo ========================================
echo 批量执行脚本打包工具
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python
    pause
    exit /b 1
)

echo 正在检查依赖...
python -m pip install -r requirements.txt

echo.
echo 开始打包...
python build_exe.py

echo.
pause

