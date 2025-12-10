# -*- coding: utf-8 -*-
import hashlib
import uuid  # 添加uuid模块导入
from flask_jwt_extended import create_access_token, get_jwt_identity

from api import db
from models.SysUserModel import SysUserModel
from models.OcrStructureModel import OcrStructureModel
from utils import modelUtil, tokenUtil,uuidUtil
from utils.result import Result



def find(req):
    query = OcrStructureModel.query

    if req.id is not None:
        query = query.filter_by(id=req.id)
    query = query.filter(OcrStructureModel.del_flag == 0)
    query = query.order_by(OcrStructureModel.create_time)
    res = query.first()
    return res

def page(req):
    query = OcrStructureModel.query

    if req.name is not None:
        query = query.filter(OcrStructureModel.name.like('%' + req + '%'))

    query = query.filter(OcrStructureModel.del_flag == 0)
    query = query.order_by(OcrStructureModel.create_time)
    res = query.paginate(page=int(req.page), per_page=int(req.size), error_out=False)

    return modelUtil.page_to_json(res, date_format=True)


def save_or_update(req):
    if not hasattr(req, 'json_content') or req.json_content is None:
        req.json_content = {}  # 设置默认空字典
    if req.id is not None:
        res = update(req)
    else:
        res = save(req)
    return res

def save(req):
    if not req.id:  # 检查是否已设置id
        req.id = str(uuidUtil.getuuid())  # 生成UUID作为主键
    db.session.add(req)
    db.session.commit()
    return 'success'

def update(req):
    model = OcrStructureModel.query.filter_by(id=req.id).first()
    modelUtil.model_to_model(req, model)
    db.session.commit()

    return model

def delete(req):
    model = OcrStructureModel.query.filter_by(id=req.id).first()
    if model:
        model.del_flag = 1  # 软删除
        db.session.commit()
        return True
    return False

    
