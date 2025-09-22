@echo off
chcp 65001
echo ========================================
echo CNKI论文信息抓取工具
echo ========================================
echo.

echo 正在检查Python环境...
python --version
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python
    pause
    exit /b 1
)

echo.
echo 正在安装依赖包...
pip install -r requirements.txt

echo.
echo 开始运行抓取程序...
python RPA/cnki_selenium.py

echo.
echo 程序执行完成！
pause
