import os
import platform
from PIL import Image
from docx2pdf import convert
import fitz  # PyMuPDF
import pythoncom

# -------------------------- 配置项（可自行修改） --------------------------
# 图片输出质量（1-100，越大越清晰）
IMAGE_QUALITY = 95
# 长图拼接时的间距（像素）
IMAGE_SPACING = 20
# 输出图片格式
OUTPUT_FORMAT = "png"
# ------------------------------------------------------------------------

def images_to_long_image(images, output_path, spacing=IMAGE_SPACING):
    """将多张图片拼接为一张长图"""
    if not images:
        return
    
    # 计算长图总尺寸
    total_height = sum(img.height for img in images) + spacing * (len(images) - 1)
    max_width = max(img.width for img in images)
    
    # 创建白色背景长图
    long_image = Image.new('RGB', (max_width, total_height), color='white')
    
    # 拼接图片
    current_y = 0
    for img in images:
        # 居中放置
        x_offset = (max_width - img.width) // 2
        long_image.paste(img, (x_offset, current_y))
        current_y += img.height + spacing
    
    # 保存长图
    long_image.save(output_path, quality=IMAGE_QUALITY)
    for img in images:
        img.close()

def pdf_to_long_image(pdf_path, output_path):
    """PDF转长图"""
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        # 高清渲染
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    
    doc.close()
    images_to_long_image(images, output_path)

def word_to_long_image(word_path, output_path):
    """Word转长图（先转PDF再转图片）"""
    pythoncom.CoInitialize()  # Windows COM初始化
    temp_pdf = word_path + ".temp.pdf"
    
    try:
        # Word转临时PDF
        convert(word_path, temp_pdf)
        # PDF转长图
        pdf_to_long_image(temp_pdf, output_path)
    finally:
        # 删除临时PDF
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)
        pythoncom.CoUninitialize()

def process_single_file(file_path, output_dir):
    """处理单个文件：转长图"""
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_dir, f"{file_name}_long.{OUTPUT_FORMAT}")
    
    ext = file_path.lower().split('.')[-1]
    
    try:
        if ext in ['pdf']:
            pdf_to_long_image(file_path, output_path)
        elif ext in ['docx', 'doc']:
            word_to_long_image(file_path, output_path)
        elif ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
            # 单张图片直接保存为长图
            img = Image.open(file_path).convert('RGB')
            img.save(output_path, quality=IMAGE_QUALITY)
            img.close()
        else:
            return None, "不支持的文件格式"
        
        return output_path, "转换成功"
    except Exception as e:
        return None, f"转换失败：{str(e)}"

def main(folder_path):
    """主函数：遍历文件夹处理所有文件"""
    # 创建输出文件夹
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "转换后的长图")
    os.makedirs(output_dir, exist_ok=True)
    
    # 记录文件路径的txt
    txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "file_paths.txt")
    
    # 遍历文件夹
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"文件夹路径：{folder_path}\n")
        f.write("="*50 + "\n\n")
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.abspath(os.path.join(root, file))
                # 写入原始文件路径
                f.write(f"原始文件：{file_path}\n")
                
                # 转换文件
                long_img_path, status = process_single_file(file_path, output_dir)
                if long_img_path:
                    f.write(f"长图路径：{long_img_path}\n状态：{status}\n\n")
                    print(f"✅ 处理完成：{file}")
                else:
                    f.write(f"长图路径：无\n状态：{status}\n\n")
                    print(f"❌ 处理失败：{file} - {status}")
    
    print(f"\n🎉 全部处理完成！")
    print(f"📄 文件路径已保存至：{txt_path}")
    print(f"🖼️ 长图已保存至：{output_dir}")

if __name__ == "__main__":
    # 在这里输入你要处理的文件夹路径
    TARGET_FOLDER = r"D:\Desktop\demo\北汽RPA\test"  # Windows示例
    # TARGET_FOLDER = "/Users/xxx/测试文件夹"  # Mac示例
    
    if not os.path.isdir(TARGET_FOLDER):
        print("❌ 请输入有效的文件夹路径！")
    else:
        main(TARGET_FOLDER)