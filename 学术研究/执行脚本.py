#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术研究脚本批量执行工具
按照顺序执行：知网数据、万方数据、文件整理
"""

import os
import sys
import subprocess
import re
import threading
import io
from datetime import datetime

# 设置Windows下的标准输出编码为UTF-8，避免中文乱码
if sys.platform == 'win32':
    try:
        # 设置控制台代码页为UTF-8
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8代码页
        kernel32.SetConsoleCP(65001)
    except:
        try:
            # 备用方法：使用chcp命令
            os.system('chcp 65001 >nul 2>&1')
        except:
            pass
    
    try:
        # 设置标准输出编码
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except:
        pass

def read_config(config_file='config.txt'):
    """读取配置文件"""
    config = {}
    
    if not os.path.exists(config_file):
        print(f"⚠️ 配置文件 {config_file} 不存在，将使用默认配置（全部执行）")
        return {
            '执行知网数据': '是',
            '执行万方数据': '是',
            '执行文件整理': '是'
        }
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 解析键值对
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    config[key] = value
        
        return config
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        print("将使用默认配置（全部执行）")
        return {
            '执行知网数据': '是',
            '执行万方数据': '是',
            '执行文件整理': '是'
        }

def should_execute(config_value):
    """判断是否应该执行脚本"""
    if not config_value:
        return False
    
    config_value = config_value.strip().upper()
    # 支持：是、Y、YES、TRUE、1
    return config_value in ['是', 'Y', 'YES', 'TRUE', '1', 'TRUE']

def read_output(pipe, output_type='stdout', is_binary=False):
    """实时读取子进程输出"""
    try:
        if is_binary:
            # Windows下使用二进制模式读取
            for line_bytes in iter(pipe.readline, b''):
                if line_bytes:
                    try:
                        # 尝试UTF-8解码
                        line = line_bytes.decode('utf-8', errors='replace')
                    except (UnicodeDecodeError, AttributeError):
                        # 如果解码失败，使用replace模式
                        line = line_bytes.decode('utf-8', errors='replace')
                    
                    # 实时输出
                    sys.stdout.write(line)
                    sys.stdout.flush()
        else:
            # 非Windows下使用文本模式读取
            for line in iter(pipe.readline, ''):
                if line:
                    # 实时输出
                    sys.stdout.write(line)
                    sys.stdout.flush()
        pipe.close()
    except Exception as e:
        error_msg = f"读取{output_type}时出错: {e}"
        try:
            sys.stdout.write(error_msg + '\n')
            sys.stdout.flush()
        except:
            print(error_msg)

def run_script(script_name, script_path):
    """执行Python脚本，实时输出日志"""
    print("\n" + "=" * 60)
    print(f"🚀 开始执行: {script_name}")
    print("=" * 60)
    
    original_dir = None
    process = None
    
    try:
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(script_path))
        
        # 切换到脚本目录
        original_dir = os.getcwd()
        os.chdir(script_dir)
        
        # 准备环境变量，确保子进程使用UTF-8编码
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        if sys.platform == 'win32':
            env['PYTHONUTF8'] = '1'
        
        # 使用Popen创建进程，启用实时输出
        # 使用 -u 参数禁用Python输出缓冲，确保实时输出
        # 在Windows下使用二进制模式读取，然后手动解码，避免编码问题
        if sys.platform == 'win32':
            process = subprocess.Popen(
                [sys.executable, '-u', '-X', 'utf8', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 将stderr合并到stdout
                bufsize=1,  # 行缓冲
                env=env  # 传递环境变量
            )
        else:
            process = subprocess.Popen(
                [sys.executable, '-u', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 将stderr合并到stdout
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,  # 行缓冲
                universal_newlines=True,
                env=env  # 传递环境变量
            )
        
        # 创建线程实时读取输出
        is_binary = sys.platform == 'win32'
        output_thread = threading.Thread(
            target=read_output,
            args=(process.stdout, 'stdout', is_binary),
            daemon=True
        )
        output_thread.start()
        
        # 等待进程完成
        return_code = process.wait()
        
        # 等待输出线程完成
        output_thread.join(timeout=1)
        
        if return_code == 0:
            print(f"\n✅ {script_name} 执行成功")
            return True
        else:
            print(f"\n❌ {script_name} 执行失败，返回码: {return_code}")
            return False
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  用户中断执行: {script_name}")
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        return False
        
    except Exception as e:
        print(f"\n❌ 执行 {script_name} 时出错: {e}")
        import traceback
        traceback.print_exc()
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        return False
        
    finally:
        # 确保切换回原目录
        if original_dir:
            try:
                os.chdir(original_dir)
            except:
                pass

def main():
    """主函数"""
    print("=" * 60)
    print("📚 学术研究脚本批量执行工具")
    print("=" * 60)
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'config.txt')
    
    # 读取配置
    print(f"\n📖 正在读取配置文件: {config_file}")
    config = read_config(config_file)
    
    # 显示配置信息
    print("\n📋 执行配置:")
    print("-" * 60)
    scripts_config = {
        '执行知网数据': '知网数据.py',
        '执行万方数据': '万方数据.py',
        '执行文件整理': '文件整理.py'
    }
    
    for config_key, script_name in scripts_config.items():
        should_run = should_execute(config.get(config_key, '否'))
        status = "✅ 执行" if should_run else "⏭️  跳过"
        print(f"  {status} - {script_name}")
    
    print("-" * 60)
    
    # 定义脚本执行顺序
    scripts = [
        ('知网数据.py', '知网数据'),
        ('万方数据.py', '万方数据'),
        ('文件整理.py', '文件整理')
    ]
    
    # 记录执行结果
    results = []
    start_time = datetime.now()
    
    # 按顺序执行脚本
    for script_file, config_key in scripts:
        script_path = os.path.join(script_dir, script_file)
        config_key_full = f'执行{config_key}'
        
        # 检查脚本文件是否存在
        if not os.path.exists(script_path):
            print(f"\n⚠️  脚本文件不存在: {script_path}")
            results.append((script_file, False, "文件不存在"))
            continue
        
        # 检查是否应该执行
        if not should_execute(config.get(config_key_full, '否')):
            print(f"\n⏭️  跳过执行: {script_file} (配置为不执行)")
            results.append((script_file, True, "已跳过"))
            continue
        
        # 执行脚本
        success = run_script(script_file, script_path)
        results.append((script_file, success, "执行成功" if success else "执行失败"))
        
        # 如果脚本执行失败，询问是否继续
        if not success:
            print(f"\n⚠️  {script_file} 执行失败")
            user_input = input("是否继续执行后续脚本？(Y/N，默认Y): ").strip().upper()
            if user_input not in ['', 'Y', 'YES']:
                print("❌ 用户选择停止执行")
                break
    
    # 显示执行总结
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("📊 执行总结")
    print("=" * 60)
    
    for script_file, success, message in results:
        status_icon = "✅" if success else "❌"
        print(f"  {status_icon} {script_file}: {message}")
    
    print(f"\n⏱️  总耗时: {duration}")
    print("=" * 60)
    
    # 检查是否有失败的脚本
    failed_scripts = [s for s, success, _ in results if not success and "跳过" not in results[results.index((s, success, _))][2]]
    if failed_scripts:
        print(f"\n⚠️  有 {len(failed_scripts)} 个脚本执行失败")
        return 1
    else:
        print("\n🎉 所有脚本执行完成！")
        return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

