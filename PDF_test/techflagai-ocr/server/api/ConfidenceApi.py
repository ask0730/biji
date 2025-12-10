# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_jwt_extended import jwt_required

from models.TrainModel import TrainModel
from services import ConfidenceService
from utils import modelUtil
from utils.result import Result

api_blueprint = Blueprint('/ocr/confidence', __name__)
api_blueprint.url_prefix = '/ocr/confidence'


@api_blueprint.route('/page', methods=['GET'])
@jwt_required()
def page():
    model = TrainModel()
    modelUtil.req_to_mode(model)
    res = ConfidenceService.page(model)

    return Result.success(res)


@api_blueprint.route('/update', methods=['GET'])
@jwt_required()
def update():
    model = TrainModel()
    modelUtil.json_to_mode(model)
    res = ConfidenceService.update(model)

    return Result.success(res)
