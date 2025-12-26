#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包执行脚本为exe的工具脚本
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("[信息] 正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("[成功] PyInstaller安装完成")
        return True
    except subprocess.CalledProcessError:
        print("[错误] PyInstaller安装失败")
        return False

def clean_build():
    """清理之前的构建文件"""
    print("[信息] 清理之前的构建文件...")
    dirs_to_remove = ['build', 'dist']
    files_to_remove = ['执行脚本.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  已删除: {dir_name}")
            except Exception as e:
                print(f"  删除失败 {dir_name}: {e}")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"  已删除: {file_name}")
            except Exception as e:
                print(f"  删除失败 {file_name}: {e}")

def build_exe():
    """打包exe"""
    print("\n[信息] 开始打包执行脚本.py为exe...")
    
    script_file = "执行脚本.py"
    if not os.path.exists(script_file):
        print(f"[错误] 找不到文件: {script_file}")
        return False
    
    # PyInstaller命令参数
    cmd = [
        'pyinstaller',
        '--name=执行脚本',
        '--onefile',
        '--console',
        '--add-data', 'config.txt;.' if sys.platform == 'win32' else 'config.txt:.',
        '--hidden-import=io',
        '--hidden-import=threading',
        '--hidden-import=subprocess',
        '--hidden-import=ctypes',
        '--clean',
        script_file
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n[成功] 打包完成！")
        print(f"[信息] exe文件位置: dist{os.sep}执行脚本.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[错误] 打包失败: {e}")
        return False

def main():
    print("=" * 50)
    print("学术研究脚本打包工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("[警告] 未找到PyInstaller")
        response = input("是否自动安装PyInstaller? (Y/N): ").strip().upper()
        if response in ['Y', 'YES']:
            if not install_pyinstaller():
                return 1
        else:
            print("[错误] 请先安装PyInstaller: pip install pyinstaller")
            return 1
    
    # 清理构建文件
    clean_build()
    
    # 打包
    if build_exe():
        print("\n" + "=" * 50)
        print("打包说明")
        print("=" * 50)
        print("\n[提示] 请确保以下文件与exe在同一目录：")
        print("  - 知网数据.py")
        print("  - 万方数据.py")
        print("  - 文件整理.py")
        print("  - config.txt")
        print("\n[提示] 目标电脑需要安装Python环境才能运行py脚本")
        print("\n[提示] 如果目标电脑没有Python，需要：")
        print("  1. 安装Python 3.x")
        print("  2. 安装依赖包: pip install pandas openpyxl selenium")
        return 0
    else:
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消操作")
        sys.exit(1)

