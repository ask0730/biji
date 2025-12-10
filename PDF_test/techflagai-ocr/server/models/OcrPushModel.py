# -*- coding: utf-8 -*-
from api import db


class OcrPushModel(db.Model):
    __tablename__ = 'tb_ocr_push'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255), info='任务id')
    proj_no = db.Column(db.String(255), info='报检单id')
    status = db.Column(db.Integer, server_default=db.FetchedValue(), info='推送状态：0推送中 1.成功 2.失败')
    err_msg = db.Column(db.String(255), info='失败信息')
    call_status = db.Column(db.String(64), info='回执状态：done 不可推送')
    push_json = db.Column(db.JSON, info='推送json')
    del_flag = db.Column(db.Integer, server_default=db.FetchedValue())
    create_by = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    update_by = db.Column(db.String(64))
    update_time = db.Column(db.DateTime, server_default=db.FetchedValue())
