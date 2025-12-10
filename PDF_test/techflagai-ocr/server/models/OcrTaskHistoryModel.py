# -*- coding: utf-8 -*-
from api import db

class OcrTaskHistoryModel(db.Model):
    __tablename__ = 'tb_ocr_task_history'

    id = db.Column(db.String(64, 'utf8mb4_0900_ai_ci'), primary_key=True)
    task_id = db.Column(db.Integer, info='任务id')
    name = db.Column(db.String(64, 'utf8mb4_0900_ai_ci'))
    output_excel = db.Column(db.String(255, 'utf8mb4_0900_ai_ci'), info='输出的excel')
    version = db.Column(db.Integer, server_default=db.FetchedValue(), info='版本')
    del_flag = db.Column(db.Integer, server_default=db.FetchedValue())
    create_by = db.Column(db.String(64, 'utf8mb4_0900_ai_ci'))
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    update_by = db.Column(db.String(64, 'utf8mb4_0900_ai_ci'))
    update_time = db.Column(db.DateTime, server_default=db.FetchedValue())
