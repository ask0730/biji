# -*- coding: utf-8 -*-
import json
import os

def process_line(line, cell=None):
    """处理单个line数据，如果有cell信息则包含行列信息"""
    if not line:
        return None
        
    item = {
        "box": line.get("position", [])[:4],  # 取position的前4个点作为box
        "col": [
            cell.get("start_col", 0) if cell else 0,
            cell.get("end_col", 0) if cell else 0
        ],
        "row": [
            cell.get("start_row", 0) if cell else 0,
            cell.get("end_row", 0) if cell else 0
        ],
        "text": line.get("text", ""),
        "type": line.get("type", "text"),
        "score": line.get("score", 1.0),
        "position": line.get("position", [])
    }
    return item

def extract_lines(data):
    """递归提取所有层级的lines，保留行列信息"""
    result = []
    
    # 处理页面级别的tables
    for page in data.get('result', {}).get('pages', []):
        for table in page.get('tables', []):
            # 处理table直接包含的lines（非单元格内的文本）
            for line in table.get('lines', []):
                item = process_line(line)
                if item:
                    result.append(item)
            
            # 处理table_cells中的lines（表格单元格内的文本）
            for cell in table.get('table_cells', []):
                for line in cell.get('lines', []):
                    # 传入cell信息以获取行列位置
                    item = process_line(line, cell)
                    if item:
                        result.append(item)
    
    return result

# 读取json文件
with open(r'D:\project_data\ocr\file\76ad9fb4026b4f1ea39faa7d5995f8d5\76ad9fb4026b4f1ea39faa7d5995f8d5.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取所有lines
result = extract_lines(data)

# 输出到指定目录
output_path = r'D:\project_data\ocr\file\76ad9fb4026b4f1ea39faa7d5995f8d5\lines_output.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    print('success')