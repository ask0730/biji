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
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            img.thumbnail((320, 320))
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=20)
            # 修复：base64.b64encode，不是b6encode
            return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print("图片处理异常：", str(e))  # 加个错误打印，方便排查
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

        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": 指令},
                        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}
                    ]
                }
            ],
            "temperature": 0.1
        }

        resp = requests.post(
            BASE_URL + "/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=60,
            proxies={"http": None, "https": None}
        )

        resp.raise_for_status()  # 加个状态码检查，方便看接口错误
        result = resp.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return "模型错误：" + str(result)

    except Exception as e:
        return "异常：" + str(e)

# ===================== 测试调用 =====================
if __name__ == "__main__":
    # 修复路径：用 r"" 原始字符串，避免转义
    结果 = 识别文件内容("提取所有文字并排版", r"D:\Desktop\demo\北汽RPA\test.jpg")
    
    print("=" * 50)
    print("图片文字识别结果：")
    print("=" * 50)
    print(结果)