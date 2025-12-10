# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_jwt_extended import jwt_required

from models.TrainModel import TrainModel
from services import TbModelService
from utils import modelUtil
from utils.result import Result
from flask import current_app
import os
from config.otherConfig import OtherConfig

api_blueprint = Blueprint('/ocr/model', __name__)
api_blueprint.url_prefix = '/ocr/model'

# 创建配置实例
_config = OtherConfig()


@api_blueprint.route('/save', methods=['POST'])
@jwt_required()
def save():
    model = TrainModel()
    modelUtil.json_to_mode(model)
    if model.id is None or model.id == '':
        res = TbModelService.save(model)
    else:
        res = TbModelService.update(model)
    if not res:
        return Result.error('保存失败') 
    return Result.success('保存成功')


@api_blueprint.route('/model_test', methods=['POST'])
@jwt_required()
def model_test():
    model = TrainModel()
    modelUtil.json_to_mode(model)
    res = TbModelService.rec_model_test(model)
    # 检查返回的状态码
    if res.get('code') != 200:
        return Result.error(res.get('msg', '识别失败'))
    
    return Result.success(res)


@api_blueprint.route('/find', methods=['GET'])
@jwt_required()
def find():
    model = TrainModel()
    modelUtil.req_to_mode(model)
    res = TbModelService.find(model)
    # 如果查询成功且有模型ID，获取数据统计信息
    if res and model.id:
        # 确保res是可序列化的字典
        if not isinstance(res, dict):
            res = modelUtil.model_to_dict(res)
        
        # 获取统计信息并添加到结果中
        stats = get_data_stats(model.id)
        res.update(stats)
            
    return Result.success(res)

@api_blueprint.route('/list', methods=['GET'])
@jwt_required()
def page():
    model = TrainModel()
    modelUtil.req_to_mode(model)
    res = TbModelService.page(model)

    return Result.success(res)

@api_blueprint.route('/config', methods=['GET'])
@jwt_required()
def config():
    model = TrainModel()
    modelUtil.json_to_mode(model)

    config_data = {
        "status_options": [
            {"value": 0, "label": "识别中"},
            {"value": 1, "label": "成功"}, 
            {"value": 2, "label": "失败"}
        ],
        "rectifye_status_options": [
            {"value": 0, "label": "未纠正"},
            {"value": 1, "label": "已纠正"}
        ],
        "confirm_status_options": [
            {"value": 0, "label": "待确认"},
            {"value": 1, "label": "已提交"}
        ]
    }
    
    res = TbModelService.add(model)
    return Result.success(res)
    
def get_data_stats(model_id):
    # 使用全局配置
    model_rec_path = os.path.join(_config.MODEL_PATH, model_id, 'rec')
    print(f'模型路径: {model_rec_path}')
    
    # 读取训练和验证数据
    def read_data_file(file_path):
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.split('\t')[0] for line in f.read().splitlines()]
    
    # 读取训练集和验证集数据
    train_list = read_data_file(os.path.join(model_rec_path, 'train.txt'))
    val_list = read_data_file(os.path.join(model_rec_path, 'val.txt'))
    
    return {
        'train_num': len(train_list),      # 训练集总数
        'val_num': len(val_list),          # 验证集总数
        'train_list': train_list[:10],     # 训练集前10条
        'val_list': val_list[:10]          # 验证集前10条
    }