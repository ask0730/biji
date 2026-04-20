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

# ===================== 配置 =====================
BASE_URL = "http://localhost:8000"  # 换成你的模型服务地址
API_KEY = ""  # 有需要就填
MODEL_NAME = "qwen-vl-plus"

# ===================== 格式判断 =====================
def is_image(suffix):
    return suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

def is_docx(suffix):
    return suffix.lower() == '.docx'

def is_pdf(suffix):
    return suffix.lower() == '.pdf'

# ===================== 图片转base64 =====================
def image_to_base64(image_path):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail((1024, 1024))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"图片处理失败：{e}")
        return None

# ===================== 调用大模型 =====================
def call_llm(base64_data, prompt):
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
        data = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
                    ]
                }
            ]
        }
        resp = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"调用模型失败：{str(e)}"

# ===================== 识别单张图片 =====================
def recognize_single_image(filepath, prompt):
    b64 = image_to_base64(filepath)
    if not b64:
        return f"[{filepath}] 图片读取失败"
    result = call_llm(b64, prompt)
    return f"=== {os.path.basename(filepath)} ===\n{result}\n"

# ===================== 读取Word =====================
def read_docx(filepath):
    try:
        doc = Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"读取Word失败：{e}"

# ===================== 读取PDF =====================
def read_pdf(filepath):
    try:
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        return f"读取PDF失败：{e}"

# ===================== 解压ZIP =====================
def extract_zip(zip_path, outdir):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(outdir)
        return True
    except Exception as e:
        print(f"解压失败：{e}")
        return False

# ===================== 扫描文件夹 =====================
def scan_images(folder, prompt):
    result = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if is_image(pathlib.Path(file).suffix):
                full_path = os.path.join(root, file)
                result.append(recognize_single_image(full_path, prompt))
    return "\n".join(result)

# ===================== 【主函数】UiBot调用 =====================
def 识别文件内容(指令, 路径):
    try:
        path = pathlib.Path(路径).resolve()
        if not path.exists():
            return "路径不存在"

        if path.is_dir():
            return scan_images(str(path), 指令)

        suffix = path.suffix.lower()

        if is_image(suffix):
            return recognize_single_image(str(path), 指令)
        elif is_docx(suffix):
            return "=== Word文档内容 ===\n" + read_docx(str(path))
        elif is_pdf(suffix):
            return "=== PDF文档内容 ===\n" + read_pdf(str(path))
        elif suffix == ".zip":
            tmp = path.parent / "tmp_unpack"
            tmp.mkdir(exist_ok=True)
            if not extract_zip(str(path), tmp):
                return "ZIP解压失败"
            return scan_images(str(tmp), 指令)
        else:
            return "不支持此格式"

    except Exception as e:
        return f"异常：{str(e)}"

# ===================== 本地测试入口 =====================
if __name__ == "__main__":
    # 本地直接运行测试
    test_path = r"D:\Desktop\demo\北汽RPA\test.jpg"  # 换成你的测试文件路径
    test_prompt = "提取图片里的所有文字"
    print(识别文件内容(test_prompt, test_path))