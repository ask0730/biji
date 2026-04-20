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

# ====================== 极限压图 ======================
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

# ====================== 插件主函数 ======================
def 识别文件内容(指令, 文件路径):
    try:
        文件路径 = str(Path(文件路径).resolve())
        if not os.path.exists(文件路径):
            return "错误：文件不存在"

        b64 = image_to_base64(文件路径)
        if not b64:
            return "错误：图片处理失败"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": 指令},
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
                "temperature": 0.0,
                "stream": False,
                "max_tokens": 1024
            },
            timeout=300
        )

        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            return f"服务异常 {resp.status_code}"

    except Exception as e:
        return f"执行异常：{str(e)}"

# ====================== 直接 Python 测试 ======================
if __name__ == "__main__":
    # 这里直接改你的图片路径即可
    结果 = 识别文件内容("提取图片里的所有文字", r"D:\Desktop\demo\北汽RPA\test.jpg")
    print("识别结果：")
    print(结果)