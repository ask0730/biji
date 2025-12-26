@echo off
chcp 65001 >nul
echo ========================================
echo 文件整理.py 打包工具
echo ========================================
echo.

REM 检查是否安装了PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 安装PyInstaller失败，请手动运行: pip install pyinstaller
        pause
        exit /b 1
    )
)

echo.
echo 开始打包...
echo.

REM 使用PyInstaller打包
pyinstaller --onefile ^
    --name "文件整理" ^
    --icon=NONE ^
    --add-data "输出路径配置.txt;." ^
    --hidden-import pandas ^
    --hidden-import openpyxl ^
    --hidden-import xlrd ^
    --collect-all pandas ^
    --collect-all openpyxl ^
    "文件整理.py"

if errorlevel 1 (
    echo.
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo 可执行文件位置: dist\文件整理.exe
echo ========================================
echo.
echo 提示：
echo 1. 将 dist\文件整理.exe 复制到需要使用的目录
echo 2. 确保同目录下有"输出路径配置.txt"配置文件
echo 3. 确保同目录下有万方和知网的数据文件
echo.
pause

