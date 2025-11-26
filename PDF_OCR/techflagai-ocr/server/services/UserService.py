# -*- coding: utf-8 -*-
import hashlib

import bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity

from models.SysUserModel import SysUserModel
from utils.result import Result


def login(userModel):
    query = SysUserModel.query.filter(SysUserModel.user_name == userModel.user_name)
    user = query.first()

    if user:
        if user.status == 1:
            return Result.error('该账号已被禁用', 403)
        if bcrypt.checkpw(userModel.password.encode('utf-8'), user.password.encode('utf-8')):
            user.password = None
            access_token = create_access_token(identity=str(user.user_id))
            token = access_token
            return Result.success({
                'access_token': token,
                'username': user.user_name
            }, '登录成功')
        else:
            return Result.error('密码错误')

    else:
        return Result.error('该账号不存在')



# 获取登录用户 信息
def get_login_user(id=None):
    if id is None:
        id = get_jwt_identity()
    user = SysUserModel.query.filter_by(user_id=id).first()

    return user


def encode_password(password: str) -> bytes:
    # 将字符串编码为字节串，因为bcrypt.hashpw需要字节串作为输入
    password_bytes = password.encode('utf-8')

    # 使用bcrypt生成盐并哈希密码
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    return hashed_password
