# -*- coding: utf-8 -*-
from flask import Blueprint, make_response, jsonify
from flask_jwt_extended import jwt_required, unset_jwt_cookies

from models.SysUserModel import SysUserModel
from services import UserService
from utils import modelUtil

api_blueprint = Blueprint('user', __name__)
api_blueprint.url_prefix = '/user'


@api_blueprint.route('/login', methods=['POST'])
def login():
    User = SysUserModel()
    modelUtil.json_to_mode(User)
    res = UserService.login(User)
    return res


@api_blueprint.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    resp = make_response(jsonify({"msg": "Logged out successfully."}))
    unset_jwt_cookies(resp)
    return resp


