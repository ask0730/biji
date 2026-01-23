# -*- coding: utf-8 -*-
"""
打包脚本：将dengji.py打包成exe文件
使用方法：python 打包成exe.py
"""

import os
import sys
import subprocess
import shutil

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
    script_file = os.path.join(script_dir, 'dengji.py')
    
    if not os.path.exists(script_file):
        print(f"✗ 找不到脚本文件: {script_file}")
        return False
    
    print("=" * 60)
    print("开始打包exe文件...")
    print("=" * 60)
    
    # PyInstaller命令参数
    cmd = [
        'pyinstaller',
        '--onefile',           # 打包成单个文件
        '--console',           # 显示控制台窗口（可以看到运行进度）
        '--name=PDF登记处理工具',  # 输出文件名
        '--clean',              # 清理临时文件
        '--noconfirm',          # 覆盖输出文件时不询问
        # 添加隐藏导入（确保所有依赖都被包含）
        '--hidden-import=pdfplumber',
        '--hidden-import=xlrd',
        '--hidden-import=xlwt',
        '--hidden-import=xlutils',
        '--hidden-import=xlutils.copy',
        '--hidden-import=PyPDF2',
        '--hidden-import=json',
        '--hidden-import=datetime',
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
            exe_file = os.path.join(dist_dir, 'PDF登记处理工具.exe')
            if os.path.exists(exe_file):
                file_size = os.path.getsize(exe_file) / 1024 / 1024
                print(f"exe文件位置: {exe_file}")
                print(f"文件大小: {file_size:.2f} MB")
            
            # 复制config.txt到dist目录（如果存在）
            config_file = os.path.join(script_dir, 'config.txt')
            if os.path.exists(config_file):
                dist_config = os.path.join(dist_dir, 'config.txt')
                shutil.copy2(config_file, dist_config)
                print(f"\n✓ 已复制 config.txt 到 dist 目录")
            
            print("\n提示:")
            print("1. exe文件在 dist 文件夹中")
            print("2. 确保exe文件和config.txt在同一目录下运行")
            print("3. 请根据实际情况修改config.txt中的路径配置")
            print("4. 如果使用Excel模板功能，请确保模板文件路径正确")
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
    print("PDF登记处理工具打包脚本")
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

