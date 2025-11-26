# -*- coding: utf-8 -*-
import mimetypes
import os
import base64  # 添加这行导入base64模块

from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required

from models.OcrTaskModel import OcrTaskModel
from utils import modelUtil, uuidUtil
from utils.result import Result

from config.otherConfig import OtherConfig

config = OtherConfig()

api_blueprint = Blueprint('file', __name__)
api_blueprint.url_prefix = '/file'
from api import db, create_app


@api_blueprint.route('/showFile', methods=['GET'])
@jwt_required()
def showFile():
    FILE_PATH = config.FILE_PATH
    TRAIN_DATA = config.TRAIN_DATA
    MODEL_PATH = config.MODEL_PATH

    id = request.args.get('name')
    type = request.args.get('type')

    if id is None:
        return "参数异常", 400

    # 直接返回静态资源URL
    return {
        'url': f'/api/file/{id}'
    }

@api_blueprint.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    try:
        target_dir = config.FILE_PATH

        # 检查是否有文件上传
        if 'file' not in request.files:
            return Result.error("No file found")

        file = request.files['file']
        
        # 检查文件是否有效（非空等）
        if file.filename == '':
            return Result.error("No selected file")

        # 先创建 model 实例并获取表单数据
        model = OcrTaskModel()
        modelUtil.form_to_mode(model)

        # 设置目标目录
        if model.id:  # 使用 if model.id 替代 if model.id is not None
            target_dir = os.path.join(target_dir, model.id)
        
        # 创建目标目录，如果不存在
        os.makedirs(target_dir, exist_ok=True)

        # 确定文件名
        if model.name:
            new_filename = model.name
        elif model.output_excel:  # 检查 output_excel 是否存在
            new_filename = model.output_excel.split('/')[-1] if '/' in model.output_excel else model.output_excel
        else:
            # 如果都没有，使用原始文件名
            new_filename = file.filename

        # 指定保存的完整路径
        save_path = os.path.join(target_dir, new_filename)

        # 保存文件
        file.save(save_path)
        
        return Result.success(msg='上传成功', data={
            'id': new_filename
        })
    except Exception as e:
        print(f"文件上传错误详情: {str(e)}")  # 添加详细的错误日志
        return Result.error(f"文件上传失败: {str(e)}")
