#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将所有脚本打包为exe的工具（适用于无Python环境的电脑）
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
    files_to_remove = ['执行脚本.spec', '知网数据.spec', '万方数据.spec', '文件整理.spec']
    
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

def build_script_exe(script_name, script_file):
    """打包单个脚本为exe"""
    if not os.path.exists(script_file):
        print(f"[警告] 找不到文件: {script_file}，跳过")
        return False
    
    print(f"\n[信息] 正在打包: {script_file} -> {script_name}.exe")
    
    cmd = [
        'pyinstaller',
        f'--name={script_name}',
        '--onefile',
        '--console',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=selenium',
        '--hidden-import=io',
        '--clean',
        script_file
    ]
    
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[成功] {script_name}.exe 打包完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[错误] {script_name}.exe 打包失败: {e}")
        return False

def build_all_exe():
    """打包所有脚本为exe"""
    scripts = [
        ('执行脚本', '执行脚本.py', True),  # 需要config.txt
        ('知网数据', '知网数据.py', False),
        ('万方数据', '万方数据.py', False),
        ('文件整理', '文件整理.py', False),
    ]
    
    success_count = 0
    total_count = len(scripts)
    
    for script_name, script_file, needs_config in scripts:
        if build_script_exe(script_name, script_file):
            success_count += 1
            # 如果需要配置文件，复制到dist目录
            if needs_config and os.path.exists('config.txt'):
                try:
                    shutil.copy2('config.txt', 'dist')
                    print(f"[信息] 已复制 config.txt 到 dist 目录")
                except Exception as e:
                    print(f"[警告] 复制 config.txt 失败: {e}")
    
    return success_count == total_count

def main():
    print("=" * 60)
    print("学术研究脚本完整打包工具（无Python环境版本）")
    print("=" * 60)
    
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
    
    # 打包所有脚本
    if build_all_exe():
        print("\n" + "=" * 60)
        print("打包完成！")
        print("=" * 60)
        print("\n[信息] 所有exe文件位于: dist 目录")
        print("\n[文件清单]")
        print("  - 执行脚本.exe")
        print("  - 知网数据.exe")
        print("  - 万方数据.exe")
        print("  - 文件整理.exe")
        print("  - config.txt")
        print("\n[部署说明]")
        print("  1. 将 dist 目录中的所有文件复制到目标电脑")
        print("  2. 目标电脑无需安装Python环境")
        print("  3. 双击 执行脚本.exe 即可运行")
        print("\n[注意] 知网数据和万方数据脚本需要Chrome浏览器")
        return 0
    else:
        print("\n[警告] 部分脚本打包失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消操作")
        sys.exit(1)

