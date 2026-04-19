# -*- coding: utf-8 -*-
import os
import base64
import requests
from PIL import Image
import io
from pathlib import Path

# ====================== 配置 ======================
BASE_URL = "http://192.168.100.121:9080/v1"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"
MODEL = "Qwen3-VL-30B-A3B-Instruct"

# ====================== 图片极致压缩 ======================
def compress_and_encode_image(image_path):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail((320, 320))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=30)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        return ""

# ====================== 调用大模型 ======================
def send_image_to_llm(base64_img, prompt):
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

        response = requests.post(
            url=f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0.0,
                "stream": False
            },
            timeout=300
        )
        return response
    except:
        return None

# ====================== 插件主函数 ======================
def 识别文件内容(指令, 文件路径):
    try:
        文件路径 = str(Path(文件路径).resolve())

        if not os.path.exists(文件路径):
            return "错误：文件不存在"

        base64_img = compress_and_encode_image(文件路径)
        if not base64_img:
            return "错误：图片处理失败"

        res = send_image_to_llm(base64_img, 指令)
        if res is None:
            return "错误：请求超时，模型处理较慢"

        if res.status_code == 200:
            try:
                return res.json()["choices"][0]["message"]["content"]
            except:
                return "错误：结果解析失败"
        else:
            return f"服务异常 {res.status_code}，请稍后重试"

    except Exception as e:
        return f"执行异常：{str(e)}"

# ====================== 本地测试 ======================
if __name__ == "__main__":
    res = 识别文件内容("提取图片中的文字", r"D:\Desktop\demo\北汽RPA\test.jpg")
    print(res)