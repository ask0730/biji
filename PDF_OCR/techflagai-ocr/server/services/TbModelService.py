# -*- coding: utf-8 -*-
from models.TrainModel import TrainModel
from api import db
from utils import modelUtil,uuidUtil
from utils.thirdOcr import ThirdPartyOCR  # This is the correct import path
import json
import datetime  # 添加datetime模块的导入


def find(req):
    query = TrainModel.query

    if req.id is not None:
        query = query.filter_by(id=req.id)
    query = query.filter(TrainModel.del_flag == 0)
    query = query.order_by(TrainModel.create_time)
    res = query.first()
    return res

def rec_model_test(req):
    ocr = ThirdPartyOCR(config=json.loads(req.rec_yml))
    test_image = './test/example.jpg'
    code=200
    msg="success"
    if req.producte_line==2:
        res = ocr._recognize_textin(test_image)
        code = res.get('code')
        msg = res.get('message')
        
    elif req.producte_line==3:
        res = ocr._recognize_baidu(test_image)   
        code = res.get('error_code', 200)  # 如果没有error_code，则默认为200
        msg = res.get('error_msg', 'success')  # 如果没有error_msg，则默认为success
    return {
        "code":code,
        "msg":msg,
    }

def save(req):
    if not req.id:  # 检查是否已设置id
        req.id = str(uuidUtil.getuuid())  # 生成UUID作为主键
    db.session.add(req)
    db.session.commit()
    return True
    
def page(req):
    query = TrainModel.query

    if req.name is not None:
        query = query.filter(TrainModel.name.like('%' + req + '%'))
    if req.use_status is not None:
        query = query.filter(TrainModel.use_status == req.use_status)
    if req.producte_line is not None:
        query = query.filter(TrainModel.producte_line == req.producte_line)
    query = query.filter(TrainModel.del_flag == 0)
    query = query.order_by(TrainModel.create_time.desc())
    res = query.paginate(page=int(req.page), per_page=int(req.size), error_out=False)
    return modelUtil.page_to_json(res, date_format=True)


def update(req):
    """
    根据id更新模型记录
    """
    if not req.id:
        return False
        
    try:
        # 使用update方法直接更新数据库记录
        affected_rows = TrainModel.query.filter_by(id=req.id).update({
            'use_status': req.use_status,
            'name': req.name,
            'producte_line': req.producte_line,
            'rec_yml': req.rec_yml,
            'update_time': datetime.datetime.now()
        })
        db.session.commit()
        return affected_rows > 0
    except Exception as e:
        db.session.rollback()
        print(f"更新失败: {str(e)}")
        return False

