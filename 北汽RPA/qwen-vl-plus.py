import base64
import requests

# ===================== 你的配置 =====================
BASE_URL = "http://192.168.100.121:9080/v1"
API_KEY = "sk-PxldK3SEs3uMLbwd8353AbA99dAd4a30B8Ee7f79C7F075Fc"
MODEL = "Qwen3-VL-30B-A3B-Instruct"
IMAGE_PATH = "test.jpg"  # 你的图片
PROMPT = "识别数字"
# ====================================================

# 图片转 base64
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 发送请求（OpenAI 兼容格式）
def chat_vl():
    url = f"{BASE_URL}/chat/completions"
    
    base64_img = encode_image(IMAGE_PATH)
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_img}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 2048,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 发送
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        res = response.json()
        print("\n✅ 识别结果：")
        print(res["choices"][0]["message"]["content"])
    else:
        print("❌ 错误码：", response.status_code)
        print("错误信息：", response.text)

if __name__ == "__main__":
    chat_vl()