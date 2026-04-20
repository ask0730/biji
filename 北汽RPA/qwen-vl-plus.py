# -*- coding: utf-8 -*-
import os
import base64
import zipfile
import requests
from PIL import Image
import io
import pathlib
from docx import Document
import PyPDF2
import patoolib

# ====================== 配置 ======================
BASE_URL = "http://192.168.100.121:9080/v1"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"
MODEL = "Qwen3-VL-30B-A3B-Instruct"

# ====================== 格式判断 ======================
def is_image(suffix):
    return suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

def is_docx(suffix):
    return suffix.lower() == '.docx'

def is_pdf(suffix):
    return suffix.lower() == '.pdf'

def is_archive(suffix):
    return suffix.lower() in ['.zip', '.rar', '.7z']

# ====================== 图片转base64 ======================
def image_to_base64(image_path):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail((240, 240))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=30)
            return base64.b64encode(buf.getvalue()).decode("utf8")
    except:
        return ""

# ====================== 调用大模型 ======================
def call_llm(base64_img, prompt):
    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                ]
            }
        ]
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0.0,
                "stream": False,
                "max_tokens": 1024
            },
            timeout=300
        )
        return resp
    except Exception as e:
        return None

# ====================== 识别单张图片 ======================
def recognize_single_image(filepath, prompt):
    b64 = image_to_base64(filepath)
    if not b64:
        return f"[{filepath}] 图片读取失败"
    resp = call_llm(b64, prompt)
    if not resp:
        return f"[{filepath}] 请求失败"
    if resp.status_code == 200:
        return f"=== {os.path.basename(filepath)} ===\n" + resp.json()["choices"][0]["message"]["content"] + "\n"
    else:
        return f"[{filepath}] 错误 {resp.status_code}"

# ====================== 读取 Word ======================
def read_docx(filepath):
    try:
        doc = Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])
    except:
        return "读取Word失败"

# ====================== 读取 PDF ======================
def read_pdf(filepath):
    try:
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        return text
    except:
        return "读取PDF失败"

# ====================== 解压 ======================
def extract(filepath, outdir):
    try:
        patoolib.extract_archive(str(filepath), outdir=str(outdir), verbosity=-1)
        return True
    except:
        return False

# ====================== 扫描文件夹 ======================
def scan_images(folder, prompt):
    result = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            p = pathlib.Path(file)
            if is_image(p.suffix):
                res = recognize_single_image(os.path.join(root, file), prompt)
                result.append(res)
    return "\n".join(result)

# ====================== 【主函数】UiBot调用 ======================
def 识别文件内容(指令, 路径):
    try:
        path = pathlib.Path(路径).resolve()
        if not path.exists():
            return "路径不存在"

        if path.is_dir():
            return scan_images(str(path), 指令)

        sf = path.suffix.lower()

        if is_image(sf):
            return recognize_single_image(str(path), 指令)

        elif is_docx(sf):
            return "=== Word内容 ===\n" + read_docx(str(path))

        elif is_pdf(sf):
            return "=== PDF内容 ===\n" + read_pdf(str(path))

        elif is_archive(sf):
            tmp = path.parent / "tmp_unpack"
            tmp.mkdir(exist_ok=True)
            if not extract(str(path), tmp):
                return "解压失败，请确保安装了解压工具"
            return scan_images(str(tmp), 指令)

        else:
            return "不支持此格式"

    except Exception as e:
        return f"异常：{str(e)}"

# ====================== 本地测试 ======================
if __name__ == "__main__":
    res = 识别文件内容("提取图片里的所有文字", r"D:\Desktop\demo\北汽RPA\test.jpg")
    print(res)