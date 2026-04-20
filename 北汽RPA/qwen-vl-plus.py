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

# ====================== 依赖安装 ======================
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
    except:
        pass

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

# ====================== 关键配置（请填写你自己的信息） ======================
BASE_URL = "http://192.168.100.121:9080"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"  # 必须填！
MODEL = "Qwen3-VL-30B-A3B-Instruct"  # 用你服务里真实的模型名

# ====================== 工具函数 ======================
def uncompress_file(file_path):
    extract_dir = Path("uncompressed_files")
    extract_dir.mkdir(exist_ok=True)
    file_path = str(file_path)
    try:
        if file_path.endswith(".zip"):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
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

def compress_and_encode_image(image_path):
    with Image.open(image_path) as img:
        img.thumbnail((1024, 1024))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

# ====================== 修复：带令牌的 LLM 调用 ======================
def send_image_to_llm(base64_image, prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"  # 强制带上令牌
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "temperature": 0.1
    }

    try:
        response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers, timeout=60)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ====================== 主函数 ======================
def 识别文件内容(指令, 文件路径):
    try:
        image_list = file_to_images(文件路径)
        if not image_list:
            return "错误：未找到可处理的图片"

        result_all = ""
        for idx, img_path in enumerate(image_list, 1):
            try:
                base64_img = compress_and_encode_image(img_path)
                res = send_image_to_llm(base64_img, 指令)

                if "choices" in res:
                    content = res["choices"][0]["message"]["content"]
                    result_all += f"【第{idx}张结果】\n{content}\n\n"
                else:
                    result_all += f"【第{idx}张】错误：{str(res)}\n\n"
            except Exception as e:
                result_all += f"【第{idx}张】异常：{str(e)}\n\n"
        return result_all.strip()
    except Exception as e:
        return f"异常：{str(e)}"

# ====================== 本地测试 ======================
if __name__ == "__main__":
    test_file = r"test.zip"  # 换成你的测试图片路径
    test_prompt = "提取图片中的所有文字"
    print(识别文件内容(test_prompt, test_file))