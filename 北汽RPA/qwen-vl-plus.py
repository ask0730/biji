import dashscope
from dashscope import MultiModalConversation
import base64
import os

# ====================== 【必须修改】这里 ======================
dashscope.api_key = "sk-d62f10e4d4e54e0ba754a7e2003d9045"  # 替换成你的API Key
FILE_PATH = "test.jpg"  # 支持：图片(.jpg/.png) 或 PDF(.pdf)
YOUR_QUESTION = "请提取这份文件里的所有文字，并告诉我发票金额"
# ==============================================================

def encode_file_to_base64(file_path):
    """将文件转为Base64编码（支持图片/PDF）"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_file(file_path, prompt):
    # 1. 校验文件是否存在
    if not os.path.exists(file_path):
        return f"❌ 错误：文件 {file_path} 不存在，请检查路径！"
    
    # 2. 区分文件类型，构造正确的请求参数
    file_ext = os.path.splitext(file_path)[1].lower()
    abs_path = os.path.abspath(file_path)
    
    if file_ext in [".jpg", ".jpeg", ".png", ".bmp"]:
        # 图片：用 image 格式传Base64
        base64_data = encode_file_to_base64(file_path)
        content_item = {"image": f"data:image/{file_ext[1:]};base64,{base64_data}"}
    elif file_ext == ".pdf":
        # PDF：用 pdf 格式传本地路径（官方推荐）
        content_item = {"pdf": f"file://{abs_path}"}
    else:
        return f"❌ 错误：不支持的文件类型 {file_ext}，仅支持图片/PDF"

    # 3. 构造标准请求
    messages = [
        {
            "role": "user",
            "content": [
                content_item,
                {"text": prompt}
            ]
        }
    ]

    # 4. 调用模型
    response = MultiModalConversation.call(
        model="qwen-vl-plus",
        messages=messages
    )

    # 5. 处理响应
    if response.status_code == 200:
        return response.output.choices[0].message.content
    else:
        return f"❌ 调用失败：错误码 {response.code}，错误信息 {response.message}"

# 运行
if __name__ == "__main__":
    print("🔍 正在分析文件，请稍候...")
    result = analyze_file(FILE_PATH, YOUR_QUESTION)
    print("\n===== 分析结果 =====")
    print(result)