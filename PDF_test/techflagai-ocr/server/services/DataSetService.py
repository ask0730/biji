# -*- coding: utf-8 -*-
from sqlalchemy import text

from api import db
from models.DataSetModel import DataSetModel
from models.OcrTaskModel import OcrTaskModel
from services import OcrTaskService
from utils import modelUtil,uuidUtil


def find(req):
    query = DataSetModel.query

    if req.id is not None:
        query = query.filter_by(id=req.id)
    query = query.filter(DataSetModel.del_flag == 0)
    query = query.order_by(DataSetModel.create_time)
    res = query.first()
    return res

def page(req):
    query = DataSetModel.query

    if req.name is not None:
        query = query.filter(DataSetModel.name.like('%' + req + '%'))

    query = query.filter(DataSetModel.del_flag == 0)
    query = query.order_by(DataSetModel.create_time)
    res = query.paginate(page=int(req.page), per_page=int(req.size), error_out=False)
    res = modelUtil.page_to_json(res, date_format=True)
    if res['record']:
        for item in res['record']:
            sql = text("""
            SELECT COUNT(*)                                                            AS total_count,
                   SUM(CASE WHEN status = 1 AND rectifye_status = 0 THEN 1 ELSE 0 END) AS status_count,
                   SUM(CASE WHEN rectifye_status = 1 THEN 1 ELSE 0 END)                AS rectify_count
            FROM tb_ocr_task
            WHERE del_flag = 0
              AND data_set_id = :data_set_id
            """)
            first = db.session.execute(sql, {'data_set_id': item['id']}).first()
            item['total_count'] = first[0] if first and first[0] is not None else 0
            item['status_count'] = first[1] if first and first[1] is not None else 0
            item['rectify_count'] = first[2] if first and first[2] is not None else 0

    return res


def add(req):
    if not req.id:  # 检查是否已设置id
        req.id = str(uuidUtil.getuuid())  # 生成UUID作为主键
    db.session.add(req)
    db.session.commit()
    return True

def delete(req):
    dataset = DataSetModel.query.filter_by(id=req.id).first()
    if dataset:
        dataset.del_flag = 1  # 软删除
        db.session.commit()
        return True
    return False

"""
对数据标注更新
"""
def annotation_update(req):
    dataset = OcrTaskModel.query.filter_by(id=req.id).first()
    if dataset:
        dataset.output_json = req.output_json
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"更新失败: {str(e)}")
            return False
    return False