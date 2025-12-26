#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
万方和知网数据去重合并工具
"""

import pandas as pd
import re
from datetime import datetime
import os
import sys

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

def find_data_file(directory, prefix):
    """查找匹配的数据文件"""
    if not os.path.exists(directory):
        return None
    
    # 可能的文件名模式
    patterns = [
        f"{prefix}.xlsx",
        f"{prefix}数据.xlsx",
        f"{prefix}数据_*.xlsx"
    ]
    
    # 先尝试精确匹配
    for pattern in patterns[:2]:
        file_path = os.path.join(directory, pattern)
        if os.path.exists(file_path):
            return file_path
    
    # 尝试模糊匹配（带年份的文件）
    import glob
    for pattern in patterns[2:]:
        matches = glob.glob(os.path.join(directory, pattern))
        if matches:
            # 返回最新的文件
            return max(matches, key=os.path.getmtime)
    
    return None

def get_base_path():
    """获取脚本或exe所在目录"""
    if getattr(sys, 'frozen', False):
        # 打包后的exe文件
        return os.path.dirname(sys.executable)
    else:
        # 普通Python脚本
        return os.path.dirname(os.path.abspath(__file__))

def load_output_path(config_file="输出路径配置.txt"):
    """从txt配置文件读取输出路径"""
    current_dir = get_base_path()
    config_path = os.path.join(current_dir, config_file)
    
    # 如果配置文件不存在，使用当前目录
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
        print(f"使用默认路径: {current_dir}")
        return current_dir
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            path = f.read().strip()
            # 移除可能的引号和空格
            path = path.strip('"\' \n\r\t')
            
            # 如果是相对路径，转换为绝对路径
            if not os.path.isabs(path):
                path = os.path.join(current_dir, path)
            
            # 如果路径不存在，创建目录
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                print(f"创建输出目录: {path}")
            
            return path
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        print(f"使用默认路径: {current_dir}")
        return current_dir

def main():
    print("万方和知网数据去重合并工具")
    print("=" * 50)
    
    # 设置文件路径
    current_dir = get_base_path()
    
    # 自动查找文件
    wanfang_file = find_data_file(current_dir, "万方")
    cnki_file = find_data_file(current_dir, "知网")
    
    print(f"当前目录: {current_dir}")
    print(f"万方数据文件: {wanfang_file if wanfang_file else '未找到'}")
    print(f"知网数据文件: {cnki_file if cnki_file else '未找到'}")
    
    try:
        # 加载数据
        print("\n正在加载数据文件...")
        
        wanfang_data = None
        cnki_data = None
        
        # 加载万方数据
        if wanfang_file and os.path.exists(wanfang_file):
            wanfang_data = pd.read_excel(wanfang_file)
            print(f"万方数据加载成功: {len(wanfang_data)} 条记录")
            print(f"   文件: {os.path.basename(wanfang_file)}")
            print(f"   列名: {list(wanfang_data.columns)}")
        else:
            print(f"万方数据文件不存在")
            wanfang_data = pd.DataFrame()
        
        # 加载知网数据
        if cnki_file and os.path.exists(cnki_file):
            cnki_data = pd.read_excel(cnki_file)
            print(f"知网数据加载成功: {len(cnki_data)} 条记录")
            print(f"   文件: {os.path.basename(cnki_file)}")
            print(f"   列名: {list(cnki_data.columns)}")
        else:
            print(f"知网数据文件不存在")
            cnki_data = pd.DataFrame()
        
        # 检查数据是否为空
        if wanfang_data.empty and cnki_data.empty:
            print("两个数据文件都为空")
            return
        
        # 为数据添加来源列（放在最前面）
        if not wanfang_data.empty:
            # 将数据来源列插入到第一列
            wanfang_data.insert(0, '数据来源', '万方')
        if not cnki_data.empty:
            # 将数据来源列插入到第一列
            cnki_data.insert(0, '数据来源', '知网')
        
        # 合并数据
        print("\n开始数据去重和合并...")
        
        if wanfang_data.empty:
            merged_data = cnki_data
            print("万方数据为空，只使用知网数据")
        elif cnki_data.empty:
            merged_data = wanfang_data
            print("知网数据为空，只使用万方数据")
        else:
            # 找到标题列
            wanfang_title_col = find_title_column(wanfang_data)
            cnki_title_col = find_title_column(cnki_data)
            
            if not wanfang_title_col or not cnki_title_col:
                print("无法识别标题列")
                return
            
            print(f"万方标题列: {wanfang_title_col}")
            print(f"知网标题列: {cnki_title_col}")
            
            # 创建标准化标题列
            wanfang_data['标准化标题'] = wanfang_data[wanfang_title_col].apply(normalize_title)
            cnki_data['标准化标题'] = cnki_data[cnki_title_col].apply(normalize_title)
            
            # 合并数据
            merged_df = pd.concat([wanfang_data, cnki_data], ignore_index=True)
            print(f"合并前总记录数: {len(merged_df)}")
            
            # 去重处理
            deduplicated = []
            seen_titles = {}
            
            for _, row in merged_df.iterrows():
                normalized_title = row['标准化标题']
                
                if normalized_title in seen_titles:
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
        output_dir = load_output_path()
        output_file = os.path.join(output_dir, "学术研究.xlsx")
        merged_data.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"\n数据处理完成！")
        print(f"输出文件: {output_file}")
        print(f"最终统计:")
        print(f"  总记录数: {len(merged_data)}")
        print(f"  列数: {len(merged_data.columns)}")
        
    except Exception as e:
        print(f"处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
