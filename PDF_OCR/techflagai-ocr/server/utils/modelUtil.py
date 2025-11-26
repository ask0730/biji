# -*- coding: utf-8 -*-
from datetime import datetime

from flask import jsonify, request
from sqlalchemy import Column

from api import db


def model_to_dict(object, date_format=None):
    data_dict = {c.name: getattr(object, c.name) for c in object.__table__.columns}

    if date_format is True:
        # 遍历所有属性，检查并格式化 DateTime 类型的字段
        for key, value in data_dict.items():
            if isinstance(value, datetime):
                data_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')

    return data_dict


# 将一组数据转为list
def scalars_to_list(object, date_format=None):
    return [model_to_dict(c, date_format) for c in object]


# 将json 赋值 model
def json_to_mode(model):
    json_data = request.get_json()
    for key, value in json_data.items():
            setattr(model, key, value)

# 将req 赋值 model
def req_to_mode(model):
    for attr in request.args.keys():
        value = request.args.get(attr)
        if value is not None and attr == 'page':
            value = int(value)
        if value is not None and attr == 'size':
            value = int(value)
        setattr(model, attr, value)

# 将req 赋值 model
def req_form_to_mode(model):
    for attr in request.form.keys():
        value = request.form.get(attr)
        setattr(model, attr, value)

# 将form 赋值 model
def form_to_mode(model):
    form_data = request.form
    for key, value in form_data.items():
            setattr(model, key, value)


# page_data 赋值 json
def page_to_json(page_data, date_format=None):

    return {
        # 'users': [user.to_dict() for user in users],  # 假设 User 模型有一个 to_dict 方法
        'total': page_data.total,  # 总记录数
        'record': scalars_to_list(page_data.items, date_format),
        'page': page_data.page,  # 当前页码
        'limit': page_data.per_page,  # 每页数量
        'pages': page_data.pages,  # 总页数
        # ... 其他你想要返回的分页信息
    }


# 赋值
def model_to_model(souc, tag):
    if souc:
        for attr in souc.__table__.columns.keys():
            value = getattr(souc, attr)
            if value:
                setattr(tag, attr, value)
