# -*- coding: utf-8 -*-
"""
文件夹内容移动脚本
功能：将一个文件夹的所有内容移动到另一个文件夹
配置：从config.txt读取源文件夹和目标文件夹路径
"""

import os
import shutil
import time
from pathlib import Path

def load_config(config_path="config.txt"):
    """从配置文件加载设置"""
    config = {}
    try:
        if not os.path.exists(config_path):
            print(f"⚠️  配置文件不存在: {config_path}")
            return config
        
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 解析key=value格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    config[key] = value
        
        print(f"✓ 已加载配置文件: {config_path}")
        return config
    except Exception as e:
        print(f"✗ 读取配置文件失败: {e}")
        return config

def move_folder_contents(source_dir, target_dir):
    """
    将源文件夹的所有内容移动到目标文件夹
    
    参数:
        source_dir: 源文件夹路径
        target_dir: 目标文件夹路径
    
    返回:
        (成功数量, 失败数量, 跳过数量)
    """
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    # 检查源文件夹是否存在
    if not os.path.exists(source_dir):
        print(f"✗ 源文件夹不存在: {source_dir}")
        return (0, 0, 0)
    
    if not os.path.isdir(source_dir):
        print(f"✗ 源路径不是文件夹: {source_dir}")
        return (0, 0, 0)
    
    # 创建目标文件夹（如果不存在）
    try:
        os.makedirs(target_dir, exist_ok=True)
        print(f"✓ 目标文件夹已准备: {target_dir}")
    except Exception as e:
        print(f"✗ 创建目标文件夹失败: {e}")
        return (0, 0, 0)
    
    # 获取源文件夹中的所有内容
    items = os.listdir(source_dir)
    
    if not items:
        print("⚠️  源文件夹为空，没有内容需要移动")
        return (0, 0, 0)
    
    print(f"\n找到 {len(items)} 个项目需要移动")
    print(f"源文件夹: {source_dir}")
    print(f"目标文件夹: {target_dir}")
    print("-" * 60)
    
    # 遍历所有文件和文件夹
    for item in items:
        source_path = os.path.join(source_dir, item)
        target_path = os.path.join(target_dir, item)
        
        try:
            # 检查目标路径是否已存在
            if os.path.exists(target_path):
                print(f"⚠️  跳过（目标已存在）: {item}")
                skip_count += 1
                continue
            
            # 移动文件或文件夹
            print(f"正在移动: {item}...", end=" ")
            shutil.move(source_path, target_path)
            print("✓")
            success_count += 1
            
        except PermissionError as e:
            print(f"✗ 权限不足: {item} - {e}")
            fail_count += 1
        except Exception as e:
            print(f"✗ 移动失败: {item} - {e}")
            fail_count += 1
    
    return (success_count, fail_count, skip_count)

def move_folder_contents_with_overwrite(source_dir, target_dir, overwrite=False):
    """
    将源文件夹的所有内容移动到目标文件夹（可选择是否覆盖）
    
    参数:
        source_dir: 源文件夹路径
        target_dir: 目标文件夹路径
        overwrite: 如果目标文件已存在，是否覆盖
    
    返回:
        (成功数量, 失败数量, 跳过数量)
    """
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    # 检查源文件夹是否存在
    if not os.path.exists(source_dir):
        print(f"✗ 源文件夹不存在: {source_dir}")
        return (0, 0, 0)
    
    if not os.path.isdir(source_dir):
        print(f"✗ 源路径不是文件夹: {source_dir}")
        return (0, 0, 0)
    
    # 创建目标文件夹（如果不存在）
    try:
        os.makedirs(target_dir, exist_ok=True)
        print(f"✓ 目标文件夹已准备: {target_dir}")
    except Exception as e:
        print(f"✗ 创建目标文件夹失败: {e}")
        return (0, 0, 0)
    
    # 获取源文件夹中的所有内容
    items = os.listdir(source_dir)
    
    if not items:
        print("⚠️  源文件夹为空，没有内容需要移动")
        return (0, 0, 0)
    
    print(f"\n找到 {len(items)} 个项目需要移动")
    print(f"源文件夹: {source_dir}")
    print(f"目标文件夹: {target_dir}")
    print(f"覆盖模式: {'是' if overwrite else '否'}")
    print("-" * 60)
    
    # 遍历所有文件和文件夹
    for item in items:
        source_path = os.path.join(source_dir, item)
        target_path = os.path.join(target_dir, item)
        
        try:
            # 检查目标路径是否已存在
            if os.path.exists(target_path):
                if overwrite:
                    # 如果目标存在且是文件夹，先删除
                    if os.path.isdir(target_path):
                        print(f"正在删除已存在的文件夹: {item}...", end=" ")
                        shutil.rmtree(target_path)
                    else:
                        print(f"正在删除已存在的文件: {item}...", end=" ")
                        os.remove(target_path)
                    print("✓")
                else:
                    print(f"⚠️  跳过（目标已存在）: {item}")
                    skip_count += 1
                    continue
            
            # 移动文件或文件夹
            print(f"正在移动: {item}...", end=" ")
            shutil.move(source_path, target_path)
            print("✓")
            success_count += 1
            
        except PermissionError as e:
            print(f"✗ 权限不足: {item} - {e}")
            fail_count += 1
        except Exception as e:
            print(f"✗ 移动失败: {item} - {e}")
            fail_count += 1
    
    return (success_count, fail_count, skip_count)

def main():
    """主函数"""
    print("=" * 60)
    print("文件夹内容移动脚本")
    print("=" * 60)
    
    # 加载配置
    config = load_config("config.txt")
    
    # 获取源文件夹和目标文件夹路径
    source_dir = config.get('source_folder', '').strip()
    target_dir = config.get('target_folder', '').strip()
    
    # 检查配置
    if not source_dir:
        print("\n✗ 配置文件中未找到 source_folder 配置")
        print("请在config.txt中添加:")
        print("  source_folder=源文件夹路径")
        print("  target_folder=目标文件夹路径")
        return
    
    if not target_dir:
        print("\n✗ 配置文件中未找到 target_folder 配置")
        print("请在config.txt中添加:")
        print("  source_folder=源文件夹路径")
        print("  target_folder=目标文件夹路径")
        return
    
    # 检查是否覆盖模式
    overwrite = config.get('overwrite', 'false').strip().lower() in ('true', '1', 'yes', '是')
    
    # 确认操作
    print(f"\n准备移动文件夹内容:")
    print(f"  源文件夹: {source_dir}")
    print(f"  目标文件夹: {target_dir}")
    print(f"  覆盖模式: {'是' if overwrite else '否'}")
    
    # 统计源文件夹中的内容数量
    if os.path.exists(source_dir):
        try:
            item_count = len(os.listdir(source_dir))
            print(f"  源文件夹中有 {item_count} 个项目")
        except:
            pass
    
    # 执行移动操作
    print("\n开始移动...")
    start_time = time.time()
    
    if overwrite:
        success, fail, skip = move_folder_contents_with_overwrite(source_dir, target_dir, overwrite=True)
    else:
        success, fail, skip = move_folder_contents(source_dir, target_dir)
    
    elapsed_time = time.time() - start_time
    
    # 显示结果
    print("\n" + "=" * 60)
    print("移动完成!")
    print("=" * 60)
    print(f"成功: {success} 个")
    print(f"失败: {fail} 个")
    print(f"跳过: {skip} 个")
    print(f"耗时: {elapsed_time:.2f} 秒")
    
    if fail > 0:
        print("\n⚠️  有文件移动失败，请检查错误信息")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        import traceback
        print(f"\n✗ 发生错误: {e}")
        traceback.print_exc()

