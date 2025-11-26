# -*- coding: utf-8 -*-
from api import db

class SysUserModel(db.Model):
    __tablename__ = 'sys_user'

    user_id = db.Column(db.BigInteger, primary_key=True, info='用户ID')
    dept_id = db.Column(db.BigInteger, info='部门ID')
    user_name = db.Column(db.String(30), nullable=False, info='用户账号')
    nick_name = db.Column(db.String(30), nullable=False, info='用户昵称')
    user_type = db.Column(db.String(2), server_default=db.FetchedValue(), info='用户类型（00系统用户）')
    email = db.Column(db.String(50), server_default=db.FetchedValue(), info='用户邮箱')
    phonenumber = db.Column(db.String(11), server_default=db.FetchedValue(), info='手机号码')
    sex = db.Column(db.String(1), server_default=db.FetchedValue(), info='用户性别（0男 1女 2未知）')
    avatar = db.Column(db.String(100), server_default=db.FetchedValue(), info='头像地址')
    password = db.Column(db.String(100), server_default=db.FetchedValue(), info='密码')
    status = db.Column(db.String(1), server_default=db.FetchedValue(), info='帐号状态（0正常 1停用）')
    del_flag = db.Column(db.String(1), server_default=db.FetchedValue(), info='删除标志（0代表存在 2代表删除）')
    login_ip = db.Column(db.String(128), server_default=db.FetchedValue(), info='最后登录IP')
    login_date = db.Column(db.DateTime, info='最后登录时间')
    create_by = db.Column(db.String(64), server_default=db.FetchedValue(), info='创建者')
    create_time = db.Column(db.DateTime, info='创建时间')
    update_by = db.Column(db.String(64), server_default=db.FetchedValue(), info='更新者')
    update_time = db.Column(db.DateTime, info='更新时间')
    remark = db.Column(db.String(500), info='备注')
