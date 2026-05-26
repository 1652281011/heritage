# -*- coding: utf-8 -*-
from flask import g, request
from flask_restful import Resource
from app.api.common.fields import user_finished_fields
from app.api.common.parser import user_finished_heritages_parser
from app.api.common.response import success
from app.utils.decorators import login_required
from app.services.heritage.heritage_service import HeritageService

class UserFinishedHeritageResource(Resource):

    method_decorators = [login_required]

    def get(self):

        # 1. 调用独立的解析器获取参数
        args = user_finished_heritages_parser()

        # 2. 从解析后的对象中提取 page 和 per_page
        result = HeritageService.get_user_finished_list(
            user_id=g.user.id,
            page=args.get('page'),
            per_page=args.get('per_page')
        )

        # 3. 规范化返回响应
        # 注意：这里依然沿用你项目中 data_fileds 的拼写习惯
        return success(
            msg="获取通关列表成功",
            data=result,
            data_fileds=user_finished_fields()
        )