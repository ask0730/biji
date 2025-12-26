@echo off
chcp 65001 >nul
echo ========================================
echo 学术研究脚本打包工具
echo ========================================
echo.

REM 检查PyInstaller是否安装
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [错误] 未找到PyInstaller，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller安装失败，请手动安装: pip install pyinstaller
        pause
        exit /b 1
    )
)

echo [信息] PyInstaller已安装
echo.

REM 清理之前的构建文件
echo [信息] 清理之前的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "执行脚本.spec" del /q "执行脚本.spec"

echo.
echo [信息] 开始打包执行脚本.py为exe...
echo.

REM 使用PyInstaller打包
pyinstaller --name="执行脚本" ^
    --onefile ^
    --console ^
    --icon=NONE ^
    --add-data "config.txt;." ^
    --hidden-import=io ^
    --hidden-import=threading ^
    --hidden-import=subprocess ^
    --hidden-import=ctypes ^
    --clean ^
    "执行脚本.py"

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo [信息] exe文件位置: dist\执行脚本.exe
echo.
echo [提示] 请确保以下文件与exe在同一目录：
echo   - 知网数据.py
echo   - 万方数据.py
echo   - 文件整理.py
echo   - config.txt
echo.
echo [提示] 目标电脑需要安装Python环境才能运行py脚本
echo.

pause

