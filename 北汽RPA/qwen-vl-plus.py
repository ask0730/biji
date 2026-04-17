# -*- coding: utf-8 -*-
"""
UiBot 插件：文件图文AI识别插件
支持：图片、Word、PDF、压缩包
参数：指令、文件路径
作者：自动封装
"""

import os
import zipfile
import subprocess
import sys
from pathlib import Path
import requests
import base64
from PIL import Image
import io

# ====================== 依赖安装（UiBot环境自动适配） ======================
def install_package(package):
    """自动安装Python库"""
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

# ====================== 核心配置 ======================
BASE_URL = "http://192.168.100.121:9080/v1"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"
MODEL = "Qwen3-VL-30B-A3B-Instruct"

# ====================== 工具函数 ======================
def uncompress_file(file_path):
    """解压压缩包：zip/rar/7z"""
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
    """Word转PDF"""
    try:
        pdf_path = str(Path(docx_path).with_suffix(".pdf"))
        docx_to_pdf(docx_path, pdf_path)
        return pdf_path
    except:
        return None

def pdf_to_images(pdf_path):
    """PDF转图片"""
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
    """统一将文件转为图片"""
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
    """图片压缩+Base64编码"""
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

def send_image_to_llm(base64_image, prompt):
    """发送到多模态大模型"""
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
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": messages,
            "temperature": 0.1
        },
        timeout=120
    )
    return response

# ====================== 插件主函数（UiBot直接调用） ======================
def 识别文件内容(指令, 文件路径):
    """
    UiBot插件入口函数
    :param 指令: 字符串，对图片的描述指令，例如：提取图片中的文字
    :param 文件路径: 字符串，文件完整路径
    :return: 识别结果字符串
    """
    try:
        # 1. 文件转图片
        image_list = file_to_images(文件路径)
        if not image_list:
            return "错误：未找到可处理的图片"

        # 2. 批量识别
        result_all = ""
        for idx, img_path in enumerate(image_list, 1):
            try:
                base64_img = compress_and_encode_image(img_path)
                res = send_image_to_llm(base64_img, 指令)

                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    result_all += f"【第{idx}张结果】\n{content}\n\n"
                else:
                    result_all += f"【第{idx}张】请求失败：{res.text}\n\n"
            except Exception as e:
                result_all += f"【第{idx}张】处理异常：{str(e)}\n\n"

        return result_all.strip()

    except Exception as e:
        return f"插件执行异常：{str(e)}"