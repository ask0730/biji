@echo off
chcp 65001 >nul
echo ========================================
echo 学术研究脚本完整打包工具
echo （无Python环境版本）
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
if exist "知网数据.spec" del /q "知网数据.spec"
if exist "万方数据.spec" del /q "万方数据.spec"
if exist "文件整理.spec" del /q "文件整理.spec"

echo.
echo [信息] 开始打包所有脚本为exe...
echo.

REM 执行Python打包脚本
python build_all_exe.py

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
echo [信息] 所有exe文件位于: dist 目录
echo.
echo [部署说明]
echo   1. 将 dist 目录中的所有文件复制到目标电脑
echo   2. 目标电脑无需安装Python环境
echo   3. 双击 执行脚本.exe 即可运行
echo.
echo [注意] 知网数据和万方数据脚本需要Chrome浏览器
echo.

pause

