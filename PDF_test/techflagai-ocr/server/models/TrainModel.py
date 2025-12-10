# -*- coding: utf-8 -*-
from api import db



class TrainModel(db.Model):
    __tablename__ = 'tb_model'

    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), info='模型名称')
    producte_line = db.Column(db.Integer, server_default=db.FetchedValue(), info='产线：1.自定义代码 2.合合；3、百度')
    mission_scene = db.Column(db.String(12), info='任务场景')
    customize = db.Column(db.String(12), info='任务场景')
    rec_yml = db.Column(db.String(255), info='rec配置文件')
    train_set = db.Column(db.Integer, server_default=db.FetchedValue(), info='训练集占比')
    val_set = db.Column(db.Integer, server_default=db.FetchedValue(), info='测试集占比')
    data_set_id = db.Column(db.String(64), info='数据集id')
    data_set_status = db.Column(db.Integer, server_default=db.FetchedValue(), info='切分状态 0.否 1.切分中 2.切分成功 -1.切分失败')
    step = db.Column(db.Integer, server_default=db.FetchedValue(), info='步骤')
    status = db.Column(db.Integer, server_default=db.FetchedValue(), info='状态：0.配置中 1.运行中 2.运行完成 3.已取消')
    model_status = db.Column(db.Integer, server_default=db.FetchedValue(), info='模型状态 0.未转换 1.转换中 2.成功 -1 失败')
    use_status = db.Column(db.Integer, server_default=db.FetchedValue(), info='使用状态 0.未使用 1.使用中')
    acc = db.Column(db.String(255), info='准确率')
    del_flag = db.Column(db.Integer, server_default=db.FetchedValue())
    create_by = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    update_by = db.Column(db.String(64))
    update_time = db.Column(db.DateTime, server_default=db.FetchedValue())

    page = 1
    size = 10

    # 识别id

    task_id=None
    # 修改值
    modify_the_value=[]


    # 模型位置
    pretrained_model=None
    # 字典位置
    character_dict_path=None
    # 轮次
    epoch_num=None
    # 学习率
    learning_rate=None
    # 批次
    batch_size_per_card=None
    # 批次
    use_gpu=None