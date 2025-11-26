# -*- coding: utf-8 -*-
from services.UserService import get_login_user


def getUser():
    login_user = get_login_user()

    return login_user

