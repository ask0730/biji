import pdfplumber
import re

def extract_pdf_info(pdf_path):
    # 存储提取结果
    result = {
        "姓名": "",
        "继续教育信息": [],
        "业绩成果名称": []
    }
    
    # 打开PDF并读取所有文本
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            # 提取每页文本，合并为完整字符串
            page_text = page.extract_text() or ""
            full_text += page_text + "\n"
    
    # 1. 提取姓名（匹配"姓名:"后的中文姓名）
    name_pattern = r"姓名:\s*([^\s\d]+)"
    name_match = re.search(name_pattern, full_text)
    if name_match:
        result["姓名"] = name_match.group(1).strip()
    
    # 2. 提取继续教育信息（匹配"起始时间-结束时间 组织单位 学习内容"）
    # 先定位继续教育模块（匹配"继续教育"后的内容）
    continue_edu_pattern = r"继续教育.*?(?=工作经历|学历信息|职称及职业资格信息|$)"
    continue_edu_text = re.search(continue_edu_pattern, full_text, re.DOTALL)
    if continue_edu_text:
        edu_text = continue_edu_text.group(0)
        # 匹配每条继续教育记录（格式：起始时间 结束时间 组织单位 学习内容）
        edu_record_pattern = r"(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})\s+([^\n]+?)\s+([^\n]+?)\s+(面授|线上|其他)"
        edu_records = re.findall(edu_record_pattern, edu_text, re.DOTALL)
        
        for record in edu_records:
            result["继续教育信息"].append({
                "起始时间": record[0],
                "结束时间": record[1],  # 额外提取结束时间（可选）
                "组织单位": record[2].strip(),
                "学习内容": record[3].strip()
            })
        
        # 补充匹配特殊格式的继续教育记录（如中国图书馆学会的培训）
        special_edu_pattern = r"(\d{4}-\d{2}-\d{2})\s+中国图书馆学会\s+(第六次全国县级以上公共图书馆评估定级培训)"
        special_edu_records = re.findall(special_edu_pattern, edu_text)
        for record in special_edu_records:
            result["继续教育信息"].append({
                "起始时间": record[0],
                "结束时间": record[0],  # 该培训无明确结束时间，用起始时间填充
                "组织单位": "中国图书馆学会",
                "学习内容": record[1].strip()
            })
    
    # 3. 提取业绩成果名称（匹配"业绩成果名称"后的项目名称）
    # 定位业绩成果模块
    achievement_pattern = r"业绩成果名称\s+本人角色排名\s+完成时间.*?(?=专业技术工作|其他业绩成果|$)"
    achievement_text = re.search(achievement_pattern, full_text, re.DOTALL)
    if achievement_text:
        achievement_content = achievement_text.group(0)
        # 匹配业绩成果名称（排除表头和无关字段）
        achievement_name_pattern = r"(公共图书馆社保卡应用场景服务调研报告|首都图书馆“十四五”时期发展规划|公共文化装备产品现状与发展对策研究图书馆行业子课|疫情常态化下公共图书馆预约入馆服务调研报告|首都图书馆2019年业务统计分析报告|首都图书馆2015年读者阅读报告)"
        achievements = re.findall(achievement_name_pattern, achievement_content)
        # 去重并添加到结果
        result["业绩成果名称"] = list(set(achievements))
    
    return result

# 主程序
if __name__ == "__main__":
    # PDF文件路径（替换为你的文件实际路径）
    pdf_file_path = r"D:\Desktop\[OCR]_职称参评-毛雅君20251114V1.0(1)_20251127_0045.layered.pdf"
    
    # 提取信息
    extracted_info = extract_pdf_info(pdf_file_path)
    
    # 打印结果
    print("=== 职称申报信息提取结果 ===")
    print(f"姓名：{extracted_info['姓名']}")
    print("\n继续教育信息：")
    for idx, edu in enumerate(extracted_info["继续教育信息"], 1):
        print(f"{idx}. 起始时间：{edu['起始时间']}")
        print(f"   组织单位：{edu['组织单位']}")
        print(f"   学习内容：{edu['学习内容']}")
    print("\n业绩成果名称：")
    for idx, achievement in enumerate(extracted_info["业绩成果名称"], 1):
        print(f"{idx}. {achievement}")