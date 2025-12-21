#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理PyInstaller打包产生的中间文件
只保留最终的exe文件
"""

import os
import shutil
import glob

def clean_build_files():
    """清理打包产生的中间文件"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("="*60)
    print("清理打包中间文件")
    print("="*60)
    
    deleted_items = []
    
    # 1. 删除build文件夹（临时构建文件）
    build_dir = os.path.join(current_dir, "build")
    if os.path.exists(build_dir):
        try:
            shutil.rmtree(build_dir)
            deleted_items.append(f"✅ 删除: build/")
            print(f"✅ 已删除: build/")
        except Exception as e:
            print(f"⚠️ 删除build文件夹失败: {e}")
    
    # 2. 删除.spec文件（PyInstaller规格文件）
    spec_files = glob.glob(os.path.join(current_dir, "*.spec"))
    for spec_file in spec_files:
        try:
            os.remove(spec_file)
            deleted_items.append(f"✅ 删除: {os.path.basename(spec_file)}")
            print(f"✅ 已删除: {os.path.basename(spec_file)}")
        except Exception as e:
            print(f"⚠️ 删除{spec_file}失败: {e}")
    
    # 3. 删除__pycache__文件夹（Python缓存）
    for root, dirs, files in os.walk(current_dir):
        # 跳过dist文件夹（保留exe文件）
        if 'dist' in root:
            continue
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_dir)
                deleted_items.append(f"✅ 删除: {os.path.relpath(pycache_dir, current_dir)}/")
                print(f"✅ 已删除: {os.path.relpath(pycache_dir, current_dir)}/")
            except Exception as e:
                print(f"⚠️ 删除{pycache_dir}失败: {e}")
    
    # 4. 删除.pyc文件（编译的Python文件）
    pyc_files = []
    for root, dirs, files in os.walk(current_dir):
        # 跳过dist文件夹
        if 'dist' in root:
            continue
        for file in files:
            if file.endswith('.pyc'):
                pyc_files.append(os.path.join(root, file))
    
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            deleted_items.append(f"✅ 删除: {os.path.relpath(pyc_file, current_dir)}")
            print(f"✅ 已删除: {os.path.relpath(pyc_file, current_dir)}")
        except Exception as e:
            print(f"⚠️ 删除{pyc_file}失败: {e}")
    
    # 5. 删除.pyo文件（优化的Python文件）
    pyo_files = []
    for root, dirs, files in os.walk(current_dir):
        if 'dist' in root:
            continue
        for file in files:
            if file.endswith('.pyo'):
                pyo_files.append(os.path.join(root, file))
    
    for pyo_file in pyo_files:
        try:
            os.remove(pyo_file)
            deleted_items.append(f"✅ 删除: {os.path.relpath(pyo_file, current_dir)}")
            print(f"✅ 已删除: {os.path.relpath(pyo_file, current_dir)}")
        except Exception as e:
            print(f"⚠️ 删除{pyo_file}失败: {e}")
    
    # 总结
    print("\n" + "="*60)
    if deleted_items:
        print(f"清理完成！共删除 {len(deleted_items)} 项")
        print("\n保留的文件:")
        print("  ✅ dist/ 文件夹（包含exe文件）")
        print("  ✅ 源代码.py文件")
        print("  ✅ config.txt配置文件")
    else:
        print("没有找到需要清理的中间文件")
    print("="*60)

if __name__ == "__main__":
    clean_build_files()

