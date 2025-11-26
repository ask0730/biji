# -*- coding: utf-8 -*-
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from services import OcrTaskService
from models.OcrTaskModel import OcrTaskModel
from utils import modelUtil
from utils.result import Result
import traceback
api_blueprint = Blueprint('ocr/task', __name__)
api_blueprint.url_prefix = '/ocr/task'


@api_blueprint.route('/query', methods=['GET'])
@jwt_required()
def query():
    model = OcrTaskModel()
    modelUtil.req_to_mode(model)

    res = OcrTaskService.query(model)

    return Result.success(res)


@api_blueprint.route('/save', methods=['POST', 'OPTIONS'])
@jwt_required()
def save():
    if request.method == 'OPTIONS':
        return Result.success()
        
    try:
        file_list = request.files.getlist('file')
        if not file_list:
            return Result.error("未找到文件字段")
            
        model = OcrTaskModel()
        modelUtil.form_to_mode(model)
        
        results = []
        for file in file_list:
            if file and file.filename:
                # 直接传递文件对象给service
                res = OcrTaskService.save(model, file)
                results.append(res)
        
        return Result.success(results)
        
    except Exception as e:
       
        traceback.print_exc()
        return Result.error(f"请求处理失败: {str(e)}")

@api_blueprint.route('/recognition', methods=['GET'])
@jwt_required()
def recognition():
    model = OcrTaskModel()
    modelUtil.req_to_mode(model)
    res = OcrTaskService.recognition(model)
    return res
  

@api_blueprint.route('/dataSetupload', methods=['POST'])
@jwt_required()
def dataSetupload():
    # 检查是否有文件上传
    if 'file' not in request.files:
        return Result.error("No file found")

    file = request.files['file']
    model = OcrTaskModel()
    modelUtil.form_to_mode(model)
    res = OcrTaskService.dataSetupload(model, file)
    return Result.success(res)


@api_blueprint.route('/read_excel', methods=['GET'])
@jwt_required()
def read_excel():
    model = OcrTaskModel()
    modelUtil.req_to_mode(model)

    res = OcrTaskService.read_excel(model)

    if isinstance(res,str):
        return  Result.error(res)

    return Result.success(res)


"""
修改任务excel对应的json数据
"""
@api_blueprint.route('/update_by_excel', methods=['POST'])
@jwt_required()
def update_by_excel():
    model = OcrTaskModel()
    modelUtil.json_to_mode(model)
    res = OcrTaskService.update_by_excel(model)
    return res


"""
提交Excel通过结构化处理后的数据
"""
@api_blueprint.route('/submit', methods=['post'])
@jwt_required()
def submit():
    json = request.get_json()

   
    if res is None:
        return Result.success('提交成功')
    else:
        return Result.error(res)



@api_blueprint.route('/list', methods=['GET'])
@jwt_required()
def page():
    model = OcrTaskModel()
    modelUtil.req_to_mode(model)

    res = OcrTaskService.page(model)

    return Result.success(res)

"""
    查看任务详情,根据id查询
    包括:
    1. 任务信息
    2. 任务结果
    3. 任务状态
""" 
@api_blueprint.route('/find', methods=['GET'])
@jwt_required()
def find():
    model = OcrTaskModel()
    modelUtil.req_to_mode(model)

    res = OcrTaskService.find(model)

    return Result.success(res)


@api_blueprint.route('/status_count', methods=['GET'])
@jwt_required()
def status_count():
    model = OcrTaskModel()
    modelUtil.req_to_mode(model)
    res = OcrTaskService.status_count()
    return Result.success(res)


@api_blueprint.route('/names', methods=['GET'])
@jwt_required()
def get_unique_names():
    """
    获取所有不重复的name列表
    :return: 去重后的name列表
    """
    names = OcrTaskService.get_unique_names()
    return Result.success(names)


@api_blueprint.route('/update_data_set', methods=['POST'])
@jwt_required()
def update_data_set():
    model = OcrTaskModel()
    modelUtil.json_to_mode(model)
    if not model or not model.id:
        return Result.error("参数不完整")
    
    res = OcrTaskService.update_data_set_id(model.id, model.data_set_id)
    if(res == False):
        return Result.error(res)
    else:
        return Result.success(res)


