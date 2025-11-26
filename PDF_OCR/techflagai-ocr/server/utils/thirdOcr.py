# -*- coding: utf-8 -*-
import requests
import json
import base64
from urllib.parse import urlencode # 导入 urlencode 用于构建查询字符串

class ThirdPartyOCR:
    def __init__(self, config):
        self.config = config

    def recognize(self, file_path):
        try:
            if 'baidu' in self.config.get('type', ''):
                return self._recognize_baidu(file_path)
            else:
                # 将整个config传递给_recognize_textin，以便获取header和parameters
                return self._recognize_textin(file_path, self.config)
        except Exception as e:
            return {"error": str(e)}

    # 修改 _recognize_textin 方法以接收完整的 config
    def _recognize_textin(self, file_path, config):
        try:
            # config 已经是字典格式，无需再次loads

            headers = config.get('header', {}) # 使用get方法，提供默认空字典
            headers['Content-Type'] = 'application/octet-stream'

            # 获取parameters，并过滤掉None值
            parameters = {k: v for k, v in config.get('parameters', {}).items() if v is not None}

            # 构建带有参数的URL
            base_url = 'https://api.textin.com/ai/service/v2/recognize/table/multipage'
            if parameters:
                query_string = urlencode(parameters)
                request_url = f"{base_url}?{query_string}"
            else:
                request_url = base_url

            image = self._get_file_content(file_path)
            response = requests.post(
                request_url, # 使用构建好的URL
                data=image,
                headers=headers
            )
            return response.json()
        except Exception as e:
            # 打印详细错误信息以便调试
            import traceback
            traceback.print_exc()
            return {"code": 500, "msg": f"TextIn OCR 请求失败: {str(e)}"}

    def _recognize_baidu(self, file_path):


        # 读取图像文件并进行Base64编码
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data)

        # 构建请求参数
        params = {"image": base64_encoded}
        headers = self.config['header']
        access_token = self._get_baidu_access_token()
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/table?access_token={access_token}"

        # 发送请求
        response = requests.post(url, headers=headers, data=params)
        return response.json()

    def _get_baidu_access_token(self):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.config['header']['API_KEY'],
            "client_secret": self.config['header']['SECRET_KEY']
        }
        response = requests.post(url, params=params)
        return response.json().get("access_token")

    def _get_file_content(self, file_path):
        with open(file_path, 'rb') as fp:
            return fp.read()

    def process_line(line, cell=None):
        """处理单个line数据，如果有cell信息则包含行列信息"""
        if not line:
            return None

        item = {
            "box": line.get("position", [])[:4],  # 取position的前4个点作为box
            "col": [
                cell.get("start_col", 0) if cell else 0,
                cell.get("end_col", 0) if cell else 0
            ],
            "row": [
                cell.get("start_row", 0) if cell else 0,
                cell.get("end_row", 0) if cell else 0
            ],
            "text": line.get("text", ""),
            "type": line.get("type", "text"),
            "score": line.get("score", 1.0),
            "position": line.get("position", [])
        }
        return item

    """
    用于解析TextIn返回的JSON数据，符合以下格式：
    {"box": [ 2821, 548, 2860, 548 ], "col": [ 36, 36 ], "row": [ 7, 8 ], "text": "OK", "type": "text", "score": 0.485, "position": [ 2821, 548, 2860, 548, 2860, 578, 2821, 578 ] },
    """
    @staticmethod
    def extract_textin(data):
        """递归提取所有层级的lines，保留行列信息"""
        result = []

        # 处理页面级别的tables
        for page in data.get('result', {}).get('pages', []):
            for table in page.get('tables', []):
                # 处理table直接包含的lines（非单元格内的文本）
                for line in table.get('lines', []):
                    item = ThirdPartyOCR.process_line(line)
                    if item:
                        result.append(item)

                # 处理table_cells中的lines（表格单元格内的文本）
                for cell in table.get('table_cells', []):
                    for line in cell.get('lines', []):
                        # 传入cell信息以获取行列位置
                        item = ThirdPartyOCR.process_line(line, cell)
                        if item:
                            result.append(item)

        return result




# 使用示例
if __name__ == "__main__":
    # 示例1：使用合合OCR（TextIn）
    textin_config = {
        "api_url": "https://api.textin.com/ai/service/v2/recognize/table/multipage",
        "header": {
            "x-ti-app-id": "",
            "x-ti-secret-code": ""
        },
        "body": {},
        "parameters": {
            "character": 1,
            "straighten": 1,
            "output_order": "table_and_remain",
            "table_type_hint": "automatic",
            "excel": 1
        }
    }
    textin_ocr = ThirdPartyOCR(config=textin_config)
    result = textin_ocr.recognize('../test/example.jpg')
    print(json.dumps(result, indent=2))

    # 示例2：使用百度OCR
    baidu_config = {
        "type": "baidu",
        "api_url": "https://aip.baidubce.com/rest/2.0/ocr/v1/table",
        "header": {
            "API_KEY": "",
            "SECRET_KEY": "",
            "Content-Type": "application/x-www-form-urlencoded",
            'Authorization': 'Bearer'
        },
        "body": {},
        "parameters": {}
    }
    baidu_ocr = ThirdPartyOCR(config=baidu_config)
    result = baidu_ocr.recognize('../test/example.jpg')
    print(json.dumps(result, indent=2))
