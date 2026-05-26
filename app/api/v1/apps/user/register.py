# -*- coding: utf-8 -*-
from flask_restful import Resource
from app.api.common import error_code
from app.api.common.parser import user_register_parser
from app.api.common.response import success, error
from app.models.users import User
from app.services.user.user_service import UserService

class Register(Resource):
    def post(self):
        """用户注册接口"""
        args = user_register_parser()
        ok, res = UserService.register(args)
        if ok:
            return success(data=res, msg="注册成功")
        if res == "USER_IS_EXISTS":
            return error(resid=error_code.USER_NOT_EXISTS, msg=u"该手机号已被注册")
        elif res == "MOBILE_TYPE_ERROR":
            return error(resid=error_code.MOBILE_TYPE_ERROR, msg=u"手机号格式不正确，请输入11位手机号")
        
        return error(msg=u"注册失败，请稍后再试", resid=401)