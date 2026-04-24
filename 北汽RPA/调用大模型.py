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
            # 适度缩放，既不糊也不超出服务端限制
            max_side = 1280
            if max(img.size) > max_side:
                ratio = max_side / max(img.size)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=90)
            return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print("图片处理异常：", str(e))
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

        # 标准 OpenAI 多模态格式，兼容绝大多数服务端
        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": 指令},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.0,
            "max_tokens": 4096
        }

        resp = requests.post(
            BASE_URL + "/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=120,
            proxies={"http": None, "https": None}
        )

        # 打印错误详情，方便定位问题
        print("状态码：", resp.status_code)
        print("返回内容：", resp.text)
        
        resp.raise_for_status()
        result = resp.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            return "模型返回异常：" + str(result)

    except Exception as e:
        return "请求异常：" + str(e)

# ===================== 测试调用 =====================
if __name__ == "__main__":
    识别指令 = """
    你是专业的文档识别助手：
    1. 精准识别图片中所有文字，不要遗漏
    2. 严格按照原文排版、分段、换行输出
    3. 只输出识别后的文字，不要任何解释、多余内容
    4. 准确理解文字内容，保证识别结果正确
    """

    图片路径 = r"D:\Desktop\demo\北汽RPA\1111111-111111111-11111111_long.png"
    
    结果 = 识别文件内容(识别指令, 图片路径)

    print("=" * 60)
    print("✅ 大模型识别结果：")
    print("=" * 60)
    print(结果)