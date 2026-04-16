import requests


BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = "sk-9cbb86c53c784b668be286883e5fa3e3"
MODEL = "qwen3-vl-30b-a3b-instruct"

# 发送请求
response = requests.post(
    url=f"{BASE_URL}/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": MODEL,
        "messages": [{"role": "user", "content": "你好"}]  
    }
)

# 打印结果
print("响应状态码:", response.status_code)
print("返回结果:\n", response.json())