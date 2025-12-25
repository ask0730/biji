# -*- coding: utf-8 -*-
"""
批量执行图书馆年报下载脚本
功能：
1. 读取Excel文件，检查是否已下载
2. 如果未下载，执行对应的图书馆脚本
3. 下载成功后，更新Excel中的"是否下载"状态为"是"
"""

import os
import sys
import subprocess
import pandas as pd
import time
from pathlib import Path

def get_script_dir():
    """获取脚本所在目录"""
    return os.path.dirname(os.path.abspath(__file__))

def load_excel(excel_path):
    """读取Excel文件"""
    try:
        df = pd.read_excel(excel_path)
        return df
    except Exception as e:
        print(f"✗ 读取Excel文件失败: {e}")
        return None

def save_excel(df, excel_path):
    """保存Excel文件"""
    try:
        df.to_excel(excel_path, index=False)
        return True
    except Exception as e:
        print(f"✗ 保存Excel文件失败: {e}")
        return False

def get_library_name_from_script(script_name):
    """从脚本文件名提取图书馆名称"""
    # 移除.py扩展名
    name = script_name.replace('.py', '')
    return name

def find_script_name_in_excel(library_name, df):
    """在Excel中查找对应的图书馆名称"""
    # 尝试匹配不同的列名
    possible_columns = ['图书馆', '图书馆名称', '名称', '图书馆名', '单位', '机构']
    library_column = None
    
    for col in possible_columns:
        if col in df.columns:
            library_column = col
            break
    
    if library_column is None:
        # 如果没有找到明确的列，使用第一列
        library_column = df.columns[0]
    
    # 查找匹配的行
    for idx, row in df.iterrows():
        excel_name = str(row[library_column]).strip()
        # 移除可能的空格和特殊字符
        excel_name_clean = excel_name.replace(' ', '').replace('　', '')
        library_name_clean = library_name.replace(' ', '').replace('　', '')
        
        # 尝试多种匹配方式
        if (library_name in excel_name or 
            excel_name in library_name or
            library_name_clean in excel_name_clean or
            excel_name_clean in library_name_clean):
            return idx, library_column
    
    return None, library_column

def check_if_downloaded(library_name, df):
    """检查图书馆是否已下载"""
    idx, library_column = find_script_name_in_excel(library_name, df)
    
    if idx is None:
        # 如果找不到对应的行，返回False（需要下载）
        return False, None, None
    
    # 查找"是否下载"列
    download_column = None
    possible_download_columns = ['是否下载', '下载状态', '状态', '已下载']
    
    for col in possible_download_columns:
        if col in df.columns:
            download_column = col
            break
    
    if download_column is None:
        # 如果没有找到明确的列，尝试查找包含"下载"的列
        for col in df.columns:
            if '下载' in str(col):
                download_column = col
                break
    
    if download_column is None:
        print(f"⚠️  警告: 未找到'是否下载'列，假设未下载")
        return False, idx, None
    
    # 检查下载状态
    try:
        status = str(df.at[idx, download_column]).strip()
        # 处理NaN值
        if status.lower() in ['nan', 'none', '']:
            status = ''
        is_downloaded = status in ['是', 'Y', 'y', 'Yes', 'YES', 'True', 'true', '1', '已下载', '完成', '✓']
    except Exception as e:
        print(f"  ⚠️  读取下载状态失败: {e}，假设未下载")
        is_downloaded = False
    
    return is_downloaded, idx, download_column

def update_download_status(df, idx, download_column, status='是'):
    """更新下载状态"""
    if idx is not None and download_column is not None:
        df.at[idx, download_column] = status
        return True
    return False

def execute_script(script_path):
    """执行Python脚本"""
    script_name = os.path.basename(script_path)
    try:
        # 获取脚本所在目录
        script_dir = os.path.dirname(script_path)
        
        print(f"\n{'='*60}")
        print(f"正在执行: {script_name}")
        print(f"{'='*60}")
        
        # 设置环境变量，强制使用UTF-8编码输出，避免GBK编码错误
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        # 对于Windows，也设置PYTHONUTF8环境变量
        if sys.platform == 'win32':
            env['PYTHONUTF8'] = '1'
        
        # 切换到脚本所在目录执行
        # 不使用text=True，而是手动处理编码，避免编码错误
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=script_dir,
            capture_output=True,
            env=env,
            timeout=600  # 10分钟超时
        )
        
        # 尝试多种编码方式解码输出
        stdout_text = ''
        stderr_text = ''
        
        if result.stdout:
            # 尝试多种编码
            for encoding in ['utf-8', 'gbk', 'gb2312', 'cp936']:
                try:
                    stdout_text = result.stdout.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # 如果所有编码都失败，使用errors='replace'忽略错误字符
                stdout_text = result.stdout.decode('utf-8', errors='replace')
            
            print(stdout_text)
        
        if result.stderr:
            # 尝试多种编码
            for encoding in ['utf-8', 'gbk', 'gb2312', 'cp936']:
                try:
                    stderr_text = result.stderr.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # 如果所有编码都失败，使用errors='replace'忽略错误字符
                stderr_text = result.stderr.decode('utf-8', errors='replace')
            
            if stderr_text.strip():  # 只打印非空的错误信息
                print(stderr_text, file=sys.stderr)
        
        # 检查是否成功
        output_text = stdout_text.lower() if stdout_text else ''
        error_text = stderr_text.lower() if stderr_text else ''
        combined_text = output_text + ' ' + error_text
        
        # 检查输出中是否包含成功信息
        success_keywords = ['下载完成', '下载成功', 'success', '完成', '✓ 下载完成']
        failure_keywords = ['下载失败', '失败', 'error', '✗', '未找到', '找不到']
        
        has_success = any(keyword in combined_text for keyword in success_keywords)
        has_failure = any(keyword in combined_text for keyword in failure_keywords)
        
        # 如果明确有成功信息，返回True
        if has_success and not has_failure:
            return True
        # 如果明确有失败信息，返回False
        elif has_failure:
            return False
        # 如果返回码为0且没有明确的失败信息，认为成功
        elif result.returncode == 0:
            return True
        else:
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ 执行超时: {script_name}")
        return False
    except Exception as e:
        print(f"✗ 执行脚本失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_all_library_scripts(script_dir):
    """获取所有图书馆脚本"""
    scripts = []
    for file in os.listdir(script_dir):
        if file.endswith('.py') and file not in ['批量执行.py', '整理.py']:
            scripts.append(file)
    return sorted(scripts)

def main():
    """主函数"""
    print("=" * 60)
    print("批量执行图书馆年报下载脚本")
    print("=" * 60)
    
    # 获取脚本所在目录
    script_dir = get_script_dir()
    excel_path = os.path.join(script_dir, '是否下载.xlsx')
    
    # 检查Excel文件是否存在
    if not os.path.exists(excel_path):
        print(f"✗ Excel文件不存在: {excel_path}")
        print("  请确保'是否下载.xlsx'文件存在于脚本目录中")
        return
    
    # 读取Excel文件
    print(f"\n正在读取Excel文件: {excel_path}")
    df = load_excel(excel_path)
    if df is None:
        return
    
    print(f"✓ Excel文件读取成功")
    print(f"  总行数: {len(df)}")
    print(f"  列名: {', '.join(df.columns.tolist())}")
    
    # 获取所有图书馆脚本
    scripts = get_all_library_scripts(script_dir)
    print(f"\n找到 {len(scripts)} 个图书馆脚本")
    
    # 统计信息
    total_scripts = len(scripts)
    skipped_count = 0
    success_count = 0
    failed_count = 0
    not_found_count = 0
    
    # 需要保存Excel的标记
    need_save = False
    
    # 遍历所有脚本
    print(f"\n开始批量执行...")
    print("-" * 60)
    
    for i, script_name in enumerate(scripts, 1):
        library_name = get_library_name_from_script(script_name)
        script_path = os.path.join(script_dir, script_name)
        
        print(f"\n[{i}/{total_scripts}] 处理: {library_name}")
        
        # 检查是否已下载
        is_downloaded, idx, download_column = check_if_downloaded(library_name, df)
        
        if is_downloaded:
            print(f"  ✓ 已下载，跳过")
            skipped_count += 1
            continue
        
        if idx is None:
            print(f"  ⚠️  在Excel中未找到对应记录，将执行脚本")
            not_found_count += 1
        
        # 执行脚本
        success = execute_script(script_path)
        
        if success:
            print(f"  ✓ 执行成功")
            success_count += 1
            
            # 更新Excel中的下载状态
            if idx is not None and download_column is not None:
                if update_download_status(df, idx, download_column, '是'):
                    need_save = True
                    print(f"  ✓ 已更新Excel中的下载状态")
            elif idx is None:
                # 如果Excel中没有对应记录，尝试添加新记录
                try:
                    # 获取图书馆列名
                    _, library_column = find_script_name_in_excel(library_name, df)
                    # 获取下载状态列名
                    download_column = None
                    for col in df.columns:
                        if '下载' in str(col) or col in ['是否下载', '下载状态', '状态']:
                            download_column = col
                            break
                    
                    if download_column:
                        # 添加新行
                        new_row = {library_column: library_name}
                        for col in df.columns:
                            if col not in new_row:
                                new_row[col] = ''
                        new_row[download_column] = '是'
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        need_save = True
                        print(f"  ✓ 已在Excel中添加新记录并标记为已下载")
                    else:
                        print(f"  ⚠️  Excel中未找到对应记录，且无法确定下载状态列，无法更新")
                except Exception as e:
                    print(f"  ⚠️  添加Excel记录失败: {e}")
        else:
            print(f"  ✗ 执行失败")
            failed_count += 1
    
    # 保存Excel文件
    if need_save:
        print(f"\n正在保存Excel文件...")
        if save_excel(df, excel_path):
            print(f"✓ Excel文件已保存")
        else:
            print(f"✗ Excel文件保存失败")
    
    # 显示统计结果
    print(f"\n" + "=" * 60)
    print("批量执行完成!")
    print("=" * 60)
    print(f"总脚本数: {total_scripts}")
    print(f"成功: {success_count} 个")
    print(f"失败: {failed_count} 个")
    print(f"跳过: {skipped_count} 个")
    print(f"未找到记录: {not_found_count} 个")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        import traceback
        print(f"\n✗ 发生错误: {e}")
        traceback.print_exc()

