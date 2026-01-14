import json
import PyPDF2
import re
import os
import shutil
import sys
from datetime import datetime
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("警告: 未安装pdfplumber库，将无法提取表格数据。请安装: pip install pdfplumber")
try:
    import xlrd
    import xlwt
    from xlutils.copy import copy as xl_copy
    HAS_XL_LIBS = True
except ImportError:
    HAS_XL_LIBS = False
    print("警告: 未安装xlrd、xlwt和xlutils库，将无法写入Excel文件")

def extract_pdf_tables(pdf_path):
    """按PDF中的表格结构提取数据，每个单元格的多行内容合并到一个格子里，处理跨页情况"""
    if not HAS_PDFPLUMBER:
        print("错误: 需要安装pdfplumber库才能提取表格数据")
        return None
    
    all_tables_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"PDF共有 {len(pdf.pages)} 页")
            
            # 先收集所有页面的表格数据
            all_page_tables = []
            for page_num, page in enumerate(pdf.pages, start=1):
                print(f"正在处理第 {page_num} 页...")
                tables = page.extract_tables()
                if tables:
                    print(f"  第 {page_num} 页找到 {len(tables)} 个表格")
                    for table_idx, table in enumerate(tables):
                        all_page_tables.append({
                            "page": page_num,
                            "table_index": table_idx + 1,
                            "table": table
                        })
                else:
                    print(f"  第 {page_num} 页未找到表格")
            
            # 处理跨页表格合并
            i = 0
            while i < len(all_page_tables):
                current = all_page_tables[i]
                table_data = {
                    "page": current["page"],
                    "table_index": current["table_index"],
                    "rows": []
                }
                
                # 处理当前表格
                for row_idx, row in enumerate(current["table"]):
                    if row is None:
                        continue
                    
                    processed_row = []
                    for cell_idx, cell in enumerate(row):
                        if cell is None:
                            continue
                        else:
                            cell_text = str(cell)
                            cell_text = re.sub(r'[\r\n]+', '', cell_text)
                            cell_text = cell_text.strip()
                            if cell_text:
                                processed_row.append(cell_text)
                    
                    if processed_row:
                        table_data["rows"].append(processed_row)
                
                # 检查下一页是否有相同表格的延续（跨页情况）
                # 判断标准：如果当前表格的最后一行只有部分内容，且下一页的第一行看起来是延续
                if i + 1 < len(all_page_tables):
                    next_table = all_page_tables[i + 1]
                    # 检查是否是同一表格的延续（通过检查列数和内容模式）
                    if (table_data["rows"] and 
                        next_table["table"] and 
                        len(next_table["table"]) > 0):
                        
                        # 检查当前表格最后一行和下一页第一行
                        last_row = table_data["rows"][-1] if table_data["rows"] else []
                        next_first_row_raw = next_table["table"][0]
                        
                        # 处理下一页第一行
                        next_first_row = []
                        for cell in next_first_row_raw:
                            if cell is not None:
                                cell_text = str(cell)
                                cell_text = re.sub(r'[\r\n]+', '', cell_text)
                                cell_text = cell_text.strip()
                                if cell_text:
                                    next_first_row.append(cell_text)
                        
                        # 检查跨页单元格分割的情况
                        # 情况1: 当前表格最后一行只有1个单元格，且内容不完整（如"考试考核结"）
                        # 情况2: 当前表格最后一行有多个单元格，但最后一个单元格可能被分割
                        should_merge = False
                        merge_info = None
                        
                        if last_row and next_first_row:
                            # 情况1: 最后一行只有1个单元格
                            if len(last_row) == 1:
                                last_cell = last_row[0]
                                if next_first_row and len(next_first_row) >= 1:
                                    next_first_cell = next_first_row[0]
                                    # 检查是否是跨页分割：当前单元格较短且不完整，下一单元格也很短
                                    if (last_cell and next_first_cell and
                                        len(last_cell) < 15 and  # 当前单元格较短
                                        len(next_first_cell) < 5 and  # 下一单元格很短（可能是被分割的部分）
                                        not last_cell.endswith(('。', '，', '、', '：', ':', '；', ';', '）', ')', '】', ']')) and
                                        not next_first_cell.startswith(('。', '，', '、', '：', ':', '；', ';', '（', '(', '【', '['))):
                                        should_merge = True
                                        merge_info = {
                                            "type": "single_cell",
                                            "last_cell": last_cell,
                                            "next_first_cell": next_first_cell,
                                            "next_row_rest": next_first_row[1:] if len(next_first_row) > 1 else []
                                        }
                            
                            # 情况2: 最后一行有多个单元格，检查最后一个单元格是否被分割
                            elif len(last_row) > 1:
                                last_cell = last_row[-1]
                                if next_first_row and len(next_first_row) >= 1:
                                    next_first_cell = next_first_row[0]
                                    # 如果当前最后一个单元格较短且不完整，下一行第一个单元格也很短
                                    if (last_cell and next_first_cell and
                                        len(last_cell) < 15 and
                                        len(next_first_cell) < 5 and
                                        not last_cell.endswith(('。', '，', '、', '：', ':', '；', ';', '）', ')', '】', ']')) and
                                        not next_first_cell.startswith(('。', '，', '、', '：', ':', '；', ';', '（', '(', '【', '['))):
                                        should_merge = True
                                        merge_info = {
                                            "type": "last_cell",
                                            "last_row": last_row[:-1],
                                            "last_cell": last_cell,
                                            "next_first_cell": next_first_cell,
                                            "next_row_rest": next_first_row[1:] if len(next_first_row) > 1 else []
                                        }
                        
                        if should_merge and merge_info:
                            # 合并单元格内容
                            merged_cell = merge_info["last_cell"] + merge_info["next_first_cell"]
                            
                            if merge_info["type"] == "single_cell":
                                # 情况1: 单单元格行
                                table_data["rows"][-1] = [merged_cell]
                                if merge_info["next_row_rest"]:
                                    table_data["rows"][-1].extend(merge_info["next_row_rest"])
                            else:
                                # 情况2: 多单元格行的最后一个单元格
                                new_row = merge_info["last_row"] + [merged_cell]
                                if merge_info["next_row_rest"]:
                                    new_row.extend(merge_info["next_row_rest"])
                                table_data["rows"][-1] = new_row
                            
                            # 处理下一页表格的剩余行
                            for row_idx in range(1, len(next_table["table"])):
                                row = next_table["table"][row_idx]
                                if row is None:
                                    continue
                                
                                processed_row = []
                                for cell_idx, cell in enumerate(row):
                                    if cell is None:
                                        continue
                                    else:
                                        cell_text = str(cell)
                                        cell_text = re.sub(r'[\r\n]+', '', cell_text)
                                        cell_text = cell_text.strip()
                                        if cell_text:
                                            processed_row.append(cell_text)
                                
                                if processed_row:
                                    table_data["rows"].append(processed_row)
                            
                            # 跳过下一页的表格（因为已经合并了）
                            i += 2
                            if table_data["rows"]:
                                all_tables_data.append(table_data)
                                print(f"    表格 {current['table_index']}: {len(table_data['rows'])} 行 (已合并跨页单元格)")
                            continue
                
                # 如果没有跨页合并，正常添加当前表格
                if table_data["rows"]:
                    all_tables_data.append(table_data)
                    print(f"    表格 {current['table_index']}: {len(table_data['rows'])} 行 x {len(table_data['rows'][0]) if table_data['rows'] else 0} 列")
                
                i += 1
        
        return all_tables_data
    
    except Exception as e:
        print(f"提取PDF表格时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def get_json_value_by_field(sheet_data, field_name, sheet_name):
    """根据字段名从对应工作表的JSON数据中提取值"""
    if not sheet_data:
        return ""
    
    # 字段名清理（去掉特殊字符）
    field_clean = field_name.replace("(ZH)", "").replace("（", "").replace("）", "").strip()
    
    # 如果是字典类型（对象）
    if isinstance(sheet_data, dict):
        # 直接匹配字段名
        if field_name in sheet_data:
            value = sheet_data[field_name]
            if value is not None and value != "":
                return str(value)
        
        # 清理后的字段名匹配
        if field_clean in sheet_data:
            value = sheet_data[field_clean]
            if value is not None and value != "":
                return str(value)
        
        # 特殊字段映射
        field_mapping = {
            "出生日期": "出生年月",
            "参加工作日期": "参加工作时间",
            "手机": "手机号码",
            "档案所在地": "档案存放单位",
            "申报级别": "级别",
        }
        
        if field_name in field_mapping:
            mapped_key = field_mapping[field_name]
            if mapped_key in sheet_data:
                value = sheet_data[mapped_key]
                if value is not None and value != "":
                    return str(value)
    
    # 如果是列表类型（数组），返回第一条记录的值
    elif isinstance(sheet_data, list) and len(sheet_data) > 0:
        first_item = sheet_data[0]
        if isinstance(first_item, dict):
            # 直接匹配
            if field_name in first_item:
                value = first_item[field_name]
                if value is not None and value != "":
                    return str(value)
            
            # 清理后的字段名匹配
            if field_clean in first_item:
                value = first_item[field_clean]
                if value is not None and value != "":
                    return str(value)
    
    return ""

def create_default_style():
    """创建默认样式：宋体12号，有边框线"""
    style = xlwt.XFStyle()
    
    # 设置字体：宋体12号
    font = xlwt.Font()
    font.name = '宋体'
    font.height = 12 * 20  # 高度单位是1/20点，12号 = 12 * 20
    style.font = font
    
    # 设置边框：所有边框都有线
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    style.borders = borders
    
    return style

def get_cell_style_from_template(rb, sheet_idx, ref_row, col_idx):
    """从模板中获取参考单元格的样式并转换为xlwt样式，如果失败则使用默认样式"""
    try:
        ws_read = rb.sheet_by_index(sheet_idx)
        if ref_row >= ws_read.nrows or col_idx >= ws_read.ncols:
            return create_default_style()
        
        # 获取单元格的格式索引
        xf_index = ws_read.cell_xf_index(ref_row, col_idx)
        if xf_index is None:
            return create_default_style()
        
        # 使用默认样式（因为xlrd和xlwt的样式系统不完全兼容）
        return create_default_style()
    except Exception as e:
        # 如果出错，返回默认样式
        return create_default_style()

def write_json_to_excel(excel_path, json_data, row=3):
    """将JSON数据写入Excel模板，从指定行开始写入（row=3对应Excel第4行）"""
    if not HAS_XL_LIBS:
        print("错误: 缺少必要的库，请安装: pip install xlrd xlwt xlutils")
        return
    
    try:
        # 使用xlrd读取文件（保留格式信息）
        rb = xlrd.open_workbook(excel_path, formatting_info=True)
        
        # 使用xlutils.copy复制工作簿，这样可以保留格式
        wb = xl_copy(rb)
        
        # 工作表名称到JSON键名的映射
        sheet_to_json_mapping = {
            "人员基本信息": "人员基本信息",
            "职称申报继续教育": "职称申报继续教育",
            "职称申报基础信息": "职称申报基础信息",
            "发表论文专著编著": "发表论文专著编著",
            "取得专利技术标准": "取得专利技术标准",
            "其他业绩成果": "其他业绩成果",
        }
        
        # 处理所有工作表
        for sheet_idx in range(len(rb.sheet_names())):
            sheet_name = rb.sheet_names()[sheet_idx]
            ws_read = rb.sheet_by_index(sheet_idx)
            ws_new = wb.get_sheet(sheet_idx)
            
            # 获取对应的JSON数据
            json_key = sheet_to_json_mapping.get(sheet_name)
            
            if json_key and json_key in json_data:
                sheet_data = json_data[json_key]
                
                # 读取第二行的字段名（索引为1，因为从0开始）
                template_fields = []
                if ws_read.nrows > 1:
                    for c in range(ws_read.ncols):
                        field_name = str(ws_read.cell_value(1, c)).strip()
                        template_fields.append(field_name)
                
                # 获取参考行的样式
                ref_row = min(2, ws_read.nrows - 1) if ws_read.nrows > 0 else 0
                default_style = create_default_style()
                
                # 处理数组类型的JSON数据（如职称申报继续教育）
                if isinstance(sheet_data, list):
                    # 对于数组，写入多行数据
                    for idx, item in enumerate(sheet_data):
                        write_row = row + idx
                        for col_idx, template_field in enumerate(template_fields):
                            value = get_json_value_by_field(item, template_field, sheet_name)
                            ws_new.write(write_row, col_idx, value, default_style)
                else:
                    # 对于单个对象，只写入一行
                    for col_idx, template_field in enumerate(template_fields):
                        value = get_json_value_by_field(sheet_data, template_field, sheet_name)
                        ws_new.write(row, col_idx, value, default_style)
        
        # 获取员工姓名用于重命名文件
        employee_name = ""
        if "人员基本信息" in json_data:
            basic_info = json_data["人员基本信息"]
            if isinstance(basic_info, dict) and "姓名" in basic_info:
                employee_name = basic_info["姓名"]
        
        # 保存文件
        if employee_name:
            output_path = os.path.join(os.path.dirname(excel_path), f"{employee_name}.xls")
        else:
            output_path = excel_path.replace(".xls", "_output.xls")
        
        wb.save(output_path)
        print(f"数据已写入: {output_path}")
        
    except Exception as e:
        print(f"写入Excel时出错: {str(e)}")
        import traceback
        traceback.print_exc()

def main(pdf_path):
    """主函数：提取PDF表格数据"""
    # 按PDF表格结构提取数据
    print("\n开始提取PDF表格数据...")
    tables_data = extract_pdf_tables(pdf_path)
    if tables_data:
        # 去掉所有单元格内容中的空格
        for table_info in tables_data:
            if "rows" in table_info:
                for row in table_info["rows"]:
                    for i in range(len(row)):
                        if isinstance(row[i], str):
                            row[i] = row[i].replace(" ", "")
        
        # 保存到JSON文件
        with open("提取的表格数据.json", "w", encoding="utf-8") as f:
            json.dump(tables_data, f, ensure_ascii=False, indent=2)
        print("已保存提取的表格数据到: 提取的表格数据.json")
    else:
        print("未能提取到表格数据")

def parse_tables_json(json_path="提取的表格数据.json"):
    """读取提取的表格数据.json，解析为六个部分的数据"""
    from datetime import datetime
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tables_data = json.load(f)
    except Exception as e:
        print(f"读取表格数据JSON文件失败: {str(e)}")
        return None
    
    # 将所有表格的行合并成一个列表，便于查找
    all_rows = []
    for table in tables_data:
        all_rows.extend(table.get("rows", []))
    
    # 获取当前年份（固定为2025）
    current_year = 2025
    
    # 一、人员基本信息（在"基础信息"后面）
    basic_info = {
        "姓名": "",
        "证件类型": "身份证",
        "证件号码": "",
        "所属组织": "首都图书馆"
    }
    
    # 找到"基础信息"标记
    basic_info_found = False
    for i, row in enumerate(all_rows):
        if any("基础信息" in str(cell) for cell in row):
            basic_info_found = True
            # 从标记后面开始查找
            for j in range(i + 1, min(i + 20, len(all_rows))):
                row_data = all_rows[j]
                # 查找姓名
                for k, cell in enumerate(row_data):
                    if "姓名" in str(cell) and k + 1 < len(row_data):
                        basic_info["姓名"] = str(row_data[k + 1]).strip()
                    # 查找证件号码
                    if "证件号码" in str(cell) and k + 1 < len(row_data):
                        basic_info["证件号码"] = str(row_data[k + 1]).strip()
            break
    
    # 二、职称申报继续教育（在"继续教育-A4"后面）
    continue_education_list = []
    
    # 找到"继续教育-A4"标记
    edu_start_idx = -1
    for i, row in enumerate(all_rows):
        if any("继续教育-A4" in str(cell) for cell in row):
            edu_start_idx = i
            break
    
    if edu_start_idx >= 0:
        # 查找所有表头行（可能跨页）
        # 先查找第一个表头（可能在"往年所填信息"或"本年度所填信息"后面）
        header_row_idx = -1
        start_time_idx = -1
        end_time_idx = -1
        org_unit_idx = -1
        content_idx = -1
        form_idx = -1
        hours_idx = -1
        result_idx = -1
        
        # 从"继续教育-A4"后面开始查找表头
        for i in range(edu_start_idx + 1, min(edu_start_idx + 30, len(all_rows))):
            row = all_rows[i]
            row_str = "".join(str(cell) for cell in row)
            
            # 查找包含"起始时间"和"结束时间"的表头行
            if "起始时间" in row_str and "结束时间" in row_str:
                header_row_idx = i
                # 确定各列的索引
                for k, cell in enumerate(row):
                    cell_str = str(cell)
                    if "起始时间" in cell_str:
                        start_time_idx = k
                    elif "结束时间" in cell_str:
                        end_time_idx = k
                    elif "组织单位" in cell_str:
                        org_unit_idx = k
                    elif "学习内容" in cell_str:
                        content_idx = k
                    elif "学习形式" in cell_str:
                        form_idx = k
                    elif "学时" in cell_str:
                        hours_idx = k
                    elif "考试考核结果" in cell_str or "考试考核" in cell_str or cell_str == "果":
                        result_idx = k
                
                # 如果result_idx还没找到，检查下一行是否有"果"
                if result_idx == -1 and i + 1 < len(all_rows):
                    next_row = all_rows[i + 1]
                    if len(next_row) > 0 and str(next_row[0]) == "果":
                        result_idx = len(row)  # 最后一列
                
                break
        
        # 如果找到了表头，开始提取数据
        if header_row_idx >= 0 and start_time_idx >= 0:
            # 从表头下一行开始提取数据（跳过"无"等无效行）
            for i in range(header_row_idx + 1, len(all_rows)):
                data_row = all_rows[i]
                row_str = "".join(str(cell) for cell in data_row)
                
                # 如果遇到下一个标记，停止
                if any(marker in row_str for marker in ["工作经历-A5", "发表论文", "取得专利", "其他业绩成果", "学历信息-A3", "继续教育-A4"]):
                    break
                
                # 跳过表头行和标记行（只跳过"本年度所填信息"，保留"往年所填信息"后面的数据）
                if ("起始时间" in row_str and "结束时间" in row_str) or \
                   "本年度所填信息" in row_str or \
                   row_str.strip() == "无" or row_str.strip() == "":
                    continue
                
                # 检查是否是数据行（包含日期格式）
                has_date = False
                for cell in data_row:
                    if isinstance(cell, str) and re.match(r'\d{4}-\d{2}-\d{2}', cell):
                        has_date = True
                        break
                
                if not has_date:
                    continue
                
                # 提取数据
                edu_item = {
                    "年度": current_year,
                    "起始时间": "",
                    "结束时间": "",
                    "组织单位": "",
                    "学习内容": "",
                    "学习形式": "其他",
                    "学时": "",
                    "考试考核结果": ""
                }
                
                if start_time_idx >= 0 and start_time_idx < len(data_row):
                    edu_item["起始时间"] = str(data_row[start_time_idx]).strip()
                if end_time_idx >= 0 and end_time_idx < len(data_row):
                    edu_item["结束时间"] = str(data_row[end_time_idx]).strip()
                if org_unit_idx >= 0 and org_unit_idx < len(data_row):
                    edu_item["组织单位"] = str(data_row[org_unit_idx]).strip()
                if content_idx >= 0 and content_idx < len(data_row):
                    edu_item["学习内容"] = str(data_row[content_idx]).strip()
                if form_idx >= 0 and form_idx < len(data_row):
                    edu_item["学习形式"] = str(data_row[form_idx]).strip()
                if hours_idx >= 0 and hours_idx < len(data_row):
                    hours_str = str(data_row[hours_idx]).strip()
                    edu_item["学时"] = hours_str  # 保持原文格式，不转换
                # 考试考核结果可能在最后一列
                if result_idx >= 0 and result_idx < len(data_row):
                    edu_item["考试考核结果"] = str(data_row[result_idx]).strip()
                elif len(data_row) > hours_idx and hours_idx >= 0:
                    # 如果result_idx没找到，尝试最后一列
                    edu_item["考试考核结果"] = str(data_row[-1]).strip() if data_row else ""
                
                # 只添加有起始时间的记录
                if edu_item["起始时间"]:
                    continue_education_list.append(edu_item)
    
    # 三、职称申报基础信息（"基础信息"后面和"个人申请"后面）
    title_app_info = {
        "年度": current_year,
        "级别": "",
        "申报专业技术资格": "",
        "手机号码": "",
        "证件号码": "",
        "姓名": "",
        "户口所在地": "",
        "性别": "",
        "参加工作时间": "",
        "出生年月": "",
        "从事申报专业工作年限": "",
        "民族": "",
        "现从事专业": "",
        "参加学术团体及职务": "",
        "工作单位": "",
        "参保单位": "",
        "所在部门": "",
        "社会信用代码": "",
        "行政职务": "",
        "档案存放单位": ""
    }
    
    # 从"个人申请"后面提取
    personal_app_found = False
    for i, row in enumerate(all_rows):
        if any("个人申请" in str(cell) for cell in row):
            personal_app_found = True
            for j in range(i + 1, min(i + 10, len(all_rows))):
                row_data = all_rows[j]
                for k, cell in enumerate(row_data):
                    cell_str = str(cell)
                    if k + 1 < len(row_data):
                        value = str(row_data[k + 1]).strip()
                        if "级别" in cell_str:
                            title_app_info["级别"] = value
                        elif "申报专业技术资格" in cell_str:
                            title_app_info["申报专业技术资格"] = value
            break
    
    # 从"基础信息"后面提取
    if basic_info_found:
        for i, row in enumerate(all_rows):
            if any("基础信息" in str(cell) for cell in row):
                for j in range(i + 1, min(i + 20, len(all_rows))):
                    row_data = all_rows[j]
                    for k, cell in enumerate(row_data):
                        cell_str = str(cell)
                        if k + 1 < len(row_data):
                            value = str(row_data[k + 1]).strip()
                            if "手机号码" in cell_str:
                                title_app_info["手机号码"] = value
                            elif "证件号码" in cell_str:
                                title_app_info["证件号码"] = value
                            elif "姓名" in cell_str:
                                title_app_info["姓名"] = value
                            elif "户口所在地" in cell_str:
                                title_app_info["户口所在地"] = value
                            elif "性别" in cell_str:
                                title_app_info["性别"] = value
                            elif "参加工作时间" in cell_str:
                                title_app_info["参加工作时间"] = value
                            elif "出生年月" in cell_str:
                                title_app_info["出生年月"] = value
                            elif "从事申报专业工作年限" in cell_str:
                                title_app_info["从事申报专业工作年限"] = value
                            elif "民族" in cell_str:
                                title_app_info["民族"] = value
                            elif "现从事专业" in cell_str:
                                title_app_info["现从事专业"] = value
                            elif "参加学术团体及职务" in cell_str:
                                title_app_info["参加学术团体及职务"] = value
                            elif "工作单位" in cell_str:
                                title_app_info["工作单位"] = value
                            elif "参保单位" in cell_str:
                                title_app_info["参保单位"] = value
                            elif "所在部门" in cell_str:
                                title_app_info["所在部门"] = value
                            elif "社会信用代码" in cell_str:
                                title_app_info["社会信用代码"] = value
                            elif "行政职务" in cell_str:
                                title_app_info["行政职务"] = value
                            elif "档案存放单位" in cell_str:
                                title_app_info["档案存放单位"] = value
                break
    
    # 如果人员基本信息中没有姓名和证件号码，从职称申报基础信息中获取
    if not basic_info["姓名"] and title_app_info["姓名"]:
        basic_info["姓名"] = title_app_info["姓名"]
    if not basic_info["证件号码"] and title_app_info["证件号码"]:
        basic_info["证件号码"] = title_app_info["证件号码"]
    
    # 四、发表论文专著编著（"发表论文/专著/编著-B4"后面）
    papers_list = []
    
    papers_start_idx = -1
    for i, row in enumerate(all_rows):
        if any("发表论文" in str(cell) and "B4" in str(cell) for cell in row):
            papers_start_idx = i
            break
    
    if papers_start_idx >= 0:
        # 查找"本年度所填信息"后面的表头行
        header_row_idx = -1
        year_idx = -1
        name_idx = -1
        time_idx = -1
        pub_idx = -1
        length_idx = -1
        role_idx = -1
        
        # 从"发表论文"后面开始查找"本年度所填信息"和表头
        found_current_year = False
        for i in range(papers_start_idx + 1, len(all_rows)):
            row = all_rows[i]
            row_str = "".join(str(cell) for cell in row)
            
            # 查找"本年度所填信息"标记
            if "本年度所填信息" in row_str:
                found_current_year = True
                continue
            
            # 如果找到了"本年度所填信息"，再查找表头行
            if found_current_year:
                # 简单匹配：包含"论文/论著/译著名称"的行就是表头
                if "论文/论著/译著名称" in row_str:
                    header_row_idx = i
                    # 简单匹配各列索引
                    for k, cell in enumerate(row):
                        cell_str = str(cell).strip()
                        if "年度" in cell_str:
                            year_idx = k
                        elif "论文/论著/译著名称" in cell_str:
                            name_idx = k
                        elif "发表时间" in cell_str:
                            time_idx = k
                        elif "刊物名称/期号/出版单位/学术会议名称" in cell_str:
                            pub_idx = k
                        elif "总章节数或总字数" in cell_str:
                            length_idx = k
                        elif "独立撰写/合作撰写/本人排名" in cell_str:
                            role_idx = k
                    break
        
        # 如果找到了表头，开始提取数据
        if header_row_idx >= 0 and name_idx >= 0:
            # 从表头下一行开始提取数据
            for i in range(header_row_idx + 1, len(all_rows)):
                data_row = all_rows[i]
                row_str = "".join(str(cell) for cell in data_row)
                
                # 遇到下一个标记时停止
                if any(marker in row_str for marker in ["取得专利", "其他业绩成果", "工作经历", "发表论文"]):
                    break
                
                # 只跳过明显的表头行和空行
                if "论文/论著/译著名称" in row_str or row_str.strip() == "" or row_str.strip() == "无":
                    continue
                
                # 提取数据
                paper_item = {
                    "年度": current_year,  # 直接使用当前年份
                    "论文/论著/译著名称": "",
                    "发表时间": "",
                    "刊物名称/期号/出版单位/学术会议名称": "",
                    "总章节数或总字数": "",
                    "独立撰写/合作撰写/本人排名": ""
                }
                
                if name_idx >= 0 and name_idx < len(data_row):
                    paper_item["论文/论著/译著名称"] = str(data_row[name_idx]).strip()
                if time_idx >= 0 and time_idx < len(data_row):
                    paper_item["发表时间"] = str(data_row[time_idx]).strip()
                if pub_idx >= 0 and pub_idx < len(data_row):
                    paper_item["刊物名称/期号/出版单位/学术会议名称"] = str(data_row[pub_idx]).strip()
                if length_idx >= 0 and length_idx < len(data_row):
                    paper_item["总章节数或总字数"] = str(data_row[length_idx]).strip()
                if role_idx >= 0 and role_idx < len(data_row):
                    paper_item["独立撰写/合作撰写/本人排名"] = str(data_row[role_idx]).strip()
                
                # 只要有论文名称就添加
                if paper_item["论文/论著/译著名称"]:
                    papers_list.append(paper_item)
    
    # 五、取得专利技术标准（"取得专利/技术标准-B5"后面）
    patents_list = []
    
    patents_start_idx = -1
    for i, row in enumerate(all_rows):
        if any("取得专利" in str(cell) and "B5" in str(cell) for cell in row):
            patents_start_idx = i
            break
    
    if patents_start_idx >= 0:
        header_row_idx = -1
        for i in range(patents_start_idx + 1, min(patents_start_idx + 10, len(all_rows))):
            row = all_rows[i]
            row_str = "".join(str(cell) for cell in row)
            if "专利" in row_str or "技术标准" in row_str:
                header_row_idx = i
                type_idx = -1
                name_idx = -1
                role_idx = -1
                time_idx = -1
                org_idx = -1
                stage_idx = -1
                
                for k, cell in enumerate(row):
                    cell_str = str(cell)
                    if "类型" in cell_str:
                        type_idx = k
                    elif "名称" in cell_str:
                        name_idx = k
                    elif "角色" in cell_str:
                        role_idx = k
                    elif "时间" in cell_str:
                        time_idx = k
                    elif "机构" in cell_str or "授予" in cell_str or "颁布" in cell_str:
                        org_idx = k
                    elif "阶段" in cell_str or "状态" in cell_str:
                        stage_idx = k
                
                for i in range(header_row_idx + 1, len(all_rows)):
                    data_row = all_rows[i]
                    row_str = "".join(str(cell) for cell in data_row)
                    if any(marker in row_str for marker in ["其他业绩成果", "工作经历"]):
                        break
                    
                    # 跳过表头行（包含表头关键词）
                    if any(keyword in row_str for keyword in ["专利/技术标准类型", "专利/技术标准名称", "角色", "授予颁布机构", "目前所处阶段"]):
                        continue
                    
                    if not any(str(cell).strip() for cell in data_row):
                        continue
                    
                    patent_item = {
                        "年度": current_year,  # 使用当前年份
                        "专利/技术标准类型": "",
                        "专利/技术标准名称": "",
                        "角色": "",
                        "时间": "",
                        "授予颁布机构": "",
                        "目前所处阶段": ""
                    }
                    
                    if type_idx >= 0 and type_idx < len(data_row):
                        patent_item["专利/技术标准类型"] = str(data_row[type_idx]).strip()
                    if name_idx >= 0 and name_idx < len(data_row):
                        patent_item["专利/技术标准名称"] = str(data_row[name_idx]).strip()
                    if role_idx >= 0 and role_idx < len(data_row):
                        patent_item["角色"] = str(data_row[role_idx]).strip()
                    if time_idx >= 0 and time_idx < len(data_row):
                        patent_item["时间"] = str(data_row[time_idx]).strip()
                    if org_idx >= 0 and org_idx < len(data_row):
                        patent_item["授予颁布机构"] = str(data_row[org_idx]).strip()
                    if stage_idx >= 0 and stage_idx < len(data_row):
                        patent_item["目前所处阶段"] = str(data_row[stage_idx]).strip()
                    
                    if patent_item["专利/技术标准名称"]:
                        patents_list.append(patent_item)
                break
    
    # 六、其他业绩成果（"其他业绩成果-B6"后面）
    achievements_list = []
    
    achievements_start_idx = -1
    for i, row in enumerate(all_rows):
        if any("其他业绩成果" in str(cell) and "B6" in str(cell) for cell in row):
            achievements_start_idx = i
            break
    
    if achievements_start_idx >= 0:
        header_row_idx = -1
        for i in range(achievements_start_idx + 1, min(achievements_start_idx + 10, len(all_rows))):
            row = all_rows[i]
            row_str = "".join(str(cell) for cell in row)
            if "年度" in row_str or "业绩成果" in row_str:
                header_row_idx = i
                year_idx = -1
                type_idx = -1
                name_idx = -1
                role_idx = -1
                time_idx = -1
                org_idx = -1
                status_idx = -1
                
                for k, cell in enumerate(row):
                    cell_str = str(cell)
                    if "年度" in cell_str:
                        year_idx = k
                    elif "类型" in cell_str:
                        type_idx = k
                    elif "名称" in cell_str:
                        name_idx = k
                    elif "角色" in cell_str or "排名" in cell_str:
                        role_idx = k
                    elif "完成时间" in cell_str or "时间" in cell_str:
                        time_idx = k
                    elif "应用机构" in cell_str or "领域" in cell_str:
                        org_idx = k
                    elif "应用状态" in cell_str or "状态" in cell_str:
                        status_idx = k
                
                for i in range(header_row_idx + 1, len(all_rows)):
                    data_row = all_rows[i]
                    row_str = "".join(str(cell) for cell in data_row)
                    # 在"专业技术工作-C1"前停止
                    if any(marker in row_str for marker in ["专业技术工作", "C1"]):
                        break
                    
                    # 跳过表头行（包含表头关键词）
                    if any(keyword in row_str for keyword in ["年度", "业绩成果类型", "业绩成果名称", "本人角色排名", "完成时间", "应用机构领域", "目前应用状态"]):
                        continue
                    
                    if not any(str(cell).strip() for cell in data_row):
                        continue
                    
                    achievement_item = {
                        "年度": current_year,
                        "业绩成果类型": "",
                        "业绩成果名称": "",
                        "本人角色排名": "",
                        "完成时间": "",
                        "应用机构领域": "",
                        "目前应用状态": ""
                    }
                    
                    if year_idx >= 0 and year_idx < len(data_row):
                        year_str = str(data_row[year_idx]).strip()
                        if year_str and year_str.isdigit():
                            year = int(year_str)
                            if year in [2025, 2026]:
                                achievement_item["年度"] = year
                    if type_idx >= 0 and type_idx < len(data_row):
                        achievement_item["业绩成果类型"] = str(data_row[type_idx]).strip()
                    if name_idx >= 0 and name_idx < len(data_row):
                        achievement_item["业绩成果名称"] = str(data_row[name_idx]).strip()
                    if role_idx >= 0 and role_idx < len(data_row):
                        achievement_item["本人角色排名"] = str(data_row[role_idx]).strip()
                    if time_idx >= 0 and time_idx < len(data_row):
                        achievement_item["完成时间"] = str(data_row[time_idx]).strip()
                    if org_idx >= 0 and org_idx < len(data_row):
                        achievement_item["应用机构领域"] = str(data_row[org_idx]).strip()
                    if status_idx >= 0 and status_idx < len(data_row):
                        achievement_item["目前应用状态"] = str(data_row[status_idx]).strip()
                    
                    if achievement_item["业绩成果名称"]:
                        achievements_list.append(achievement_item)
                break
    
    # 组装结果
    result = {
        "人员基本信息": basic_info,
        "职称申报继续教育": continue_education_list,
        "职称申报基础信息": title_app_info,
        "发表论文专著编著": papers_list,
        "取得专利技术标准": patents_list,
        "其他业绩成果": achievements_list
    }
    
    return result

def load_config_from_txt(config_path):
    """从TXT配置文件读取配置，格式：key=value，支持#注释和空行"""
    config = {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                # 解析 key=value 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 去掉引号（如果有）
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    config[key] = value
    except Exception as e:
        print(f"读取配置文件时出错: {str(e)}")
        return None
    return config

# 运行示例（从配置文件读取路径）
if __name__ == "__main__":
    # 获取exe或脚本所在目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # 如果是Python脚本
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 配置文件路径（exe或脚本同级目录）
    config_path = os.path.join(base_dir, "config.txt")
    if not os.path.exists(config_path):
        print(f"✗ 错误: 配置文件不存在: {config_path}")
        print("请在同级目录创建config.txt文件，格式如下：")
        print('input_folder=输入文件夹路径（必填）')
        print('output_folder=输出文件夹路径（必填）')
        print('template_path=Excel模板文件路径（可选，不填则跳过Excel写入）')
        print('processed_folder=已处理PDF文件夹路径（可选，不填则不移动PDF文件）')
        print('json_output_folder=JSON输出文件夹路径（可选，不填则保存到exe同级目录）')
        print('')
        print('说明：')
        print('  - 每行一个配置项，格式为 key=value')
        print('  - 支持使用 # 开头添加注释')
        print('  - 支持空行')
        exit(1)
    
    try:
        config = load_config_from_txt(config_path)
        if config is None:
            print("✗ 错误: 读取配置文件失败")
            exit(1)
        
        input_folder = config.get("input_folder", "").strip()
        output_folder = config.get("output_folder", "").strip()
        template_path = config.get("template_path", "").strip()
        processed_folder = config.get("processed_folder", "").strip()
        json_output_folder = config.get("json_output_folder", "").strip()
        
        if not input_folder or not output_folder:
            print("✗ 错误: 配置文件中缺少必要的路径配置")
            print("必须配置: input_folder 和 output_folder")
            exit(1)
        
        # 确保输出文件夹存在
        os.makedirs(output_folder, exist_ok=True)
        
        # 确保已处理文件夹存在（如果配置了）
        if processed_folder:
            os.makedirs(processed_folder, exist_ok=True)
            print(f"✓ 已处理文件夹: {processed_folder}")
        
        # 确定JSON输出文件夹路径
        if json_output_folder:
            # 使用配置的JSON输出文件夹
            json_output_dir = json_output_folder
            os.makedirs(json_output_dir, exist_ok=True)
            print(f"✓ JSON输出文件夹: {json_output_dir}")
        else:
            # 使用默认路径（exe或脚本同级目录）
            if getattr(sys, 'frozen', False):
                json_output_dir = os.path.dirname(sys.executable)
            else:
                json_output_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"✓ JSON输出文件夹: {json_output_dir} (默认路径)")
        
        # 检查模板文件路径
        if not template_path:
            print("⚠ 提示: 未配置模板文件路径（template_path）")
            print("将跳过Excel写入步骤，只生成JSON文件")
            template_path = None
        elif not os.path.exists(template_path):
            print(f"✗ 警告: 模板文件不存在: {template_path}")
            print("请检查配置文件中的 template_path 路径是否正确")
            print("将跳过Excel写入步骤，只生成JSON文件")
            template_path = None
        else:
            print(f"✓ 模板文件路径: {template_path}")
        
        # 获取输入文件夹中的所有PDF文件
        pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"✗ 在输入文件夹中未找到PDF文件: {input_folder}")
            exit(0)
        
        print(f"找到 {len(pdf_files)} 个PDF文件，开始处理...")
        print("=" * 60)
        
        # 处理每个PDF文件
        for pdf_file in pdf_files:
            pdf_file_path = os.path.join(input_folder, pdf_file)
            pdf_name = os.path.splitext(pdf_file)[0]  # 获取PDF文件名（不含扩展名）
            
            print(f"\n正在处理: {pdf_file}")
            print("-" * 60)
            
            # 第一步：处理PDF文件，生成"提取的表格数据.json"
            print("第一步：处理PDF文件，提取表格数据...")
            # JSON文件保存到配置的路径或默认路径
            extracted_json_path = os.path.join(json_output_dir, f"{pdf_name}_提取的表格数据.json")
            main(pdf_file_path)
            
            # 将提取的表格数据移动到配置的路径
            if os.path.exists("提取的表格数据.json"):
                shutil.move("提取的表格数据.json", extracted_json_path)
                print(f"已保存提取的表格数据到: {extracted_json_path}")
            
            # 第二步：解析"提取的表格数据.json"，生成"解析后的数据.json"
            print("\n第二步：解析表格数据JSON，生成解析后的数据...")
            
            # 等待一下，确保文件已写入
            import time
            time.sleep(0.5)
            
            # JSON文件保存到配置的路径或默认路径
            parsed_json_path = os.path.join(json_output_dir, f"{pdf_name}_解析后的数据.json")
            
            parsed_data = parse_tables_json(extracted_json_path)
            if parsed_data:
                with open(parsed_json_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_data, f, ensure_ascii=False, indent=2)
                print(f"✓ 已将解析后的数据保存为: {parsed_json_path}")
                
                # 第三步：将解析后的数据写入Excel模板
                if template_path:
                    print("\n第三步：将解析后的数据写入Excel模板...")
                    
                    # 获取员工姓名
                    employee_name = parsed_data.get("人员基本信息", {}).get("姓名", "")
                    if not employee_name:
                        employee_name = parsed_data.get("职称申报基础信息", {}).get("姓名", "")
                    
                    # 如果还是没有姓名，使用PDF文件名
                    if not employee_name:
                        employee_name = pdf_name
                    
                    # 以员工姓名重命名文件，保存到输出文件夹
                    output_excel_path = os.path.join(output_folder, f"{employee_name}.xls")
                    
                    # 如果文件已存在，添加序号
                    counter = 1
                    while os.path.exists(output_excel_path):
                        output_excel_path = os.path.join(output_folder, f"{employee_name}_{counter}.xls")
                        counter += 1
                    
                    # 复制模板
                    shutil.copy2(template_path, output_excel_path)
                    print(f"已复制模板到: {output_excel_path}")
                    
                    # 写入JSON数据到第四行
                    write_json_to_excel(output_excel_path, parsed_data, row=3)
                    print(f"✓ 已将解析后的数据写入Excel第4行（文件名: {os.path.basename(output_excel_path)}）")
                
                # 处理成功后，将PDF文件移动到已处理文件夹
                if processed_folder:
                    try:
                        processed_pdf_path = os.path.join(processed_folder, pdf_file)
                        # 如果目标文件已存在，添加时间戳
                        if os.path.exists(processed_pdf_path):
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            name, ext = os.path.splitext(pdf_file)
                            processed_pdf_path = os.path.join(processed_folder, f"{name}_{timestamp}{ext}")
                        
                        shutil.move(pdf_file_path, processed_pdf_path)
                        print(f"✓ 已将PDF文件移动到已处理文件夹: {os.path.basename(processed_pdf_path)}")
                    except Exception as e:
                        print(f"⚠ 警告: 移动PDF文件到已处理文件夹失败: {str(e)}")
            else:
                print("✗ 解析失败，请检查提取的表格数据文件是否存在")
                print("⚠ PDF文件保留在原文件夹，可重新处理")
        
        print("\n" + "=" * 60)
        print(f"✓ 处理完成！共处理 {len(pdf_files)} 个文件")
        print(f"输出文件夹: {output_folder}")
        
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)