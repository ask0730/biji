#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量打包Python脚本为exe文件
使用PyInstaller打包项目申报文件夹中的所有Python脚本
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

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
            print(f"❌ 安装失败: {e}")
            print("请手动运行: pip install pyinstaller")
            return False

def build_exe(py_file, dist_dir="dist"):
    """打包单个Python文件为exe"""
    file_name = Path(py_file).stem
    print(f"\n{'='*60}")
    print(f"正在打包: {file_name}.py")
    print(f"{'='*60}")
    
    # PyInstaller 命令参数
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个exe文件
        "--console",  # 显示控制台窗口（可以看到运行进度）
        "--name", file_name,  # 指定exe文件名
        "--distpath", dist_dir,  # 输出目录
        "--workpath", "build",  # 临时文件目录
        "--clean",  # 清理临时文件
        py_file
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {file_name}.exe 打包成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {file_name}.py 打包失败")
        print(f"错误信息: {e.stderr}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("Python脚本批量打包工具")
    print("="*60)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return
    
    # 获取当前目录
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # 查找所有Python文件（排除打包脚本本身）
    python_files = [
        f for f in current_dir.glob("*.py")
        if f.name != "打包成exe.py" and f.name != "__init__.py"
    ]
    
    if not python_files:
        print("❌ 未找到Python文件")
        return
    
    print(f"\n📁 找到 {len(python_files)} 个Python文件:")
    for py_file in python_files:
        print(f"  - {py_file.name}")
    
    print("\n⚠️  注意:")
    print("  - 打包过程可能需要几分钟")
    print("  - 打包后的exe文件将保存在 dist 目录")
    print("  - 请确保 config.txt 文件与exe在同一目录")
    print()
    
    # 确认
    try:
        confirm = input("确认开始打包? (y/n): ").lower().strip()
        if confirm not in ['y', 'yes', '是']:
            print("操作已取消")
            return
    except:
        print("操作已取消")
        return
    
    # 创建输出目录
    dist_dir = current_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # 打包统计
    success_count = 0
    fail_count = 0
    
    # 逐个打包
    for py_file in python_files:
        if build_exe(str(py_file), str(dist_dir)):
            success_count += 1
        else:
            fail_count += 1
    
    # 复制config.txt到dist目录
    config_file = current_dir / "config.txt"
    if config_file.exists():
        dist_config = dist_dir / "config.txt"
        shutil.copy2(config_file, dist_config)
        print(f"\n✅ 已复制 config.txt 到 dist 目录")
    
    # 清理临时文件
    print("\n🧹 正在清理临时文件...")
    
    # 删除 build 目录
    build_dir = current_dir / "build"
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
            print(f"  ✅ 已删除 build 目录")
        except Exception as e:
            print(f"  ⚠️  删除 build 目录失败: {e}")
    
    # 删除所有 .spec 文件
    spec_files = list(current_dir.glob("*.spec"))
    if spec_files:
        deleted_count = 0
        for spec_file in spec_files:
            try:
                spec_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"  ⚠️  删除 {spec_file.name} 失败: {e}")
        if deleted_count > 0:
            print(f"  ✅ 已删除 {deleted_count} 个 .spec 文件")
    
    # 显示结果
    print("\n" + "="*60)
    print("打包完成!")
    print("="*60)
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {fail_count} 个")
    print(f"\n📁 exe文件位置: {dist_dir}")
    print("\n💡 提示:")
    print("  - config.txt 已自动复制到 dist 目录")
    print("  - 临时文件已自动清理")
    print("  - 确保exe文件和config.txt在同一目录下运行")

if __name__ == "__main__":
    main()

