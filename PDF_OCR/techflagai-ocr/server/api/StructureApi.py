# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_jwt_extended import jwt_required

from models.OcrStructureModel import OcrStructureModel
from services import OcrStructureService
from utils import modelUtil
from utils.result import Result

api_blueprint = Blueprint('/ocr/structure', __name__)
api_blueprint.url_prefix = '/ocr/structure'


@api_blueprint.route('/find', methods=['GET'])
@jwt_required()
def find():
    model = OcrStructureModel()
    modelUtil.req_to_mode(model)
    res = OcrStructureService.find(model)

    return Result.success(res)

@api_blueprint.route('/list', methods=['GET'])
@jwt_required()
def page():
    model = OcrStructureModel()
    modelUtil.req_to_mode(model)
    res = OcrStructureService.page(model)
    return Result.success(res)


@api_blueprint.route('/save_or_update', methods=['POST'])
@jwt_required()
def save_or_update():
    model = OcrStructureModel()
    modelUtil.json_to_mode(model)
    
    # 必填字段校验
    if not model.name or not model.output_excel:
        return Result.error("name和output_excel是必填字段", 400)
        
    res = OcrStructureService.save_or_update(model)
    return Result.success(res)

@api_blueprint.route('/delete', methods=['POST'])
@jwt_required()
def delete():
    model = OcrStructureModel()
    modelUtil.json_to_mode(model)
    res = OcrStructureService.delete(model)
    return Result.success(res)
