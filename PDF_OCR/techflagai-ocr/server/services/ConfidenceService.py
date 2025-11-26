# -*- coding: utf-8 -*-
from api import db
from models.ConfidenceModel import ConfidenceModel
from utils import modelUtil, tokenUtil


def page(req):

    user = tokenUtil.getUser()
    query = ConfidenceModel.query

    query = query.filter(ConfidenceModel.del_flag == 0)
    query = query.order_by(ConfidenceModel.create_time)
    res = query.paginate(page=int(req.page), per_page=int(req.size), error_out=False)

    res = modelUtil.page_to_json(res, date_format=True)

    if not res['record']:
        error_correction_is_required = ConfidenceModel()
        error_correction_is_required.conf_color = 'rgba(255, 99, 71, 0.2)'
        error_correction_is_required.conf_value = '0.8'
        error_correction_is_required.conf_name = '需要纠错'
        error_correction_is_required.create_by = user.user_id
        error_correction_is_required.update_by = user.user_id
        db.session.add(error_correction_is_required)

        confirmation_is_required = ConfidenceModel()
        confirmation_is_required.conf_color = 'rgba(255, 165, 0, 0.2)'
        confirmation_is_required.conf_value = '0.9'
        confirmation_is_required.conf_name = '需要确认'
        confirmation_is_required.create_by = user.user_id
        confirmation_is_required.update_by = user.user_id
        db.session.add(confirmation_is_required)
        db.session.commit()

        res = query.paginate(page=int(req.page), per_page=int(req.size), error_out=False)
        res = modelUtil.page_to_json(res, date_format=True)

    return res



def update(req):
    update_data = {
        ConfidenceModel.id: req.id,
        ConfidenceModel.conf_value: req.conf_value,
        ConfidenceModel.conf_name: req.conf_name,
    }
    update_data = {k: v for k, v in update_data.items() if v is not None}

    ConfidenceModel.query.filter(ConfidenceModel.id == req.id).update(
        update_data, synchronize_session='fetch')
    db.session.commit()
    # 调用识别接口
    return {
        'id': ConfidenceModel.id
    }