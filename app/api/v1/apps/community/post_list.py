# -*- coding: utf-8 -*-
from flask_restful import Resource
from app.api.common.response import success
from app.api.common.parser import post_list_parser
from app.api.common.fields import post_list_fields
from app.services.community.post_service import PostService

class PostListResource(Resource):
    def get(self):
        # 1. 获取解析后的参数
        args = post_list_parser()
        
        # 2. 提取变量
        page = args.get('page', 1)
        per_page = args.get('per_page', 10)
        keyword = args.get('keyword')

        # 3. 调用 Service
        result = PostService.get_post_list(
            page=page, 
            per_page=per_page, 
            keyword=keyword
        )

        return success(
            msg=u"请求成功", 
            data=result, 
            data_fileds=post_list_fields()
        )