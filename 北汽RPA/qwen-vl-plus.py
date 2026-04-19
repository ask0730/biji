# -*- coding: utf-8 -*-
import os
import zipfile
import subprocess
import sys
from pathlib import Path
import requests
import base64
from PIL import Image
import io

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
    except:
        pass

# 自动安装依赖
try:
    from pdf2image import convert_from_path
except ImportError:
    install_package("pdf2image")

try:
    from docx2pdf import convert as docx_to_pdf
except ImportError:
    install_package("docx2pdf")

from pdf2image import convert_from_path
from docx2pdf import convert as docx_to_pdf

# ====================== 配置 ======================
BASE_URL = "http://192.168.100.121:9080/v1"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"
MODEL = "Qwen3-VL-30B-A3B-Instruct"

# ====================== 工具函数 ======================
def uncompress_file(file_path):
    extract_dir = Path("uncompressed_files")
    extract_dir.mkdir(exist_ok=True)
    file_path = str(file_path)
    try:
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
    except:
        return [file_path]

    files = []
    for f in extract_dir.rglob("*"):
        if f.is_file():
            files.append(str(f))
    return files

def word_to_pdf(docx_path):
    try:
        pdf_path = str(Path(docx_path).with_suffix(".pdf"))
        docx_to_pdf(docx_path, pdf_path)
        return pdf_path
    except:
        return None

def pdf_to_images(pdf_path):
    try:
        images = convert_from_path(pdf_path)
        image_paths = []
        for i, img in enumerate(images):
            img_path = f"pdf_page_{i+1}.jpg"
            img.save(img_path, "JPEG")
            image_paths.append(img_path)
        return image_paths
    except:
        return []

def file_to_images(input_file):
    if not Path(input_file).exists():
        return []
    if input_file.endswith((".zip", ".rar", ".7z")):
        all_files = uncompress_file(input_file)
    else:
        all_files = [input_file]

    final_images = []
    for file in all_files:
        ext = Path(file).suffix.lower()
        if ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
            final_images.append(file)
        elif ext in [".docx", ".doc"]:
            pdf = word_to_pdf(file)
            if pdf:
                imgs = pdf_to_images(pdf)
                final_images.extend(imgs)
        elif ext == ".pdf":
            imgs = pdf_to_images(file)
            final_images.extend(imgs)
    return final_images

def compress_and_encode_image(image_path, max_size_kb=1024):
    try:
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
            return base64.b64encode(data).decode("utf-8")
    except:
        return ""

def send_image_to_llm(base64_image, prompt):
    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
        response = requests.post(
            url=f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}","Content-Type": "application/json"},
            json={"model": MODEL,"messages": messages,"temperature": 0.1},
            timeout=120
        )
        return response
    except:
        return None

# ====================== 插件主函数（给UiBot用） ======================
def 识别文件内容(指令, 文件路径):
    try:
        # 1. 检查文件是否存在
        if not os.path.exists(文件路径):
            return "错误：文件不存在，请检查路径是否正确"

        # 2. 转换图片
        image_list = file_to_images(文件路径)
        if not image_list:
            return "错误：无法解析出有效图片，请检查文件格式"

        # 3. 识别
        result_all = ""
        for idx, img_path in enumerate(image_list, 1):
            try:
                base64_img = compress_and_encode_image(img_path)
                if not base64_img:
                    result_all += f"【第{idx}张】图片处理失败\n\n"
                    continue

                res = send_image_to_llm(base64_img, 指令)
                if res is None:
                    result_all += f"【第{idx}张】请求大模型接口失败\n\n"
                    continue

                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    result_all += f"【第{idx}张结果】\n{content}\n\n"
                else:
                    result_all += f"【第{idx}张】接口返回异常：{res.status_code}\n\n"
            except Exception as e:
                result_all += f"【第{idx}张】处理失败：{str(e)}\n\n"

        return result_all.strip()

    except Exception as e:
        return f"执行失败：{str(e)}"

# ====================== 【测试专用区】直接运行这个文件即可测试 ======================
if __name__ == "__main__":
    # 在这里改你的测试路径和指令
    test_prompt = "提取所有文字并排版"
    test_file_path = r"D:\Desktop\demo\北汽RPA\test.jpg"

    print("开始测试...")
    result = 识别文件内容(test_prompt, test_file_path)
    print("\n===== 测试结果 =====")
    print(result)