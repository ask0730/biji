import json
import PyPDF2
import re
import os
import shutil
from datetime import datetime
try:
    import xlrd
    import xlwt
    from xlutils.copy import copy as xl_copy
    HAS_XL_LIBS = True
except ImportError:
    HAS_XL_LIBS = False
    print("警告: 未安装xlrd、xlwt和xlutils库，将无法写入Excel文件")

def extract_pdf_text(pdf_path):
    """读取PDF文件文本内容"""
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def parse_basic_info(text):
    """解析人员基本信息（第一部分JSON）"""
    basic_info = {
        "姓名": "",
        "证件类型": "身份证",
        "证件号码": "",
        "所属组织": "首都图书馆"
    }
    
    # 提取姓名（尝试多种模式）
    # 模式1: 姓名 后面跟中文名字（2-4个中文字符），然后可能是性别或其他
    name_patterns = [
        r'姓名\s*[:：]?\s*([\u4e00-\u9fa5]{2,4})',  # 姓名: 张三 或 姓名 张三
        r'姓名\s+([\u4e00-\u9fa5]{2,4})',  # 姓名 张三
        r'姓名\s+(\S+?)(?:\s+[男女]|\s+性别|\s+出生|$)',  # 姓名 张三 女 或 姓名 张三
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, text)
        if name_match:
            name = name_match.group(1).strip()
            # 验证是否是合理的姓名（2-4个中文字符）
            if re.match(r'^[\u4e00-\u9fa5]{2,4}$', name):
                basic_info["姓名"] = name
                break
    
    # 提取证件号码（身份证号码：18位或15位数字，可能带X）
    id_patterns = [
        r'证件号码\s*[:：]?\s*([0-9Xx]{15,18})',  # 证件号码: 123456789012345678
        r'身份证号\s*[:：]?\s*([0-9Xx]{15,18})',  # 身份证号: 123456789012345678
        r'身份证\s*[:：]?\s*([0-9Xx]{15,18})',  # 身份证: 123456789012345678
        r'([0-9]{17}[0-9Xx])',  # 18位身份证（最后一位可能是X）
    ]
    
    for pattern in id_patterns:
        id_match = re.search(pattern, text)
        if id_match:
            id_number = id_match.group(1).strip().upper()
            # 验证身份证号码格式
            if len(id_number) in [15, 18] and (id_number.isdigit() or (len(id_number) == 18 and id_number[-1] in 'X0123456789')):
                basic_info["证件号码"] = id_number
                break
    
    return basic_info

def parse_continue_education(text):
    """解析自定义子集02（继续教育信息，第二部分JSON）"""
    education_list = []
    
    # 年度使用当前年份（今年）
    current_year = datetime.now().year
    
    # 找到"继续教育-A4"和"工作经历-A5"的位置，只在这之间提取
    section_start = text.find("继续教育-A4")
    section_end = text.find("工作经历-A5")
    
    if section_start == -1:
        print("未找到'继续教育-A4'标记")
        # 如果没有找到标记，使用整个文本
        section_text = text
    elif section_end == -1:
        print("未找到'工作经历-A5'标记，使用到文本末尾")
        section_text = text[section_start:]
    else:
        # 提取"继续教育-A4"之后到"工作经历-A5"之前的内容
        section_text = text[section_start:section_end]
        print(f"找到继续教育部分，从位置 {section_start} 到 {section_end}")
    
    # 在指定范围内查找所有日期对（起始时间 结束时间）
    date_pattern = r'(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})'
    date_matches = list(re.finditer(date_pattern, section_text))
    
    print(f"在继续教育部分找到 {len(date_matches)} 个日期对")
    
    if not date_matches:
        return education_list
    
    # 对每个日期对提取信息
    for date_idx, date_match in enumerate(date_matches):
        try:
            start_time = date_match.group(1)
            end_time = date_match.group(2)
            
            start_pos = date_match.start()
            end_pos = date_match.end()
            
            # 找到包含当前日期对的那一行（在section_text中查找）
            # 计算在section_text中的相对位置
            date_match_in_section = re.search(rf'{re.escape(start_time)}\s+{re.escape(end_time)}', section_text)
            if not date_match_in_section:
                continue
            
            rel_start_pos = date_match_in_section.start()
            rel_end_pos = date_match_in_section.end()
            
            # 向前查找换行符，确定行的开始位置
            line_start = section_text.rfind('\n', 0, rel_start_pos)
            if line_start == -1:
                line_start = 0
            else:
                line_start += 1  # 跳过换行符
            
            # 向后查找换行符，确定行的结束位置
            line_end = section_text.find('\n', rel_end_pos)
            if line_end == -1:
                line_end = len(section_text)
            
            # 提取整行内容
            line_text = section_text[line_start:line_end].strip()
            
            # 为了处理跨行的组织单位，也获取下一行内容
            next_line_start = line_end + 1 if line_end < len(section_text) else len(section_text)
            next_line_end = section_text.find('\n', next_line_start)
            if next_line_end == -1:
                next_line_end = len(section_text)
            next_line_text = section_text[next_line_start:next_line_end].strip()
            
            # 合并当前行和下一行，用于提取可能跨行的组织单位
            combined_text = line_text + " " + next_line_text if next_line_text else line_text
            
            # 打印调试信息：显示整行内容和下一行
            print(f"日期对 {date_idx + 1} 所在行: {line_text[:200]}...")
            if next_line_text:
                print(f"日期对 {date_idx + 1} 下一行: {next_line_text[:200]}...")
            
            # 按行结构提取字段：尝试按多个空格或制表符分割
            # 方法1: 按多个空格分割（表格通常用多个空格分隔列）
            parts = re.split(r'\s{2,}|\t+', line_text)  # 2个或更多空格，或制表符
            parts = [p.strip() for p in parts if p.strip()]
            
            # 如果分割后的部分数量足够，按位置提取字段
            org_unit = ""
            content = ""
            form = "其他"
            hours = 0.0
            exam_result = ""
            
            # 查找日期对在parts中的位置
            # 日期对可能是分开的两个部分，或者合并在一起
            date_idx_in_parts = -1
            for i, part in enumerate(parts):
                if start_time in part and end_time in part:
                    # 日期对在同一个part中
                    date_idx_in_parts = i
                    break
                elif i < len(parts) - 1 and start_time in part and end_time in parts[i + 1]:
                    # 日期对分开在两个part中
                    date_idx_in_parts = i
                    break
            
            # 如果找到了日期对的位置，按列位置提取字段
            # 格式：起始时间 结束时间 组织单位 学习内容 学习形式 学时 考试结果
            if date_idx_in_parts >= 0:
                # 检查日期对是否分开在两个part中
                if start_time in parts[date_idx_in_parts] and end_time in parts[date_idx_in_parts]:
                    # 日期对在同一个part中，下一个part是组织单位
                    if len(parts) > date_idx_in_parts + 1:
                        org_unit = parts[date_idx_in_parts + 1]
                    if len(parts) > date_idx_in_parts + 2:
                        content = parts[date_idx_in_parts + 2]
                    if len(parts) > date_idx_in_parts + 3:
                        form = parts[date_idx_in_parts + 3]
                    if len(parts) > date_idx_in_parts + 4:
                        hours_str = parts[date_idx_in_parts + 4]
                        try:
                            hours = float(hours_str)
                        except:
                            hours = 0.0
                    if len(parts) > date_idx_in_parts + 5:
                        exam_result = parts[date_idx_in_parts + 5]
                elif date_idx_in_parts < len(parts) - 1 and end_time in parts[date_idx_in_parts + 1]:
                    # 日期对分开在两个part中，下下个part是组织单位
                    if len(parts) > date_idx_in_parts + 2:
                        org_unit = parts[date_idx_in_parts + 2]
                    if len(parts) > date_idx_in_parts + 3:
                        content = parts[date_idx_in_parts + 3]
                    if len(parts) > date_idx_in_parts + 4:
                        form = parts[date_idx_in_parts + 4]
                    if len(parts) > date_idx_in_parts + 5:
                        hours_str = parts[date_idx_in_parts + 5]
                        try:
                            hours = float(hours_str)
                        except:
                            hours = 0.0
                    if len(parts) > date_idx_in_parts + 6:
                        exam_result = parts[date_idx_in_parts + 6]
            
            # 如果按列位置提取失败，使用正则表达式从整行中提取（包括跨行情况）
            if not org_unit:
                # 在结束时间之后查找组织单位（先从合并文本中查找，支持跨行）
                org_keywords = ['图书馆', '学会', '学院', '大学', '中心', '研究院', '所', '馆', '部', '处', '网络学院', '委员会', '协会', '局', '公司', '集团']
                org_keywords_pattern = '|'.join(org_keywords)
                
                # 方法1: 从合并文本中查找（支持跨行）
                org_pattern = rf'{re.escape(end_time)}\s+([\u4e00-\u9fa5\s]+?(?:{org_keywords_pattern}))'
                org_match = re.search(org_pattern, combined_text)
                if org_match:
                    org_unit = org_match.group(1).strip()
                    # 如果组织单位包含换行符或空格，清理它
                    org_unit = re.sub(r'\s+', '', org_unit)  # 移除所有空格和换行
                    # 限制长度，避免包含其他字段
                    if len(org_unit) > 50:
                        # 找到第一个组织单位关键词的位置
                        for keyword in org_keywords:
                            idx = org_unit.find(keyword)
                            if idx != -1:
                                # 提取关键词前后各15个字符
                                start_idx = max(0, idx - 15)
                                end_idx = min(len(org_unit), idx + len(keyword) + 15)
                                org_unit = org_unit[start_idx:end_idx]
                                break
                
                # 方法2: 如果方法1失败，尝试从当前行中查找
                if not org_unit:
                    org_pattern = rf'{re.escape(end_time)}\s+([\u4e00-\u9fa5]+?(?:{org_keywords_pattern}))'
                    org_match = re.search(org_pattern, line_text)
                    if org_match:
                        org_unit = org_match.group(1).strip()
                    else:
                        # 尝试提取2-50个字符的中文（增加长度限制以支持跨行）
                        org_patterns = [
                            rf'{re.escape(end_time)}\s+([\u4e00-\u9fa5\s]{{2,50}})',
                            rf'{re.escape(end_time)}\s+([^\n\d\s]{{2,50}})',
                        ]
                        for pattern in org_patterns:
                            org_match = re.search(pattern, combined_text)
                            if org_match:
                                potential_org = org_match.group(1).strip()
                                # 清理空格和换行
                                potential_org = re.sub(r'\s+', '', potential_org)
                                # 检查是否包含组织单位关键词
                                if any(kw in potential_org for kw in org_keywords):
                                    org_unit = potential_org
                                    # 限制长度
                                    if len(org_unit) > 50:
                                        for keyword in org_keywords:
                                            idx = org_unit.find(keyword)
                                            if idx != -1:
                                                start_idx = max(0, idx - 15)
                                                end_idx = min(len(org_unit), idx + len(keyword) + 15)
                                                org_unit = org_unit[start_idx:end_idx]
                                                break
                                    break
                
                # 方法3: 如果组织单位可能在下一行，从下一行中查找
                if not org_unit and next_line_text:
                    # 下一行如果包含组织单位关键词，可能是组织单位的延续
                    for keyword in org_keywords:
                        if keyword in next_line_text:
                            # 提取包含关键词的部分
                            idx = next_line_text.find(keyword)
                            start_idx = max(0, idx - 20)
                            end_idx = min(len(next_line_text), idx + len(keyword) + 20)
                            potential_org = next_line_text[start_idx:end_idx].strip()
                            # 清理空格
                            potential_org = re.sub(r'\s+', '', potential_org)
                            if len(potential_org) >= 2 and len(potential_org) <= 50:
                                org_unit = potential_org
                                break
            
            # 如果组织单位太长（超过30个字符），可能包含了学习内容，需要分割
            if org_unit and len(org_unit) > 30:
                # 查找组织单位关键词的位置，截取到第一个关键词结束
                for keyword in org_keywords:
                    if keyword in org_unit:
                        idx = org_unit.find(keyword)
                        # 组织单位通常在关键词前后10个字符内
                        start_idx = max(0, idx - 10)
                        end_idx = idx + len(keyword)
                        potential_org = org_unit[start_idx:end_idx]
                        # 如果提取的部分包含完整的组织单位关键词，使用它
                        if any(kw in potential_org for kw in org_keywords):
                            org_unit = potential_org.strip()
                            break
                # 如果还是太长，尝试按空格分割
                if len(org_unit) > 30:
                    parts = org_unit.split()
                    if len(parts) >= 2:
                        # 找到包含组织单位关键词的部分
                        for part in parts:
                            if any(kw in part for kw in org_keywords):
                                org_unit = part
                                break
                        else:
                            org_unit = parts[0]  # 第一部分作为组织单位
            
            # 如果按列位置提取失败，使用正则表达式从整行中提取学习内容
            if not content:
                if org_unit:
                    # 在组织单位之后查找学习内容
                    after_org = line_text[line_text.find(org_unit) + len(org_unit):] if org_unit in line_text else line_text
                    content_patterns = [
                        r'\s+([\u4e00-\u9fa5]{2,100})',
                        r'\s+([^\n\d\s]{2,100})',
                    ]
                    for pattern in content_patterns:
                        content_match = re.search(pattern, after_org)
                        if content_match:
                            content = content_match.group(1).strip()
                            # 如果学习内容太长，可能包含了其他字段，需要截断
                            if len(content) > 80:
                                form_pos = len(content)
                                for form_keyword in ['其他', '网络专题培训', '线上讲座', '面授', '在线学习', '自学']:
                                    pos = content.find(form_keyword)
                                    if pos != -1 and pos < form_pos:
                                        form_pos = pos
                                num_match = re.search(r'\d+(?:\.\d+)?', content)
                                if num_match and num_match.start() < form_pos:
                                    form_pos = num_match.start()
                                if form_pos < len(content):
                                    content = content[:form_pos].strip()
                            break
                else:
                    # 如果没有组织单位，尝试直接提取学习内容
                    content_patterns = [
                        rf'{re.escape(end_time)}\s+[\u4e00-\u9fa5]{{2,20}}\s+([\u4e00-\u9fa5]{{2,100}})',
                        rf'{re.escape(end_time)}\s+([\u4e00-\u9fa5]{{2,100}})',
                    ]
                    for pattern in content_patterns:
                        content_match = re.search(pattern, line_text)
                        if content_match:
                            if content_match.lastindex >= 2:
                                content = content_match.group(2).strip()
                            elif content_match.lastindex >= 1:
                                content = content_match.group(1).strip()
                            break
            
            # 如果按列位置提取失败，使用正则表达式从整行中提取学习形式
            # 学习形式通常是"其他"或"面授"等
            if form == "其他":
                # 在组织单位和学习内容之后查找学习形式
                search_text = line_text
                if org_unit:
                    org_pos = search_text.find(org_unit)
                    if org_pos != -1:
                        search_text = search_text[org_pos + len(org_unit):]
                if content:
                    content_pos = search_text.find(content)
                    if content_pos != -1:
                        search_text = search_text[content_pos + len(content):]
                
                form_patterns = [
                    r'(其他)',
                    r'(面授)',
                    r'(网络专题培训)',
                    r'(线上讲座)',
                    r'(在线学习)',
                    r'(自学)',
                ]
                for pattern in form_patterns:
                    form_match = re.search(pattern, search_text)
                    if form_match:
                        form = form_match.group(1)
                        break
            
            # 简化学时提取：从当前行中查找大于0的数字（排除日期）
            # 学时就是大于0的数字，在继续教育-A4后面，工作经历-A5前面
            if hours == 0.0:
                # 替换日期格式为占位符，避免提取日期中的数字
                temp_text = line_text
                temp_text = re.sub(r'\d{4}-\d{2}-\d{2}', 'DATE', temp_text)
                
                # 查找所有数字（包括小数）
                all_numbers = re.findall(r'(\d+(?:\.\d+)?)', temp_text)
                
                # 选择第一个大于0的数字作为学时
                for num_str in all_numbers:
                    try:
                        num = float(num_str)
                        if num > 0:
                            hours = num
                            break
                    except:
                        continue
                
                # 如果当前行没找到，尝试从下一行中查找
                if hours == 0.0 and next_line_text:
                    next_temp_text = re.sub(r'\d{4}-\d{2}-\d{2}', 'DATE', next_line_text)
                    next_numbers = re.findall(r'(\d+(?:\.\d+)?)', next_temp_text)
                    for num_str in next_numbers:
                        try:
                            num = float(num_str)
                            if num > 0:
                                hours = num
                                break
                        except:
                            continue
            
            # 如果按列位置提取失败，使用正则表达式从整行中提取考试考核结果
            # 考试结果通常是"合格"或"不合格"，在学时之后
            if not exam_result:
                # 在学时之后查找考试结果
                search_text = line_text
                if hours > 0:
                    hours_str = str(int(hours)) if hours == int(hours) else str(hours)
                    hours_pos = search_text.find(hours_str)
                    if hours_pos != -1:
                        search_text = search_text[hours_pos + len(hours_str):]
                
                result_patterns = [
                    r'(合格)',
                    r'(不合格)',
                    r'(通过)',
                    r'(未通过)',
                    r'(优秀)',
                    r'(良好)',
                    r'(及格)',
                ]
                for pattern in result_patterns:
                    result_match = re.search(pattern, search_text)
                    if result_match:
                        exam_result = result_match.group(1)
                        break
                
                # 如果还没找到，在整个行中查找
                if not exam_result:
                    for pattern in result_patterns:
                        result_match = re.search(pattern, line_text)
                        if result_match:
                            exam_result = result_match.group(1)
                            break
            
            # 年度使用当前年份（今年）
            year = current_year
            
            
            # 打印调试信息
            print(f"日期对 {date_idx + 1}: {start_time} - {end_time}, 组织单位: {org_unit}, 学习内容: {content}, 学时: {hours}, 考试结果: {exam_result}")
            
            # 如果学时为0，跳过这条记录（不添加）
            if hours == 0.0:
                print(f"警告: 日期对 {date_idx + 1} 的学时为0，跳过此条记录")
                continue
            
            # 移除所有过滤条件：直接添加所有找到的日期对作为继续教育记录
            edu_info = {
                "年度": year,
                "起始时间": start_time,
                "结束时间": end_time,
                "组织单位": org_unit,
                "学习内容": content,
                "学习形式": form,
                "学时": hours,
                "考试考核结果": exam_result
            }
            education_list.append(edu_info)
        except Exception as e:
            # 如果解析失败，打印错误但继续处理下一条
            print(f"解析继续教育记录失败: {str(e)}, 起始时间: {start_time if 'start_time' in locals() else 'N/A'}")
            continue
    
    return education_list

def parse_title_application(text):
    """解析职称申报基础信息（第三部分JSON）"""
    app_info = {
        "年度": datetime.now().year,  # 使用当前年份（今年）
        "级别": "",
        "申报专业技术资格": "",
        "手机号码": "",  # 文档中未提供，留空
        "证件号码": "",  # 文档中未提供，留空
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
    
    # 提取基础信息字段
    # 提取姓名（尝试多种模式，优先使用已提取的姓名）
    name_match = None
    name_patterns = [
        r'姓名\s*[:：]?\s*([\u4e00-\u9fa5]{2,4})',
        r'姓名\s+([\u4e00-\u9fa5]{2,4})',
        r'姓名\s+(\S+?)(?:\s+[男女]|\s+性别|\s+出生|$)',
    ]
    for pattern in name_patterns:
        name_match = re.search(pattern, text)
        if name_match:
            name = name_match.group(1).strip()
            if re.match(r'^[\u4e00-\u9fa5]{2,4}$', name):
                break
    
    # 提取性别（从姓名后面提取）
    gender_match = re.search(r'姓名\s+[\u4e00-\u9fa5]{2,4}\s+([男女])', text)
    if not gender_match:
        gender_match = re.search(r'性别\s*[:：]?\s*([男女])', text)
    # 提取手机号码（11位数字，可能包含空格或横线）
    mobile_patterns = [
        r'手机号码\s*[:：]?\s*([0-9]{11})',
        r'手机号\s*[:：]?\s*([0-9]{11})',
        r'手机\s*[:：]?\s*([0-9]{11})',
        r'联系电话\s*[:：]?\s*([0-9]{11})',
        r'电话\s*[:：]?\s*([0-9]{11})',
        r'([0-9]{3}[-\s]?[0-9]{4}[-\s]?[0-9]{4})',  # 带分隔符的手机号
        r'([0-9]{11})',  # 11位连续数字（需要验证）
    ]
    mobile_match = None
    for pattern in mobile_patterns:
        mobile_match = re.search(pattern, text)
        if mobile_match:
            mobile = mobile_match.group(1).replace('-', '').replace(' ', '').replace('\t', '')
            if len(mobile) == 11 and mobile.isdigit():
                break
    
    birth_match = re.search(r'出生年月\s*[:：]?\s*(\d{4}-\d{2}-\d{2})', text)
    if not birth_match:
        birth_match = re.search(r'出生日期\s*[:：]?\s*(\d{4}-\d{2}-\d{2})', text)
    
    # 提取参加工作时间（多种格式）
    work_start_patterns = [
        r'参加工作时间\s*[:：]?\s*(\d{4}-\d{2}-\d{2})',
        r'参加工作时间\s*[:：]?\s*(\d{4}\.\d{2}\.\d{2})',
        r'参加工作时间\s*[:：]?\s*(\d{4}/\d{2}/\d{2})',
        r'参加工作时间\s*[:：]?\s*(\d{4}年\d{1,2}月\d{1,2}日)',
        r'参加工作时间\s*[:：]?\s*(\d{4}年\d{1,2}月)',
        r'参加工作时间\s*[:：]?\s*(\d{4}年)',
    ]
    work_start_match = None
    for pattern in work_start_patterns:
        work_start_match = re.search(pattern, text)
        if work_start_match:
            break
    
    # 提取从事申报专业工作年限（多种格式）
    work_years_patterns = [
        r'从事申报专业\s*工作年限\s*[:：]?\s*(\d+)',
        r'从事申报专业工作年限\s*[:：]?\s*(\d+)',
        r'专业工作年限\s*[:：]?\s*(\d+)',
        r'工作年限\s*[:：]?\s*(\d+)',
        r'从事.*?专业.*?年限\s*[:：]?\s*(\d+)',
    ]
    work_years_match = None
    for pattern in work_years_patterns:
        work_years_match = re.search(pattern, text)
        if work_years_match:
            break
    
    nation_match = re.search(r'民族\s*[:：]?\s*(\S+)', text)
    current_major_match = re.search(r'现从事专业\s*[:：]?\s*(\S+)', text)
    academic_group_match = re.search(r'参加学术团体\s*及职务\s*[:：]?\s*(\S+)', text)
    if not academic_group_match:
        academic_group_match = re.search(r'参加学术团体及职务\s*[:：]?\s*(\S+)', text)
    
    work_unit_match = re.search(r'工作单位\s*[:：]?\s*(\S+)', text)
    insurance_unit_match = re.search(r'参保单位\s*[:：]?\s*(\S+)', text)
    department_match = re.search(r'所在部门\s*[:：]?\s*(\S+)', text)
    
    # 提取社会信用代码（18位统一社会信用代码，可能包含字母和数字）
    credit_code_patterns = [
        r'社会信用代码\s*[:：]?\s*([0-9A-Z]{18})',
        r'社会信用代码\s*[:：]?\s*([0-9A-Z]{15,18})',
        r'统一社会信用代码\s*[:：]?\s*([0-9A-Z]{18})',
        r'信用代码\s*[:：]?\s*([0-9A-Z]{18})',
        r'([0-9A-Z]{18})(?=\s|$)',  # 18位字母数字组合
    ]
    credit_code_match = None
    for pattern in credit_code_patterns:
        credit_code_match = re.search(pattern, text)
        if credit_code_match:
            break
    
    admin_job_match = re.search(r'行政职务\s*[:：]?\s*(\S+)', text)
    
    # 提取档案存放单位（多种格式）
    file_unit_patterns = [
        r'档案存放单位\s*[:：]?\s*([^\n]{2,50}?)(?:\s|$)',
        r'档案存放单位\s*[:：]?\s*(\S+)',
        r'档案单位\s*[:：]?\s*([^\n]{2,50}?)(?:\s|$)',
        r'档案\s*存放\s*单位\s*[:：]?\s*([^\n]{2,50}?)(?:\s|$)',
    ]
    file_unit_match = None
    for pattern in file_unit_patterns:
        file_unit_match = re.search(pattern, text)
        if file_unit_match:
            break
    
    hukou_match = re.search(r'户口所在地\s*[:：]?\s*(\S+)', text)
    
    # 提取个人申请字段
    level_match = re.search(r'级别\s+(\S+)', text)
    title_match = re.search(r'申报专业技术资格\s+(\S+)', text)
    
    # 赋值（匹配到则填充，未匹配到留空）
    if name_match:
        name = name_match.group(1).strip()
        if re.match(r'^[\u4e00-\u9fa5]{2,4}$', name):
            app_info["姓名"] = name
    
    if gender_match: 
        app_info["性别"] = gender_match.group(1)
    
    # 提取手机号码
    if mobile_match:
        mobile = mobile_match.group(1).replace('-', '').replace(' ', '').replace('\t', '')
        if len(mobile) == 11 and mobile.isdigit():
            app_info["手机号码"] = mobile
    
    # 提取证件号码（如果人员基本信息中没有提取到）
    if not app_info.get("证件号码"):
        id_patterns = [
            r'证件号码\s*[:：]?\s*([0-9Xx]{15,18})',
            r'身份证号\s*[:：]?\s*([0-9Xx]{15,18})',
            r'身份证\s*[:：]?\s*([0-9Xx]{15,18})',
            r'([0-9]{17}[0-9Xx])',
            r'([0-9]{15})',
        ]
        for pattern in id_patterns:
            id_match = re.search(pattern, text)
            if id_match:
                id_number = id_match.group(1).strip().upper()
                if len(id_number) in [15, 18] and (id_number.isdigit() or (len(id_number) == 18 and id_number[-1] in 'X0123456789')):
                    app_info["证件号码"] = id_number
                    break
    
    if birth_match: 
        app_info["出生年月"] = birth_match.group(1)
    
    if work_start_match: 
        work_start = work_start_match.group(1)
        # 统一格式为 YYYY-MM-DD
        work_start = work_start.replace('.', '-').replace('/', '-')
        work_start = re.sub(r'年|月|日', '-', work_start)
        work_start = re.sub(r'-+', '-', work_start).strip('-')
        app_info["参加工作时间"] = work_start
    
    if work_years_match: 
        app_info["从事申报专业工作年限"] = work_years_match.group(1)
    
    if nation_match: 
        app_info["民族"] = nation_match.group(1)
    
    if current_major_match: 
        app_info["现从事专业"] = current_major_match.group(1)
    
    if academic_group_match: 
        app_info["参加学术团体及职务"] = academic_group_match.group(1)
    
    if work_unit_match: 
        app_info["工作单位"] = work_unit_match.group(1)
    
    if insurance_unit_match: 
        app_info["参保单位"] = insurance_unit_match.group(1)
    
    if department_match: 
        app_info["所在部门"] = department_match.group(1)
    
    if credit_code_match: 
        credit_code = credit_code_match.group(1).strip().upper()
        if len(credit_code) >= 15:  # 统一社会信用代码通常是18位，但可能也有15位
            app_info["社会信用代码"] = credit_code
    
    if admin_job_match: 
        app_info["行政职务"] = admin_job_match.group(1)
    
    if file_unit_match: 
        file_unit = file_unit_match.group(1).strip()
        if file_unit:
            app_info["档案存放单位"] = file_unit
    
    if hukou_match: 
        app_info["户口所在地"] = hukou_match.group(1)
    if level_match: app_info["级别"] = level_match.group(1)
    if title_match: app_info["申报专业技术资格"] = title_match.group(1)
    
    return app_info

def parse_papers(text):
    """解析发表论文专著编著（第四部分JSON）"""
    papers_list = []
    # 文档中无相关数据，返回空列表（如需占位可添加空字典）
    # 若有数据，可使用以下模式匹配（示例）：
    # paper_pattern = r'(\S+)\s+(\d{4}-\d{2}-\d{2})\s+(\S+)\s+(\d+)\s+(\S+)'
    # matches = re.findall(paper_pattern, text)
    # for match in matches:
    #     paper_info = {
    #         "论文/论著/译著名称": match[0],
    #         "发表时间": match[1],
    #         "刊物名称/期号/出版单位/学术会议名称": match[2],
    #         "总章节数或总字数": match[3],
    #         "独立撰写/合作撰写/本人排名": match[4]
    #     }
    #     papers_list.append(paper_info)
    return papers_list

def parse_patents(text):
    """解析取得专利技术标准（第五部分JSON）"""
    patents_list = []
    # 文档中无相关数据，返回空列表
    return patents_list

def parse_other_achievements(text):
    """解析其他业绩成果（第六部分JSON）"""
    achievements_list = []
    # 文档中无相关数据，返回空列表（如需占位可添加空字典）
    # 若有数据，可参考以下格式添加：
    # achievement_info = {
    #     "年度": 2025,
    #     "业绩成果类型": "",
    #     "业绩成果名称": "",
    #     "本人角色排名": "",
    #     "完成时间": "",
    #     "应用机构领域": "",
    #     "目前应用状态": ""
    # }
    # achievements_list.append(achievement_info)
    return achievements_list

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
        
        # 从工作簿的格式列表中获取格式对象
        xf = None
        if hasattr(rb, 'format_list') and xf_index < len(rb.format_list):
            xf = rb.format_list[xf_index]
        elif hasattr(rb, 'format_map') and xf_index in rb.format_map:
            xf = rb.format_map[xf_index]
        
        if xf is None:
            return create_default_style()
        
        # 创建xlwt样式对象
        style = xlwt.XFStyle()
        
        # 复制字体信息，如果没有则使用默认（宋体12号）
        font = xlwt.Font()
        font.name = '宋体'
        font.height = 12 * 20  # 默认12号
        if hasattr(xf, 'font') and xf.font:
            font_info = xf.font
            if hasattr(font_info, 'height') and font_info.height:
                font.height = font_info.height
            if hasattr(font_info, 'bold'):
                font.bold = font_info.bold
            if hasattr(font_info, 'italic'):
                font.italic = font_info.italic
            if hasattr(font_info, 'name') and font_info.name:
                font.name = font_info.name
            if hasattr(font_info, 'colour_index'):
                font.colour_index = font_info.colour_index
        style.font = font
        
        # 复制对齐信息
        if hasattr(xf, 'alignment') and xf.alignment:
            alignment = xlwt.Alignment()
            align_info = xf.alignment
            if hasattr(align_info, 'horz'):
                alignment.horz = align_info.horz
            if hasattr(align_info, 'vert'):
                alignment.vert = align_info.vert
            if hasattr(align_info, 'wrap'):
                alignment.wrap = align_info.wrap
            style.alignment = alignment
        
        # 设置边框：确保所有边框都有线
        borders = xlwt.Borders()
        if hasattr(xf, 'border') and xf.border:
            border_info = xf.border
            borders.left = border_info.left if hasattr(border_info, 'left') and border_info.left else xlwt.Borders.THIN
            borders.right = border_info.right if hasattr(border_info, 'right') and border_info.right else xlwt.Borders.THIN
            borders.top = border_info.top if hasattr(border_info, 'top') and border_info.top else xlwt.Borders.THIN
            borders.bottom = border_info.bottom if hasattr(border_info, 'bottom') and border_info.bottom else xlwt.Borders.THIN
        else:
            # 如果没有边框信息，使用默认边框
            borders.left = xlwt.Borders.THIN
            borders.right = xlwt.Borders.THIN
            borders.top = xlwt.Borders.THIN
            borders.bottom = xlwt.Borders.THIN
        style.borders = borders
        
        # 复制背景色
        if hasattr(xf, 'background') and xf.background:
            pattern = xlwt.Pattern()
            bg_info = xf.background
            if hasattr(bg_info, 'fill_pattern'):
                pattern.pattern = bg_info.fill_pattern
            if hasattr(bg_info, 'pattern_colour_index'):
                pattern.pattern_fore_colour = bg_info.pattern_colour_index
            if hasattr(bg_info, 'background_colour_index'):
                pattern.pattern_back_colour = bg_info.background_colour_index
            style.pattern = pattern
        
        # 复制数字格式
        if hasattr(xf, 'format_key') and hasattr(rb, 'format_map'):
            format_key = xf.format_key
            if format_key in rb.format_map:
                num_format_str = rb.format_map[format_key].format_str
                style.num_format_str = num_format_str
        
        return style
    except Exception as e:
        # 如果获取格式失败，返回默认样式（宋体12号，有边框线）
        return create_default_style()

def write_json_to_excel(excel_path, json_data, row=4):
    """将JSON数据按照各个工作表的第二行字段映射写入Excel文件的指定行"""
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
            "自定义子集02": "自定义子集02（继续教育）",  # JSON中的键名包含"（继续教育）"
            "职称申报基础信息": "职称申报基础信息",
            "发表论文专著编著": "发表论文专著编著",
            "取得专利技术标准": "取得专利技术标准",
            "其他业绩成果": "其他业绩成果",
        }
        
        # 处理所有工作表
        for sheet_idx in range(len(rb.sheet_names())):
            sheet_name = rb.sheet_names()[sheet_idx]
            ws_read = rb.sheet_by_index(sheet_idx)
            ws_new = wb.get_sheet(sheet_idx)  # 获取可写的工作表对象
            
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
                
                print(f"工作表 '{sheet_name}' 字段数: {len(template_fields)}")
                
                # 获取参考行的样式（使用第三行作为参考，如果第三行不存在则使用第二行）
                ref_row = min(2, ws_read.nrows - 1) if ws_read.nrows > 0 else 0
                cell_styles = {}  # 缓存每列的样式
                
                # 处理数组类型的JSON数据（如自定义子集02）
                if isinstance(sheet_data, list):
                    # 对于数组，从第四行开始写入每条记录
                    start_row = row - 1  # 转换为0-based索引（第四行是索引3）
                    for record_idx, record in enumerate(sheet_data):
                        current_row = start_row + record_idx
                        for col_idx, template_field in enumerate(template_fields):
                            # 跳过前两列：导入信息、校验信息
                            if col_idx < 2:
                                continue
                            
                            # 直接从记录字典中提取值（record是字典类型）
                            value = ""
                            if isinstance(record, dict):
                                # 直接匹配字段名
                                if template_field in record:
                                    val = record[template_field]
                                    if val is not None and val != "":
                                        value = str(val)
                                else:
                                    # 尝试清理后的字段名匹配
                                    field_clean = template_field.replace("(ZH)", "").replace("（", "").replace("）", "").strip()
                                    if field_clean in record:
                                        val = record[field_clean]
                                        if val is not None and val != "":
                                            value = str(val)
                            
                            # 写入值（应用格式：宋体12号，有边框线）
                            if value:
                                # 获取或创建样式
                                if col_idx not in cell_styles:
                                    cell_styles[col_idx] = get_cell_style_from_template(rb, sheet_idx, ref_row, col_idx)
                                
                                # 总是使用样式（确保宋体12号，有边框线）
                                ws_new.write(current_row, col_idx, value, cell_styles[col_idx])
                    
                    if len(sheet_data) > 0:
                        print(f"  已写入 {len(sheet_data)} 条记录到工作表 '{sheet_name}' (行 {row} 到 {row + len(sheet_data) - 1})")
                        # 打印调试信息
                        print(f"  第一条记录示例: {sheet_data[0] if sheet_data else '无'}")
                else:
                    # 处理对象类型的JSON数据
                    for col_idx, template_field in enumerate(template_fields):
                        # 跳过前两列：导入信息、校验信息
                        if col_idx < 2:
                            continue
                        
                        # 根据模板字段名从JSON中提取对应的值
                        value = get_json_value_by_field(sheet_data, template_field, sheet_name)
                        
                        # 写入值（应用格式：宋体12号，有边框线）
                        if value:
                            # 获取或创建样式
                            if col_idx not in cell_styles:
                                cell_styles[col_idx] = get_cell_style_from_template(rb, sheet_idx, ref_row, col_idx)
                            
                            # 总是使用样式（确保宋体12号，有边框线）
                            ws_new.write(row-1, col_idx, value, cell_styles[col_idx])
                    
                    print(f"  已写入数据到工作表 '{sheet_name}' 第{row}行")
            else:
                print(f"  工作表 '{sheet_name}' 没有对应的JSON数据，跳过")
        
        # 保存文件
        wb.save(excel_path)
        print(f"\n成功将所有JSON数据按照模板字段映射写入Excel")
    except Exception as e:
        print(f"写入Excel时出错: {str(e)}")
        import traceback
        traceback.print_exc()

def main(pdf_path):
    """主函数：读取PDF并生成六个JSON"""
    # 1. 读取PDF文本
    pdf_text = extract_pdf_text(pdf_path)
    
    # 2. 解析各部分数据
    json1 = parse_basic_info(pdf_text)          # 人员基本信息
    json2 = parse_continue_education(pdf_text)  # 自定义子集02
    json3 = parse_title_application(pdf_text)   # 职称申报基础信息
    json4 = parse_papers(pdf_text)              # 发表论文专著编著
    json5 = parse_patents(pdf_text)             # 取得专利技术标准
    json6 = parse_other_achievements(pdf_text)  # 其他业绩成果
    
    # 3. 如果人员基本信息中没有姓名和证件号码，尝试从职称申报基础信息中获取
    if not json1.get("姓名") and json3.get("姓名"):
        json1["姓名"] = json3["姓名"]
    if not json1.get("证件号码") and json3.get("证件号码"):
        json1["证件号码"] = json3["证件号码"]
    
    # 4. 返回六个JSON（可选择打印或保存文件）
    result = {
        "人员基本信息": json1,
        "自定义子集02（继续教育）": json2,
        "职称申报基础信息": json3,
        "发表论文专著编著": json4,
        "取得专利技术标准": json5,
        "其他业绩成果": json6
    }
    
    # 打印格式化JSON（便于查看）
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # （可选）保存为JSON文件
    json_output_path = "职称申报数据.json"
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 将text输出为JSON文件
    text_json = {"text": pdf_text}
    text_json_path = "提取的文本.json"
    with open(text_json_path, "w", encoding="utf-8") as f:
        json.dump(text_json, f, ensure_ascii=False, indent=2)
    print(f"已将提取的文本保存为JSON文件: {text_json_path}")
    
    # 复制模板并写入JSON数据
    template_path = r"D:\Desktop\导入模版.xls"
    if os.path.exists(template_path):
        # 获取PDF文件名（不含扩展名）
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_excel_path = os.path.join(os.path.dirname(pdf_path), f"{pdf_name}.xls")
        
        # 复制模板
        shutil.copy2(template_path, output_excel_path)
        print(f"已复制模板到: {output_excel_path}")
        
        # 写入JSON数据到第四行
        write_json_to_excel(output_excel_path, result, row=4)
        print(f"已将JSON数据写入Excel第4行")
    else:
        print(f"警告: 模板文件不存在: {template_path}")
    
    return json1, json2, json3, json4, json5, json6

# 运行示例（需替换为实际PDF文件路径）
if __name__ == "__main__":
    pdf_file_path = "D:\Desktop\首图源文件\王雪屏.pdf"  # 请替换为你的PDF文件路径
    json1, json2, json3, json4, json5, json6 = main(pdf_file_path)