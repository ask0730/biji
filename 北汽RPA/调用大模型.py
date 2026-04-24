# -*- coding: utf-8 -*-
import base64
import io
import requests
from PIL import Image

BASE_URL = "http://192.168.100.121:9080"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"
MODEL = "Qwen3-VL-30B-A3B-Instruct"

def img_to_base64(img_path):
    try:
        img = Image.open(img_path)
        img = img.convert("RGB")
        img.thumbnail((1024,1024))
        buf = io.BytesIO()
        img.save(buf, "JPEG")
        return base64.b64encode(buf.getvalue()).decode()
    except:
        return ""

def 识别文件内容(指令, 文件路径):
    try:
        b64 = img_to_base64(文件路径)
        if not b64:
            return "图片读取失败"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + API_KEY
        }

        data = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": 指令},
                        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,"+b64}}
                    ]
                }
            ],
            "temperature": 0.1
        }

        rep = requests.post(BASE_URL+"/v1/chat/completions", json=data, headers=headers)
        j = rep.json()
        return j["choices"][0]["message"]["content"]
    
    except Exception as e:
        return "异常："+str(e)

# 本地测试
if __name__ == "__main__":
    img_path = r"D:\Desktop\demo\北汽RPA\1111111-111111111-11111111_第1页.png"
    print(识别文件内容("提取文字", img_path))