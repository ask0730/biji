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

from pdf2image import convert_from_path

# ====================== 配置 ======================
BASE_URL = "http://192.168.100.121:9080"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"
MODEL = "Qwen3-VL-30B-A3B-Instruct"

# ====================== 工具 ======================
def uncompress_file(file_path):
    extract_dir = Path("uncompressed_files")
    extract_dir.mkdir(exist_ok=True)
    try:
        if str(file_path).endswith(".zip"):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
    except:
        return [file_path]
    return [str(f) for f in extract_dir.rglob("*") if f.is_file()]

def pdf_to_images(pdf_path):
    try:
        images = convert_from_path(pdf_path)
        paths = []
        for i, img in enumerate(images):
            p = f"pdf_page_{i}.jpg"
            img.save(p, "JPEG")
            paths.append(p)
        return paths
    except:
        return []

def file_to_images(input_file):
    all_files = uncompress_file(input_file) if input_file.endswith((".zip",".rar",".7z")) else [input_file]
    final = []
    for f in all_files:
        e = Path(f).suffix.lower()
        if e in [".jpg",".jpeg",".png",".bmp",".gif"]:
            final.append(f)
        elif e == ".pdf":
            final.extend(pdf_to_images(f))
    return final

def img2base64(p):
    with Image.open(p) as img:
        img.thumbnail((1024,1024))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=60)
        return base64.b64encode(buf.getvalue()).decode()

# ====================== LLM ======================
def send_to_llm(b64, prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"<img>{b64}</img>{prompt}"
            }
        ],
        "temperature": 0.1
    }
    try:
        r = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data, timeout=60)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ====================== 【带日志返回】主函数 ======================
def 识别文件内容(指令, 文件路径):
    log = []  # 用来存日志
    def print_log(msg):
        print(msg)       # 本地测试显示
        log.append(msg)  # 同时返回给 UiBot

    try:
        print_log(f"[开始] 路径：{文件路径}")

        imgs = file_to_images(文件路径)
        print_log(f"[找到图片] {len(imgs)} 张")

        if not imgs:
            return "\n".join(log) + "\n错误：无图片"

        res_all = ""
        for i, p in enumerate(imgs,1):
            print_log(f"[处理第 {i} 张] {p}")

            b64 = img2base64(p)
            print_log(f"[请求大模型...]")
            ret = send_to_llm(b64, 指令)

            if "choices" in ret:
                content = ret["choices"][0]["message"]["content"]
                print_log(f"[识别成功]")
                res_all += f"【第{i}张】\n{content}\n\n"
            else:
                print_log(f"[错误] {str(ret)}")
                res_all += f"【第{i}张】错误：{str(ret)}\n\n"

        print_log("[完成]")
        return "\n".join(log) + "\n\n" + res_all.strip()

    except Exception as e:
        err = f"异常：{str(e)}"
        print_log(err)
        return "\n".join(log)

# ====================== 测试 ======================
if __name__ == "__main__":
    result = 识别文件内容("提取文字并排版", r"D:\Desktop\demo\北汽RPA\test.jpg")
    print("\n===== 最终结果 =====\n")
    print(result)