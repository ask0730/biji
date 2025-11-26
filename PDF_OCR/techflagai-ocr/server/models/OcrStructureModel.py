# -*- coding: utf-8 -*-
from api import db

class OcrStructureModel(db.Model):
    __tablename__ = 'tb_ocr_structure'

    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64))
    json_content = db.Column(db.JSON, info='输出的json')
    output_excel = db.Column(db.String(256),info='输出的excel')
    type = db.Column(db.Integer, server_default=db.FetchedValue())
    del_flag = db.Column(db.Integer, server_default=db.FetchedValue())
    create_by = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    update_by = db.Column(db.String(64))
    update_time = db.Column(db.DateTime, server_default=db.FetchedValue())


    page = 1
    size = 10
