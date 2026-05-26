# -*- coding: utf-8 -*-
from flask import g, request # 必须导入 request
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import heritage_detail_parser
from app.api.common.fields import heritage_detail_fields
from app.services.heritage.heritage_service import HeritageService
# 必须导入 User 模型用于校验 Token
from app.models.users import User
from app.utils.decorators import login_required 

class HeritageDetailResource(Resource):
    def get(self):
        args = heritage_detail_parser()
        h_id = args.get('id')

        token = request.headers.get('Auth-Token')
        user = User.verify_auth_token(token)
        user_id = user.id if user else None
        
        heritage = HeritageService.get_heritage_detail(h_id, user_id=user_id)

        if not heritage:
            return error(msg="该非遗项目不存在或已下架")

        # 4. 返回成功响应
        return success(
            msg="获取详情成功",
            data=heritage,
            data_fileds=heritage_detail_fields()
        )