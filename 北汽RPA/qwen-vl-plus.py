# -*- coding: utf-8 -*-
import os
import base64
import requests
from PIL import Image
import io

# ====================== 配置 ======================
BASE_URL = "http://192.168.100.121:9080/v1"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"
MODEL = "Qwen3-VL-30B-A3B-Instruct"

# ====================== 极限压图 ======================
def image_to_base64(image_path):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail((128, 128))  # 超级小图
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=10)  # 画质极低
            return base64.b64encode(buf.getvalue()).decode("utf8")
    except:
        return ""

# ====================== 仅发图片+极简提示 ======================
def recognize_image(image_path):
    b64 = image_to_base64(image_path)
    if not b64:
        return "图片读取失败"

    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "图里有什么"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
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
                "temperature": 0.01,
                "stream": False,
                "max_tokens": 256  # 输出极短，快速返回
            },
            timeout=120
        )
        return resp
    except Exception as e:
        return None

# ====================== 测试 ======================
if __name__ == "__main__":
    res = recognize_image(r"D:\Desktop\demo\北汽RPA\test.jpg")
    if res:
        print("状态码:", res.status_code)
        if res.status_code == 200:
            print(res.json()["choices"][0]["message"]["content"])