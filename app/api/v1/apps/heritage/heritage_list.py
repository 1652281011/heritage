# -*- coding: utf-8 -*-
from flask import g, request # 导入 g
from flask_restful import Resource
from app.api.common.fields import heritage_list_fields
from app.api.common.parser import heritage_list_parser
from app.api.common.response import success
from app.services.heritage.heritage_service import HeritageService
from app.models.users import User

class HeritageListResource(Resource):
    """非遗列表"""
    def get(self):
        user_id = None
        
        auth_token = getattr(g, 'auth_token', request.headers.get('Auth-Token'))
        app_type = getattr(g, 'app_type', 'web') # 默认 web

        if auth_token:
            user = User.verify_auth_token(auth_token, app_type)
            if user:
                user_id = user.id

        # 2. 获取参数
        args = heritage_list_parser()
        
        # 3. 将 user_id 传给 Service
        result = HeritageService.get_heritage_list(
            page=args.get('page', 1),
            per_page=args.get('per_page', 20),
            keyword=args.get('keyword'),
            heritage_class=args.get('heritage_class'),
            origin=args.get('origin'),
            enroll_year=args.get('enroll_year'),
            order_by=args.get('order_by'),
            user_id=user_id  # 关键：一定要传这个参数
        )
        
        return success(
            msg=u"请求成功", 
            data=result, 
            data_fileds=heritage_list_fields()
        )