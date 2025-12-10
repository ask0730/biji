# -*- coding: utf-8 -*-
from api import db

class ConfidenceModel(db.Model):
    __tablename__ = 'tb_confidence'

    id = db.Column(db.Integer, primary_key=True)
    conf_color = db.Column(db.String(64, 'utf8mb4_0900_ai_ci'), info='颜色')
    conf_value = db.Column(db.String(11, 'utf8mb4_0900_ai_ci'), info='值')
    conf_name = db.Column(db.String(11, 'utf8mb4_0900_ai_ci'), info='文字')
    del_flag = db.Column(db.Integer, server_default=db.FetchedValue())
    create_by = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    update_by = db.Column(db.String(64))
    update_time = db.Column(db.DateTime, server_default=db.FetchedValue())

    page = 1
    limit = 10

