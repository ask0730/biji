# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_jwt_extended import jwt_required

from models.TrainModel import TrainModel
from services import DataSetService
from models.DataSetModel import DataSetModel
from utils import modelUtil
from utils.result import Result

api_blueprint = Blueprint('/ocr/dataset', __name__)
api_blueprint.url_prefix = '/ocr/dataset'


@api_blueprint.route('/find', methods=['GET'])
@jwt_required()
def find():
    model = DataSetModel()
    modelUtil.req_to_mode(model)
    res = DataSetService.find(model)
    return Result.success(res)

@api_blueprint.route('/list', methods=['GET'])
@jwt_required()
def page():
    model = DataSetModel()
    modelUtil.req_to_mode(model)
    res = DataSetService.page(model)
    return Result.success(res)

@api_blueprint.route('/save', methods=['POST'])
@jwt_required()
def add():
    model = DataSetModel()
    modelUtil.json_to_mode(model)
    res = DataSetService.add(model)
    return Result.success(res)

@api_blueprint.route('/delete', methods=['POST'])
@jwt_required()
def delete():
    model = DataSetModel()
    modelUtil.json_to_mode(model)
    res = DataSetService.delete(model)
    return Result.success(res)

"""
对数据标注更新
"""
@api_blueprint.route('/annotation_update', methods=['POST'])
@jwt_required()
def annotation_update():
    model = DataSetModel()
    modelUtil.json_to_mode(model)
    res = DataSetService.annotation_update(model)

    return Result.success(res)
