#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将Python脚本打包成exe文件的工具
使用PyInstaller进行打包
"""

import os
import subprocess
import sys

def check_pyinstaller():
    """检查是否安装了PyInstaller"""
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装")
        print("正在安装 PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller 安装成功")
            return True
        except Exception as e:
            print(f"❌ PyInstaller 安装失败: {e}")
            return False

def build_exe(script_name, exe_name=None, icon=None, show_console=True):
    """打包单个Python文件为exe"""
    if exe_name is None:
        exe_name = os.path.splitext(script_name)[0]
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ 文件不存在: {script_path}")
        return False
    
    print(f"\n{'='*60}")
    print(f"正在打包: {script_name}")
    print(f"输出名称: {exe_name}")
    print(f"显示控制台: {'是' if show_console else '否'}")
    print(f"{'='*60}")
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个exe文件
        "--name", exe_name,  # 指定输出文件名
        "--clean",  # 清理临时文件
        "--distpath", os.path.join(current_dir, "dist"),  # 输出目录
        "--workpath", os.path.join(current_dir, "build"),  # 临时文件目录
    ]
    
    # 根据是否需要控制台窗口添加参数
    if not show_console:
        cmd.append("--noconsole")  # 不显示控制台窗口（GUI模式）
    
    # 添加图标（如果提供）
    if icon and os.path.exists(icon):
        cmd.extend(["--icon", icon])
    
    cmd.append(script_path)
    
    try:
        result = subprocess.run(cmd, cwd=current_dir, check=True, capture_output=True, text=True)
        print(f"✅ {script_name} 打包成功！")
        print(f"   输出文件: {os.path.join(current_dir, 'dist', exe_name + '.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} 打包失败:")
        print(f"   错误信息: {e.stderr}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("Python脚本打包工具")
    print("="*60)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("\n❌ 无法继续，请手动安装 PyInstaller:")
        print("   pip install pyinstaller")
        return
    
    # 要打包的Python文件列表
    # 格式: (脚本文件名, exe名称, 是否显示控制台)
    scripts_to_build = [
        ("文件整理.py", "文件整理", False),  # 文件整理不需要控制台
        ("万方数据.py", "万方数据", True),   # 万方数据需要控制台查看进度
        ("知网数据.py", "知网数据", True),    # 知网数据需要控制台查看进度
    ]
    
    print(f"\n准备打包 {len(scripts_to_build)} 个文件:")
    for script, exe_name, show_console in scripts_to_build:
        console_info = "（显示控制台）" if show_console else "（无控制台）"
        print(f"  - {script} -> {exe_name}.exe {console_info}")
    
    input("\n按回车键开始打包...")
    
    # 打包每个文件
    success_count = 0
    for script, exe_name, show_console in scripts_to_build:
        if build_exe(script, exe_name, show_console=show_console):
            success_count += 1
    
    # 总结
    print(f"\n{'='*60}")
    print(f"打包完成！")
    print(f"成功: {success_count}/{len(scripts_to_build)}")
    print(f"{'='*60}")
    
    if success_count == len(scripts_to_build):
        print("\n✅ 所有文件打包成功！")
        print(f"📁 exe文件位置: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')}")
    else:
        print(f"\n⚠️ 有 {len(scripts_to_build) - success_count} 个文件打包失败")

if __name__ == "__main__":
    main()

