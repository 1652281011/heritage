#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/30 上午8:11
# @Author  : scott
"""管理员登录"""
import time
from flask import current_app, request
from flask_restful import Resource

from app.api.common import error_code
from app.api.common.fields import user_fields, user_login_fields
from app.api.common.parser import user_sign_in_parser
from app.api.common.response import error, success
from app.models.users import User
from app.models import db
from app.services.user.user_service import UserService

class SignIn(Resource):

    def post(self):
        """
        登录接口
        """
        args = user_sign_in_parser()
        
        # 调用 Service
        ok, res = UserService.login(args)
        
        if ok:
            # 登录成功
            return success(data=res, data_fileds=user_login_fields(), msg="登录成功")
        
        # --- 核心修改：区分错误信息 ---
        if res == "ACCOUNT_NOT_FOUND":
            return error(resid=error_code.USER_NOT_EXISTS, msg=u"该账号尚未注册")
        
        elif res == "PASSWORD_ERROR":
            return error(resid=error_code.USER_PASSWORD_NOT_CORRECT, msg=u"密码错误，请重新输入")
        
        elif res == "ACCOUNT_DISABLED":
            return error(resid=error_code.USER_NOT_ACTIVE_OR_LOCKED, msg=u"账号已被禁用或冻结")
        
        # 其他未知系统错误
        return error(msg=u"登录失败，请稍后再试", resid=401)