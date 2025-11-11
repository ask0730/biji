import logging
import os
import traceback
import requests
import json
import re


# 初始化日志（用 logging 替代手动文件操作）
def init_logger():
    log_dir = os.path.join(os.path.dirname(__file__), "test.lib")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "api_debug.log")

    # Create file handler with UTF-8 encoding for Python 3.7.1 compatibility
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logging.getLogger()


logger = init_logger()


def handle_uibot_string(input_str):
    if input_str is None:
        return {"error": "输入为 None，需传入字符串"}
    if not isinstance(input_str, str):
        try:
            input_str = str(input_str)
        except:
            return {"error": f"输入类型错误，无法转换为字符串：{type(input_str)}"}
    return call_volcano_ark_api(input_str)


def call_volcano_ark_api(content):
    try:
        API_KEY = "f0ae6958-d859-43a9-8190-497aa9e0113a"
        MODEL = "deepseek-v3-250324"
        REGION = "cn-beijing"
        ENDPOINT = f"ark.{REGION}.volces.com"
        PATH = "/api/v3/chat/completions"

        prompt = f"""请提取以下文本的"服务类型、服务范围、服务人群"关键词，返回JSON格式：
        文本内容：{content}
        要求：
        1. 只返回JSON，不添加任何解释、说明或额外文本
        2. 每个字段为数组，不存在则为空数组（[]）
        3. 确保JSON格式正确（引号匹配、逗号正确、无多余符号）
        示例:
        {{"服务类型": ["借阅", "开放"], "服务范围": ["上海"], "服务人群": ["老年人"]}}
        """

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "你是关键词提取专家，仅返回符合要求的JSON格式结果，不添加任何额外内容。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {API_KEY}"
        }

        url = f"https://{ENDPOINT}{PATH}"
        json_payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')

        response = requests.post(
            url,
            headers=headers,
            data=json_payload,
            timeout=15
        )
        response.encoding = 'utf-8'
        logger.info(f"API响应状态码: {response.status_code}")

        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            logger.info(f"模型原始返回内容: {content}")
            processed_content = preprocess_json_content(content)

            try:
                return json.loads(processed_content)
            except json.JSONDecodeError:
                error_msg = f"预处理后仍无法解析JSON，原始内容: {content}，处理后内容: {processed_content}"
                logger.error(error_msg)
                return {
                    "error": "模型返回内容不符合JSON格式",
                    "原始内容": content,
                    "处理后内容": processed_content,
                    "建议": "检查模型返回是否包含额外文本，或JSON语法错误"
                }
        else:
            error_msg = f"响应无有效内容: {str(result)}"
            logger.error(error_msg)
            return {"error": "响应无有效内容", "details": result}

    except requests.exceptions.HTTPError as e:
        error_msg = f"API返回错误 ({response.status_code}): {str(e)}"
        logger.error(error_msg)
        return {
            "error": f"API返回错误 ({response.status_code})",
            "status_code": response.status_code,
            "response_text": response.text[:500],
            "details": str(e)
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求失败: {str(e)}")
        return {"error": "网络请求失败", "details": str(e)}
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"未知错误: {str(e)}\n{error_details}")
        return {
            "error": "处理请求时发生未知错误",
            "details": str(e),
            "traceback": error_details
        }


def preprocess_json_content(content):
    content = content.strip()
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        content = json_match.group()
    content = content.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    return content


if __name__ == "__main__":
    try:
        test_input = "上海图书馆对老年人开放借阅服务小孩"
        result = handle_uibot_string(test_input)
        print(f"最终结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"测试执行错误: {str(e)}")

