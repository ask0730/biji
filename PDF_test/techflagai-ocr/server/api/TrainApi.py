# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_jwt_extended import jwt_required

from models.TrainModel import TrainModel
from services import TrainService
from utils import modelUtil
from utils.result import Result


api_blueprint = Blueprint('/ocr/train', __name__)
api_blueprint.url_prefix = '/ocr/train'



@api_blueprint.route('/find', methods=['GET'])
@jwt_required()
def find():
    model = TrainModel()
    modelUtil.req_to_mode(model)
    res = TrainService.find(model)

    return Result.success(res)
@api_blueprint.route('/save', methods=['POST'])
@jwt_required()
def save():
    model = TrainModel()
    modelUtil.json_to_mode(model)
    res = TrainService.save(model)

    return Result.success(res)
@api_blueprint.route('/update', methods=['POST'])
@jwt_required()
def update():
    model = TrainModel()
    modelUtil.json_to_mode(model)
    res = TrainService.update(model)

    return Result.success(res)


@api_blueprint.route('/data_check', methods=['POST'])
@jwt_required()
def data_check():
    model = TrainModel()
    modelUtil.json_to_mode(model)
    res = TrainService.data_check(model)

    return res

@api_blueprint.route('/data_check_data', methods=['POST'])
@jwt_required()
def data_check_data():
    model = TrainModel()
    modelUtil.json_to_mode(model)
    res = TrainService.data_check_data(model)

    return res


@api_blueprint.route('/update_yml', methods=['POST'])
@jwt_required()
def update_yml():
    model = TrainModel()
    modelUtil.json_to_mode(model)
    res = TrainService.update_yml(model)

    return res


@api_blueprint.route('/cutting_img', methods=['POST'])
@jwt_required()
def cutting_img():
    try:
        model = TrainModel()
        modelUtil.json_to_mode(model)
        res = TrainService.cutting_img(model)
        return res
    except Exception as e:
        return Result.error(f"图片切割处理失败: {str(e)}")
