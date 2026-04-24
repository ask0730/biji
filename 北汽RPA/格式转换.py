import os
import time
from PIL import Image
from docx2pdf import convert
import fitz  # PyMuPDF
import pythoncom

# -------------------------- 配置项（可自行修改） --------------------------
# 图片输出质量（1-100，越大越清晰）
IMAGE_QUALITY = 95
# 输出图片格式
OUTPUT_FORMAT = "png"
# Word转PDF后等待的时间（秒，避免文件被占用）
WAIT_TIME = 0.5
# ------------------------------------------------------------------------

def read_config():
    """读取同目录下的 config.txt 获取输入输出路径"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.txt")
    if not os.path.exists(config_path):
        raise Exception("未找到配置文件 config.txt，请创建后再运行！")

    input_folder = None
    output_folder = None

    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key == "输入文件夹路径":
                input_folder = value
            elif key == "输出文件夹路径":
                output_folder = value

    if not input_folder or not output_folder:
        raise Exception("config.txt 配置不完整，请填写 输入文件夹路径 和 输出文件夹路径")

    return input_folder, output_folder

def pdf_to_images(pdf_path, output_dir, file_name):
    """PDF 按自然分页转成一页一张图片"""
    doc = None
    try:
        # 增加重试机制，避免文件被占用
        for attempt in range(3):
            try:
                doc = fitz.open(pdf_path)
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(WAIT_TIME * 2)
                else:
                    raise e

        for page_num in range(len(doc)):
            page = doc[page_num]
            # 高清渲染
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # 保存单页图片（按页码命名）
            output_path = os.path.join(output_dir, f"{file_name}_第{page_num+1}页.{OUTPUT_FORMAT}")
            img.save(output_path, quality=IMAGE_QUALITY)
            img.close()

        return len(doc)  # 返回总页数
    finally:
        if doc is not None:
            doc.close()

def word_to_images(word_path, output_dir, file_name):
    """Word 转单页图片（先转PDF再分页转图）"""
    pythoncom.CoInitialize()
    temp_pdf = word_path + ".temp.pdf"

    try:
        # Word转临时PDF
        convert(word_path, temp_pdf)
        # 等待文件写入完成
        time.sleep(WAIT_TIME)
        # 确认文件存在且非空
        if not os.path.exists(temp_pdf) or os.path.getsize(temp_pdf) == 0:
            raise Exception("Word转PDF失败，生成的临时文件无效")
        # PDF分页转图片
        total_pages = pdf_to_images(temp_pdf, output_dir, file_name)
        return total_pages
    finally:
        # 删除临时PDF
        if os.path.exists(temp_pdf):
            try:
                os.remove(temp_pdf)
            except:
                pass
        pythoncom.CoUninitialize()

def process_single_file(file_path, output_dir):
    """处理单个文件：分页输出图片"""
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    ext = file_path.lower().split('.')[-1]

    # 跳过临时文件
    if file_path.endswith(".temp.pdf"):
        return "跳过临时文件"

    try:
        if ext in ['pdf']:
            # PDF 分页输出
            total_pages = pdf_to_images(file_path, output_dir, file_name)
            return f"转换成功（共{total_pages}页）"

        elif ext in ['docx', 'doc']:
            # Word 分页输出
            total_pages = word_to_images(file_path, output_dir, file_name)
            return f"转换成功（共{total_pages}页）"

        elif ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
            # 图片直接保存
            try:
                with Image.open(file_path) as img:
                    img = img.convert('RGB')
                    output_path = os.path.join(output_dir, f"{file_name}.{OUTPUT_FORMAT}")
                    img.save(output_path, quality=IMAGE_QUALITY)
                return "图片已保存"
            except Exception as e:
                return f"图片文件损坏或无法识别：{str(e)}"

        else:
            return "不支持的文件格式"

    except Exception as e:
        return f"转换失败：{str(e)}"

def main(input_folder, output_folder):
    """主函数：遍历文件夹处理所有文件"""
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 记录文件路径的txt（和python同目录）
    txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "file_paths.txt")

    # 遍历文件夹
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"输入文件夹路径：{input_folder}\n")
        f.write(f"输出文件夹路径：{output_folder}\n")
        f.write("="*50 + "\n\n")

        for root, dirs, files in os.walk(input_folder):
            for file in files:
                file_path = os.path.abspath(os.path.join(root, file))
                f.write(f"原始文件：{file_path}\n")

                # 转换文件
                status = process_single_file(file_path, output_folder)
                f.write(f"状态：{status}\n")
                f.write(f"输出目录：{output_folder}\n\n")

                if "成功" in status or "已保存" in status:
                    print(f"✅ 处理完成：{file} | {status}")
                elif "跳过" in status:
                    print(f"⏭️ 跳过文件：{file}")
                else:
                    print(f"❌ 处理失败：{file} - {status}")

    print(f"\n🎉 全部处理完成！")
    print(f"📄 文件路径日志：{txt_path}")
    print(f"🖼️ 图片输出目录：{output_folder}")

if __name__ == "__main__":
    try:
        # 从 config.txt 读取路径
        TARGET_FOLDER, OUTPUT_FOLDER = read_config()

        if not os.path.isdir(TARGET_FOLDER):
            print("❌ 输入文件夹路径无效！")
        else:
            main(TARGET_FOLDER, OUTPUT_FOLDER)
    except Exception as e:
        print(f"❌ 错误：{str(e)}")