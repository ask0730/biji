import os
import zipfile
import subprocess
from pathlib import Path
import requests
import base64
from PIL import Image
import io
from pdf2image import convert_from_path
from docx2pdf import convert as docx_to_pdf

# ====================== 你的配置 ======================
BASE_URL = "http://192.168.100.121:9080/v1"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"
MODEL = "Qwen3-VL-30B-A3B-Instruct"

# 要处理的文件（支持：图片 / Word / PDF / 压缩包）
INPUT_FILE = "test.zip"  # 可改为：test.docx、test.pdf、test.zip、test.rar
# =====================================================

def install_package(package):
    """自动安装缺失的库"""
    try:
        subprocess.check_call(["pip", "install", package])
    except:
        print(f"请手动安装：pip install {package}")

# 自动安装依赖
try:
    from pdf2image import convert_from_path
except ImportError:
    install_package("pdf2image")

try:
    from docx2pdf import convert as docx_to_pdf
except ImportError:
    install_package("docx2pdf")

def uncompress_file(file_path):
    """解压压缩包：支持 zip/rar/7z"""
    extract_dir = Path("uncompressed_files")
    extract_dir.mkdir(exist_ok=True)
    
    file_path = str(file_path)
    if file_path.endswith(".zip"):
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
    elif file_path.endswith(".rar"):
        install_package("unrar")
        from unrar import rarfile
        with rarfile.RarFile(file_path, "r") as rar_ref:
            rar_ref.extractall(extract_dir)
    elif file_path.endswith(".7z"):
        install_package("py7zr")
        import py7zr
        with py7zr.SevenZipFile(file_path, "r") as z:
            z.extractall(extract_dir)
    else:
        return [file_path]
    
    # 收集解压后的所有文件
    files = []
    for f in extract_dir.rglob("*"):
        if f.is_file():
            files.append(str(f))
    return files

def word_to_pdf(docx_path):
    """Word 转 PDF"""
    pdf_path = str(Path(docx_path).with_suffix(".pdf"))
    try:
        docx_to_pdf(docx_path, pdf_path)
    except Exception as e:
        print(f"Word转PDF失败：{e}")
        return None
    return pdf_path

def pdf_to_images(pdf_path):
    """PDF 转图片（每页一张）"""
    try:
        images = convert_from_path(pdf_path)
    except:
        print("需要安装 poppler！请按提示安装：")
        print("Windows: 下载 poppler 并配置环境变量")
        print("Mac: brew install poppler")
        print("Ubuntu: sudo apt-get install poppler-utils")
        return []
    
    image_paths = []
    for i, img in enumerate(images):
        img_path = f"pdf_page_{i+1}.jpg"
        img.save(img_path, "JPEG")
        image_paths.append(img_path)
    return image_paths

def file_to_images(input_file):
    """统一入口：自动识别文件类型 → 转成图片"""
    # 1. 如果是压缩包，先解压
    if input_file.endswith((".zip", ".rar", ".7z")):
        all_files = uncompress_file(input_file)
    else:
        all_files = [input_file]

    final_images = []
    for file in all_files:
        ext = Path(file).suffix.lower()

        # 图片
        if ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
            final_images.append(file)

        # Word
        elif ext in [".docx", ".doc"]:
            pdf = word_to_pdf(file)
            if pdf:
                imgs = pdf_to_images(pdf)
                final_images.extend(imgs)

        # PDF
        elif ext == ".pdf":
            imgs = pdf_to_images(file)
            final_images.extend(imgs)

    return final_images

def compress_and_encode_image(image_path, max_size_kb=1024):
    """压缩图片并转base64"""
    with Image.open(image_path) as img:
        img.thumbnail((1024, 1024))
        quality = 85
        while True:
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            data = buffer.getvalue()
            if len(data) / 1024 <= max_size_kb or quality <= 10:
                break
            quality -= 10
        print(f"图片压缩完成：{len(data)/1024:.2f} KB")
        return base64.b64encode(data).decode("utf-8")

def send_image_to_llm(base64_image):
    """发送图片给大模型"""
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "请详细描述这张图片的内容"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        }
    ]

    response = requests.post(
        url=f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": messages,
            "temperature": 0.1
        }
    )
    return response

# ====================== 主流程 ======================
if __name__ == "__main__":
    print(f"正在处理文件：{INPUT_FILE}")
    
    # 自动转图片（支持：压缩包、Word、PDF、图片）
    image_list = file_to_images(INPUT_FILE)
    if not image_list:
        print("未找到可处理的图片")
        exit()

    print(f"\n生成图片列表：{image_list}")

    # 逐个处理图片
    for idx, img_path in enumerate(image_list, 1):
        print(f"\n========== 正在处理第 {idx} 张图片 ==========")
        try:
            base64_img = compress_and_encode_image(img_path)
            res = send_image_to_llm(base64_img)

            print(f"状态码：{res.status_code}")
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"]
                print("✅ 识别结果：")
                print(content)
            else:
                print("❌ 请求失败：")
                print(res.text)
        except Exception as e:
            print(f"处理失败：{e}")