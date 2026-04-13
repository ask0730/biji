import dashscope
from dashscope import MultiModalConversation
import base64

# ====================== 你只需要改这里 ======================
dashscope.api_key = "sk-d62f10e4d4e54e0ba754a7e2003d9045"  # 替换成你的
IMAGE_PATH = "test.jpg"                      # 替换成你的图片路径
# ==========================================================

def img_to_text(image_path):
    # 图片转base64
    with open(image_path, "rb") as f:
        base64_data = base64.b64encode(f.read()).decode()

    # 调用OCR模型
    response = MultiModalConversation.call(
        model="qwen-vl-max-latest",
        messages=[
            {
                "role": "user",
                "content": [
                    {"image": f"data:image/png;base64,{base64_data}"},
                    {"text": "把图片里所有文字提取出来"}
                ]
            }
        ]
    )
    return response.output.choices[0].message.content

# 运行
if __name__ == "__main__":
    result = img_to_text(IMAGE_PATH)
    print("📝 图片文字识别结果：")
    print(result)