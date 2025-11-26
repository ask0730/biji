# -*- coding: utf-8 -*-
from api import db



class DataSetModel(db.Model):
    __tablename__ = 'tb_data_set'

    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(32), info='数据集名称')
    del_flag = db.Column(db.Integer, server_default=db.FetchedValue())
    create_by = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    update_by = db.Column(db.String(64))
    update_time = db.Column(db.DateTime, server_default=db.FetchedValue())

    page=1
    size=10
