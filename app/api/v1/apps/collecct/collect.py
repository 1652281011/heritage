# -*- coding: utf-8 -*-
from flask import g, request
from flask_restful import Resource
from app.api.common.parser import collect_parser
from app.api.common.response import success, error
# 导入你的装饰器
from app.utils.decorators import login_required 
from app.services.heritage.collect_service import HeritageCollectService

class HeritageCollectResource(Resource):
    method_decorators = [login_required]

    def post(self):
        """
        收藏/取消收藏
        由于有 login_required，我们可以直接从 g.user 获取当前用户信息
        """
        args = collect_parser()
        heritage_id = args.get('heritage_id')

        # 调用服务层逻辑
        res, msg = HeritageCollectService.toggle_collect(g.user.id, heritage_id)

        if res is None:
            return error(msg=msg)

        return success(msg=msg, data={'is_collected': res})