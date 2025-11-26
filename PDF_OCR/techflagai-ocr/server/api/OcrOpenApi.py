# -*- coding: utf-8 -*-
from xxlimited import Str
from flask import Blueprint, request, jsonify
import traceback
import os
import tempfile
from werkzeug.utils import secure_filename
import requests # 假设需要requests库来处理URL
import base64 # 导入base64库
from config.otherConfig import OtherConfig
import uuid # 导入uuid库用于生成文件名
from utils.thirdOcr import ThirdPartyOCR # 确保导入了ThirdPartyOCR
from utils.ocr_utils import format_items_as_markdown_table
_config = OtherConfig()

api_blueprint = Blueprint('/ocr/open', __name__)
api_blueprint.url_prefix = '/ocr/open'



# 定义TextIn错误码到内部响应的映射
TEXTIN_ERROR_MAP = {
    40101: {"code": 401, "msg": "OCR服务认证失败，缺少API密钥。", "http_status": 401},
    40102: {"code": 401, "msg": "OCR服务认证失败，API密钥无效。", "http_status": 401},
    40103: {"code": 403, "msg": "客户端IP不在OCR服务白名单。", "http_status": 403},
    40003: {"code": 402, "msg": "OCR服务余额不足，请联系管理员充值。", "http_status": 400}, # 使用 400 作为 HTTP 状态码
    40004: {"code": 400, "msg": "请求参数错误，请检查。", "http_status": 400},
    40007: {"code": 400, "msg": "OCR机器人不存在或未发布。", "http_status": 400},
    40008: {"code": 400, "msg": "OCR机器人未开通。", "http_status": 400},
    40301: {"code": 400, "msg": "文件类型不支持。", "http_status": 400},
    40302: {"code": 400, "msg": "上传文件大小超出限制。", "http_status": 400},
    40303: {"code": 400, "msg": "文件类型不支持。", "http_status": 400},
    40304: {"code": 400, "msg": "图片尺寸不符。", "http_status": 400},
    40305: {"code": 400, "msg": "识别文件未上传。", "http_status": 400},
    40400: {"code": 404, "msg": "无效的请求链接。", "http_status": 404},
    30203: {"code": 503, "msg": "OCR基础服务故障，请稍后重试。", "http_status": 503},
    500: {"code": 500, "msg": "OCR服务器内部错误。", "http_status": 500},
}


@api_blueprint.route('/recognize_table_multipage', methods=['POST'])
# 注意：此API不需要登录，因此不使用 @jwt_required()
def external_ocr():
    temp_file_path = None # 用于存储上传的二进制文件或下载的URL文件
    try:
        # 1. 获取请求头
        app_id = request.headers.get('x-ti-app-id')
        secret_code = request.headers.get('x-ti-secret-code')
        captcha = request.headers.get('x-captcha') # 获取验证码头部

        # 简单的头部校验（您可以根据实际需求增强校验逻辑）
        if not app_id or not secret_code:
             return jsonify({"code": 400, "msg": "缺少必要的请求头: x-ti-app-id 或 x-ti-secret-code"}), 400

        # 验证码校验（这里只是一个简单的示例，您需要根据实际的验证码生成和校验逻辑来实现）
        if not captcha:
             return jsonify({"code": 400, "msg": "缺少必要的请求头: x-captcha"}), 400
        # TODO: 在这里添加实际的验证码校验逻辑，例如：
        # if not validate_captcha(captcha): # 假设您有一个validate_captcha函数
        #      return jsonify({"code": 400, "msg": "验证码无效"}), 400


        # 2. 获取URL参数
        character = request.args.get('character', type=int)
        straighten = request.args.get('straighten', type=int)
        output_order = request.args.get('output_order', type=str)
        table_type_hint = request.args.get('table_type_hint', type=str)
        excel = request.args.get('excel', type=int)
        
        # 将参数和头部信息收集到一个config字典中，传递给ThirdPartyOCR
        ocr_config = {
            'type': 'textin', # 指定使用textin
            'header': {
                'x-ti-app-id': app_id,
                'x-ti-secret-code': secret_code
            },
            'parameters': {
                'character': character,
                'straighten': straighten,
                'output_order': output_order,
                'table_type_hint': table_type_hint,
                'excel': excel
            }
        }
        # 过滤掉parameters中值为 None 的参数
        ocr_config['parameters'] = {k: v for k, v in ocr_config['parameters'].items() if v is not None}


        # 3. 处理请求体 (文件或URL)
        content_type = request.headers.get('Content-Type')
        image_source_value = None # 存储文件路径或URL

        if content_type == 'application/octet-stream':
            # 处理二进制文件流
            image_data = request.data
            if not image_data:
                 return jsonify({"code": 400, "msg": "请求体为空"}), 400

            # 将二进制数据保存到临时文件
            try:
                # 使用临时文件保存上传的图片数据
                fd, temp_file_path = tempfile.mkstemp(suffix=".tmp")
                with os.fdopen(fd, 'wb') as tmp:
                    tmp.write(image_data)
                image_source_value = temp_file_path
            except Exception as e:
                 return jsonify({"code": 500, "msg": f"保存临时文件失败: {str(e)}"}), 500

        elif content_type == 'text/plain':
            # 处理URL链接
            image_url = request.data.decode('utf-8').strip()
            if not image_url:
                 return jsonify({"code": 400, "msg": "请求体为空或URL为空"}), 400
            
            # 从URL下载文件到临时文件
            try:
                response = requests.get(image_url, stream=True)
                response.raise_for_status() # 检查请求是否成功
                fd, temp_file_path = tempfile.mkstemp(suffix=".tmp")
                with os.fdopen(fd, 'wb') as tmp:
                    for chunk in response.iter_content(chunk_size=8192):
                        tmp.write(chunk)
                image_source_value = temp_file_path
            except requests.exceptions.RequestException as e:
                 return jsonify({"code": 400, "msg": f"下载图片失败: {str(e)}"}), 400
            except Exception as e:
                 return jsonify({"code": 500, "msg": f"保存下载的图片失败: {str(e)}"}), 500
        else:
             return jsonify({"code": 415, "msg": f"不支持的Content-Type: {content_type}"}), 415

        # 4. 调用第三方OCR服务
        try:
            _ocr = ThirdPartyOCR(config=ocr_config)
            # 调用recognize方法，传递临时文件路径
            ocr_response = _ocr.recognize(image_source_value)

            # 5. 处理OCR响应
            if ocr_response and ocr_response.get('code') == 200:
                ocr_result = ocr_response.get('result', {})

                # 提取pages数据，无论excel参数如何，只要OCR成功就尝试提取
                extracted_pages_data = ThirdPartyOCR.extract_textin(ocr_response)
                markdown_table_output = format_items_as_markdown_table(extracted_pages_data)

                # 6. 处理excel参数和保存excel文件
                # 检查请求参数中是否要求返回excel，并且OCR结果中是否包含excel数据
                if excel == 1 and ocr_result and ocr_result.get('excel'):
                    try:
                        excel_base64 = ocr_result['excel']

                        # 如果需要保存到指定目录
                        output_dir = _config.OCR_OPEN_FILE_PATH
                        if output_dir:
                            os.makedirs(output_dir, exist_ok=True)
                            # 生成文件名，可以使用UUID确保唯一性
                            file_name = f"ocr_result_{uuid.uuid4()}.xlsx"
                            file_path_to_save = os.path.join(output_dir, file_name)

                            # 解码并保存Excel内容到文件
                            excel_bytes = base64.b64decode(excel_base64)
                            with open(file_path_to_save, 'wb') as f:
                                f.write(excel_bytes)

                            # 如果excel=1且保存成功，返回包含文件路径和pages数据的响应
                            return jsonify({
                                "code": 200,
                                "msg": "识别成功，Excel文件已保存",
                                "excel_file_path": _config.STATIC_URL + file_name, # 返回文件路径
                                "pages": markdown_table_output # 添加pages数据
                            }), 200
                        else:
                             print("OCR_OPEN_FILE_PATH 环境变量未设置，不保存Excel文件。")
                             # 如果要求保存但目录未设置，返回警告信息并包含原始OCR结果和pages数据
                             return jsonify({
                                "code": 200,
                                "msg": "识别成功，但OCR_OPEN_FILE_PATH 未设置，Excel文件未保存。",
                                "data": ocr_result, # 返回原始OCR结果
                                "pages": markdown_table_output # 添加pages数据
                             }), 200


                    except Exception as excel_e:
                        # 处理Excel生成或编码失败的情况
                        print(f"处理Excel失败: {excel_e}")
                        # 即使OCR成功，Excel处理失败，仍然返回OCR结果、pages数据和错误信息
                        return jsonify({
                            "code": 200, # OCR本身成功
                            "msg": "识别成功，但处理Excel失败",
                            "data": ocr_result, # 返回原始OCR结果
                            "pages": extracted_pages_data, # 添加pages数据
                            "excel_error": f"处理Excel失败: {str(excel_e)}"
                        }), 200

                # 如果excel != 1 或者 OCR结果中不包含excel，则返回完整的OCR结果和pages数据
                response_data = {
                    "code": 200,
                    "msg": "识别成功",
                    "excel_file_path": "", # 返回文件路径
                    "pages": markdown_table_output # 添加pages数据
                }
                return jsonify(response_data), 200 # 返回成功响应

            else:
                # OCR服务返回非200状态码或错误信息
                ocr_code = ocr_response.get('code', 500)
                ocr_msg = ocr_response.get('msg', 'TextIn OCR 识别失败')

                # 从映射字典中查找对应的响应信息
                error_info = TEXTIN_ERROR_MAP.get(ocr_code, {
                    "code": 500,
                    "msg": f"未知第三方OCR服务错误 (Code: {ocr_code}, Msg: {ocr_msg})",
                })

                return jsonify({
                    "code": error_info["code"], # 返回内部定义的错误码
                    "msg": error_info["msg"],  # 返回更友好的错误信息
                }), error_info["http_status"] # 返回相应的HTTP状态码

        except Exception as e:
            traceback.print_exc()
            return jsonify({"code": 500, "msg": f"调用OCR服务失败: {str(e)}"}), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({"code": 500, "msg": f"请求处理失败: {str(e)}"}), 500
    finally:
        # 确保临时文件被清理
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"临时文件已清理: {temp_file_path}")
            except Exception as cleanup_e:
                print(f"清理临时文件失败 {temp_file_path}: {cleanup_e}")
