# -*- coding: utf-8 -*-
import datetime


class JwtConfig:
    JWT_SECRET_KEY = 'your-secret-key'  # 更换为你自己的密钥
    JWT_BLACKLIST_ENABLED = False  # 启用或禁用令牌黑名单
    JWT_DEBUG = True
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=12)
    # JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(milliseconds=10000)
