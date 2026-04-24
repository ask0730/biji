import os
import time
import traceback
from PIL import Image
import fitz
import pythoncom
import win32com.client
import sys

# -------------------------- 配置项 --------------------------
IMAGE_QUALITY = 95
OUTPUT_FORMAT = "png"
WAIT_TIME = 1
# ------------------------------------------------------------

def get_exe_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def write_error_log(msg):
    try:
        base_dir = get_exe_dir()
        log_path = os.path.join(base_dir, "error.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except:
        pass

def read_config():
    base_dir = get_exe_dir()
    config_path = os.path.join(base_dir, "config.txt")

    if not os.path.exists(config_path):
        err = "未找到config.txt"
        write_error_log(err)
        raise Exception(err)

    input_folder = None
    output_folder = None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        err = "读取config.txt失败"
        write_error_log(err)
        raise Exception(err)

    for line in lines:
        line = line.strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key == "输入文件夹路径":
            input_folder = value
        elif key == "输出文件夹路径":
            output_folder = value

    if not input_folder or not output_folder:
        err = "config.txt配置不完整"
        write_error_log(err)
        raise Exception(err)

    return input_folder, output_folder

def pdf_to_images(pdf_path, output_dir, file_name):
    doc = None
    try:
        doc = fitz.open(pdf_path)
        total_pages = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            output_path = os.path.join(output_dir, f"{file_name}_第{page_num+1}页.{OUTPUT_FORMAT}")
            img.save(output_path, quality=IMAGE_QUALITY)
            img.close()
            total_pages += 1
        return total_pages
    finally:
        if doc:
            doc.close()

def word_to_pdf(word_path, pdf_path):
    pythoncom.CoInitialize()
    word = None
    doc = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(word_path)
        doc.SaveAs(pdf_path, FileFormat=17)
        return True
    except Exception as e:
        raise Exception(f"Word转PDF失败: {str(e)}")
    finally:
        if doc:
            doc.Close()
        if word:
            word.Quit()
        pythoncom.CoUninitialize()
        time.sleep(0.5)

def word_to_images(word_path, output_dir, file_name):
    temp_pdf = os.path.join(get_exe_dir(), "temp_file.pdf")
    try:
        word_to_pdf(word_path, temp_pdf)
        if not os.path.exists(temp_pdf):
            raise Exception("未生成PDF")
        return pdf_to_images(temp_pdf, output_dir, file_name)
    finally:
        try:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
        except:
            pass

def process_single_file(file_path, output_dir):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    ext = file_path.lower().split('.')[-1]

    try:
        if ext == "pdf":
            cnt = pdf_to_images(file_path, output_dir, file_name)
            return f"成功({cnt}页)"
        elif ext in ["docx", "doc"]:
            cnt = word_to_images(file_path, output_dir, file_name)
            return f"成功({cnt}页)"
        elif ext in ["jpg", "jpeg", "png", "bmp", "tiff"]:
            with Image.open(file_path) as img:
                img.convert("RGB").save(os.path.join(output_dir, f"{file_name}.{OUTPUT_FORMAT}"), quality=IMAGE_QUALITY)
            return "已保存"
        else:
            return "不支持格式"
    except Exception as e:
        return f"失败: {str(e)}"

def main(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    log_path = os.path.join(get_exe_dir(), "file_paths.txt")

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"输入目录：{input_folder}\n输出目录：{output_folder}\n")
        f.write("="*50 + "\n\n")

        for root, dirs, files in os.walk(input_folder):
            for file in files:
                file_path = os.path.abspath(os.path.join(root, file))
                status = process_single_file(file_path, output_folder)
                f.write(f"{file_path} | {status}\n")
                print(f"{'✅' if '成功' in status or '已保存' in status else '❌'} {file} | {status}")

    print("\n🎉 全部处理完成！")

if __name__ == "__main__":
    try:
        print("===== 格式转换工具 =====")
        input_dir, output_dir = read_config()
        main(input_dir, output_dir)
    except Exception as e:
        print(f"错误：{e}")
        write_error_log(f"崩溃：{str(e)}\n{traceback.format_exc()}")
    finally:
        input("\n按回车键退出...")