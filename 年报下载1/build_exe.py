# -*- coding: utf-8 -*-
"""
打包脚本：将批量执行.py打包成exe文件
使用方法：python build_exe.py
"""

import os
import sys
import subprocess

def check_pyinstaller():
    """检查是否安装了PyInstaller"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("✓ PyInstaller安装成功")
        return True
    except Exception as e:
        print(f"✗ PyInstaller安装失败: {e}")
        return False

def build_exe():
    """打包exe文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_file = os.path.join(script_dir, '批量执行.py')
    
    if not os.path.exists(script_file):
        print(f"✗ 找不到脚本文件: {script_file}")
        return False
    
    print("=" * 60)
    print("开始打包exe文件...")
    print("=" * 60)
    
    # PyInstaller命令参数
    # --onefile: 打包成单个exe文件
    # --windowed 或 -w: 不显示控制台窗口
    # --name: 指定输出文件名
    # --icon: 可以指定图标文件（如果有的话）
    # --add-data: 添加数据文件（如果需要）
    # --hidden-import: 隐藏导入的模块
    
    cmd = [
        'pyinstaller',
        '--onefile',           # 打包成单个文件
        '--windowed',          # 不显示控制台窗口
        '--name=批量执行',      # 输出文件名
        '--clean',              # 清理临时文件
        '--noconfirm',          # 覆盖输出文件时不询问
        # 添加隐藏导入
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=xlrd',
        '--hidden-import=xlsxwriter',
        # 添加数据文件（如果需要）
        # f'--add-data={os.path.join(script_dir, "是否下载.xlsx")};.',
        script_file
    ]
    
    try:
        print(f"执行命令: {' '.join(cmd)}")
        print("-" * 60)
        result = subprocess.run(cmd, cwd=script_dir)
        
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✓ 打包成功!")
            print("=" * 60)
            dist_dir = os.path.join(script_dir, 'dist')
            exe_file = os.path.join(dist_dir, '批量执行.exe')
            if os.path.exists(exe_file):
                print(f"exe文件位置: {exe_file}")
                print(f"文件大小: {os.path.getsize(exe_file) / 1024 / 1024:.2f} MB")
            print("\n提示:")
            print("1. exe文件在 dist 文件夹中")
            print("2. 将exe文件与所有图书馆脚本放在同一目录")
            print("3. 确保目录中有'是否下载.xlsx'文件")
            print("4. 运行exe文件，日志会保存在 logs 文件夹中")
            return True
        else:
            print("\n✗ 打包失败")
            return False
            
    except Exception as e:
        print(f"\n✗ 打包过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("批量执行脚本打包工具")
    print("=" * 60)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("未检测到PyInstaller，正在安装...")
        if not install_pyinstaller():
            print("\n请手动安装PyInstaller:")
            print("  pip install pyinstaller")
            return
    
    # 打包
    build_exe()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        import traceback
        print(f"\n✗ 发生错误: {e}")
        traceback.print_exc()

