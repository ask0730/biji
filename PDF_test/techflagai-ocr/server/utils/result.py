# -*- coding: utf-8 -*-
from flask import jsonify

from api import db
from utils import modelUtil


class Result:

    @classmethod
    def success(cls, data=None, date_format=None, msg=None):
        # 如果 data 是单个对象，调用 model_to_dict 转换为字典
        if isinstance(data, db.Model):
            data_dict = modelUtil.model_to_dict(data, date_format)
            data_dict = {'data': data_dict}

            # 如果 data 是列表，调用 scalars_to_list 转换为字典列表
        elif isinstance(data, list) and all([isinstance(d, db.Model) for d in data]):
            data_dict_list = modelUtil.scalars_to_list(data, date_format)
            data_dict = {'data': data_dict_list}
            # 其他情况，假设 data 已经是可 JSON 序列化的对象
        else:
            data_dict = {'data': data}
            # 构建响应内容
        response_content = {
            'msg': msg if msg else 'success',
            'code': 200,
            'data': data_dict['data']
        }
        # 返回 JSON 格式的响应
        return jsonify(response_content)


    @classmethod
    def error(cls, msg=None, code=500):
        # 构建响应内容
        response_content = {
            'msg': msg,
            'code': code
        }
        # 返回 JSON 格式的响应
        return jsonify(response_content)
