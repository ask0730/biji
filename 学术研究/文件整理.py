#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
万方和知网数据去重合并工具
"""

import pandas as pd
import re
from datetime import datetime
import os
import glob

def normalize_title(title):
    """标准化论文标题，用于去重比较"""
    if pd.isna(title) or not isinstance(title, str):
        return ""
    
    # 转换为小写并移除标点符号
    normalized = re.sub(r'[^\w\u4e00-\u9fa5]', '', title.lower())
    return normalized

def find_title_column(df):
    """自动识别标题列"""
    title_columns = [
        '论文名(arrayTitle)', '标题', 'title', 'Title', '论文标题',
        'arrayTitle', '论文名', '文章标题', '文献标题', '题名'
    ]
    
    for col in title_columns:
        if col in df.columns:
            return col
    
    # 如果没有找到标准列名，返回第一列
    if len(df.columns) > 0:
        return df.columns[0]
    
    return None

def detect_data_source(filename):
    """根据文件名判断数据来源"""
    filename_lower = filename.lower()
    if '万方' in filename or 'wanfang' in filename_lower:
        return '万方'
    elif '知网' in filename or 'cnki' in filename_lower or '知网' in filename:
        return '知网'
    else:
        return '未知'

def find_excel_files(directory):
    """查找目录下所有xlsx文件（排除输出文件）"""
    excel_files = []
    pattern = os.path.join(directory, "*.xlsx")
    
    for file_path in glob.glob(pattern):
        filename = os.path.basename(file_path)
        # 排除合并输出文件和学术研究.xlsx
        if not filename.startswith("合并去重数据_") and filename != "学术研究.xlsx":
            excel_files.append(file_path)
    
    return excel_files

def load_config(config_file="config.txt"):
    """加载配置文件"""
    config = {}
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, config_file)
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    # 解析 key=value 格式
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        except Exception as e:
            print(f"⚠️ 读取配置文件失败: {e}，使用默认配置")
    else:
        print(f"⚠️ 配置文件不存在: {config_path}，使用默认配置")
    
    return config

def main():
    print("万方和知网数据去重合并工具")
    print("=" * 50)
    
    # 设置文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"当前目录: {current_dir}")
    
    try:
        # 自动查找所有xlsx文件
        print("\n正在扫描目录下的Excel文件...")
        excel_files = find_excel_files(current_dir)
        
        if not excel_files:
            print("未找到任何Excel文件（.xlsx）")
            return
        
        print(f"找到 {len(excel_files)} 个Excel文件:")
        for i, file_path in enumerate(excel_files, 1):
            filename = os.path.basename(file_path)
            source = detect_data_source(filename)
            print(f"  {i}. {filename} ({source})")
        
        # 加载数据
        print("\n正在加载数据文件...")
        
        all_dataframes = []
        
        for file_path in excel_files:
            filename = os.path.basename(file_path)
            source = detect_data_source(filename)
            
            try:
                df = pd.read_excel(file_path)
                if not df.empty:
                    # 添加数据来源列
                    df.insert(0, '数据来源', source)
                    all_dataframes.append(df)
                    print(f"✅ {filename} 加载成功: {len(df)} 条记录 ({source})")
                    print(f"   列名: {list(df.columns)}")
                else:
                    print(f"⚠️ {filename} 为空文件，跳过")
            except Exception as e:
                print(f"❌ {filename} 加载失败: {e}")
                continue
        
        # 检查是否有数据
        if not all_dataframes:
            print("没有成功加载任何数据")
            return
        
        # 合并数据
        print("\n开始数据去重和合并...")
        
        # 合并所有数据框
        merged_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"合并前总记录数: {len(merged_df)}")
        
        # 找到标题列（使用第一个数据框的标题列）
        title_col = None
        for df in all_dataframes:
            title_col = find_title_column(df)
            if title_col:
                break
        
        if not title_col:
            print("⚠️ 无法识别标题列，将使用第一列进行去重")
            if len(merged_df.columns) > 1:
                title_col = merged_df.columns[1]  # 跳过"数据来源"列
            else:
                title_col = merged_df.columns[0]
        
        print(f"使用标题列: {title_col}")
        
        # 创建标准化标题列
        merged_df['标准化标题'] = merged_df[title_col].apply(normalize_title)
        
        # 去重处理
        deduplicated = []
        seen_titles = {}
        
        for _, row in merged_df.iterrows():
            normalized_title = row['标准化标题']
            
            if normalized_title and normalized_title in seen_titles:
                # 如果标题已存在，更新数据来源
                existing_idx = seen_titles[normalized_title]
                existing_source = deduplicated[existing_idx]['数据来源']
                current_source = row['数据来源']
                
                # 合并数据来源
                if existing_source != current_source:
                    deduplicated[existing_idx]['数据来源'] = f"{existing_source}和{current_source}"
            else:
                # 新标题，添加到结果中
                deduplicated.append(row.to_dict())
                seen_titles[normalized_title] = len(deduplicated) - 1
        
        # 转换为DataFrame
        merged_data = pd.DataFrame(deduplicated)
        
        # 删除临时列
        if '标准化标题' in merged_data.columns:
            merged_data = merged_data.drop('标准化标题', axis=1)
        
        print(f"去重后记录数: {len(merged_data)}")
        if len(merged_df) > 0:
            print(f"去重率: {((len(merged_df) - len(merged_data)) / len(merged_df) * 100):.2f}%")
        
        # 分析数据来源
        print("\n数据来源分析:")
        source_counts = merged_data['数据来源'].value_counts()
        
        for source, count in source_counts.items():
            percentage = (count / len(merged_data)) * 100
            print(f"  {source}: {count} 条 ({percentage:.2f}%)")
        
        # 预览数据
        print(f"\n数据预览 (前5条记录):")
        print("=" * 80)
        print("列名:", list(merged_data.columns))
        print("-" * 80)
        
        for i, (_, row) in enumerate(merged_data.head(5).iterrows()):
            print(f"记录 {i+1}:")
            for col in merged_data.columns:
                value = str(row[col])[:50] + "..." if len(str(row[col])) > 50 else str(row[col])
                print(f"  {col}: {value}")
            print("-" * 40)
        
        # 保存合并数据
        # 从配置文件读取输出路径
        config = load_config()
        output_folder = config.get('output_folder', '').strip()
        
        print(f"\n{'='*60}")
        print(f"配置信息:")
        print(f"  从配置文件读取的 output_folder: '{output_folder}'")
        print(f"  当前脚本目录: {current_dir}")
        
        # 确定输出目录
        if output_folder:
            # 如果配置了路径，尝试使用或创建
            try:
                # 转换为绝对路径
                if not os.path.isabs(output_folder):
                    # 如果是相对路径，相对于当前脚本目录
                    output_folder = os.path.join(current_dir, output_folder)
                
                output_folder = os.path.normpath(output_folder)  # 规范化路径
                
                # 如果路径不存在，创建它
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder, exist_ok=True)
                    print(f"  ✅ 已创建输出目录: {output_folder}")
                elif not os.path.isdir(output_folder):
                    raise ValueError(f"路径存在但不是目录: {output_folder}")
                
                if os.path.isdir(output_folder):
                    output_dir = output_folder
                    print(f"  ✅ 使用配置的输出路径: {output_dir}")
                else:
                    output_dir = current_dir
                    print(f"  ⚠️ 配置的路径不是目录: {output_folder}，使用当前目录: {output_dir}")
            except Exception as e:
                output_dir = current_dir
                print(f"  ⚠️ 无法创建或访问配置的路径: {output_folder}")
                print(f"     错误: {e}")
                print(f"     使用当前目录: {output_dir}")
        else:
            output_dir = current_dir
            print(f"  ℹ️ 未配置输出路径，使用默认路径: {output_dir}")
        
        # 输出文件名为"学术研究.xlsx"
        output_file = os.path.join(output_dir, "学术研究.xlsx")
        output_file = os.path.normpath(output_file)  # 规范化路径
        print(f"\n正在保存文件到: {output_file}")
        print(f"文件完整路径: {os.path.abspath(output_file)}")
        merged_data.to_excel(output_file, index=False, engine='openpyxl')
        
        # 验证文件是否成功保存
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ 文件保存成功！文件大小: {file_size} 字节")
        else:
            print(f"⚠️ 警告：文件保存后未找到，请检查路径权限")
        
        # 删除原始Excel文件
        print(f"\n正在删除原始Excel文件...")
        deleted_count = 0
        for file_path in excel_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"  ✅ 已删除: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"  ⚠️ 删除失败 {os.path.basename(file_path)}: {e}")
        
        print(f"\n数据处理完成！")
        print(f"输出文件: {output_file}")
        print(f"删除原始文件: {deleted_count}/{len(excel_files)} 个")
        print(f"最终统计:")
        print(f"  总记录数: {len(merged_data)}")
        print(f"  列数: {len(merged_data.columns)}")
        
    except Exception as e:
        print(f"处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
