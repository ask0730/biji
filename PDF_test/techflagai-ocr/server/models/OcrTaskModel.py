# -*- coding: utf-8 -*-
from api import db

class OcrTaskModel(db.Model):
    __tablename__ = 'tb_ocr_task'

    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255, 'utf8mb4_0900_ai_ci'))
    data_type = db.Column(db.Integer, server_default=db.FetchedValue(), info='上传类型：0.识别 1.手动')
    upload_image = db.Column(db.String(255), info='上传的图片')
    output_image = db.Column(db.String(255), info='输出的图片')
    output_draw_image = db.Column(db.String(255), info='输出的识别图片')
    output_excel = db.Column(db.String(255), info='输出的excel')
    output_json = db.Column(db.JSON, info='输出的json')
    status = db.Column(db.Integer, server_default=db.FetchedValue(), info='任务状态 0.识别中 1.成功 2.失败')
    rectifye_status = db.Column(db.Integer, server_default=db.FetchedValue(), info='纠正状态 0.未纠正 1.纠正')
    confirm_status = db.Column(db.Integer, server_default=db.FetchedValue(), info='确认状态 0.待确认 1.已提交')
    confirm_time = db.Column(db.DateTime, info='提交时间')
    model_id = db.Column(db.String(255, 'utf8mb4_0900_ai_ci'), info='模型名称')
    data_set_id = db.Column(db.String(64, 'utf8mb4_0900_ai_ci'), server_default=db.FetchedValue(), info='数据集id')
    del_flag = db.Column(db.Integer, server_default=db.FetchedValue())
    create_by = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    update_by = db.Column(db.String(64))
    update_time = db.Column(db.DateTime, server_default=db.FetchedValue())

    page = 1
    limit = 10
    no_data_type = None
    end_time = None
    start_time = None

    @property
    def create_time_str(self):
        return self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None

    @property 
    def update_time_str(self):
        return self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None

    def to_dict(self):
        data = super().to_dict() if hasattr(super(), 'to_dict') else {}
        if hasattr(self, 'create_time'):
            data['create_time'] = self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None
        if hasattr(self, 'update_time'):
            data['update_time'] = self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        return data

    # 修改的字段
    modify_the_value=[]
