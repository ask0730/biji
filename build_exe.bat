@echo off
echo 正在打包dengji.py为exe文件...
echo.

REM 检查是否安装了pyinstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装pyinstaller...
    pip install pyinstaller
)

echo.
echo 开始打包...
pyinstaller dengji.spec

echo.
echo 打包完成！
echo exe文件位置: dist\dengji.exe
echo.
echo 请将以下文件放在exe同级目录：
echo   - config.txt
echo   - 导入模版.xls (如果使用Excel功能)
echo.
pause

