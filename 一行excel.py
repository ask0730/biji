import pdfplumber
import pandas as pd

# 1. 配置文件路径（修改为你的PDF路径）
pdf_path = r"D:\Desktop\[OCR]_职称参评-毛雅君20251114V1.0(1)_20251127_0045.layered.pdf"
excel_path = r"D:\Desktop\PDF导出表格.xlsx"  # 输出Excel路径（可自定义）

# 2. 提取PDF所有文本行（保留原始换行和结构）
all_lines = []
with pdfplumber.open(pdf_path) as pdf:
    # 遍历PDF的每一页
    for page_num, page in enumerate(pdf.pages, 1):
        print(f"正在处理第 {page_num} 页...")
        # 提取页面文本（strip=False 保留首尾空格，避免破坏表格对齐）
        page_text = page.extract_text(strip=False)
        if page_text:
            # 按换行符分割，获取每一行文本（过滤纯空行，可选）
            lines = [line.rstrip('\n') for line in page_text.split('\n') if line.strip()]
            all_lines.extend(lines)

# 3. 将文本行转换为Excel格式（保持原表格结构）
# 由于PDF表格是文本对齐的，直接按行存入Excel即可保留结构
df = pd.DataFrame(all_lines, columns=["PDF原始内容"])

# 4. 导出到Excel（设置列宽自适应，优化显示）
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name="PDF导出数据", index=False)
    # 获取工作表对象，设置列宽自适应
    worksheet = writer.sheets["PDF导出数据"]
    worksheet.column_dimensions['A'].width = 80  # 调整列宽（根据PDF内容长度自定义）

print(f"导出完成！Excel文件已保存至：{excel_path}")
print(f"共导出 {len(all_lines)} 行数据")