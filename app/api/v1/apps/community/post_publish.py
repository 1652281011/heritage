# -*- coding: utf-8 -*-
from flask import g
from flask_restful import Resource

from app.api.common import error_code
from app.api.common.fields import post_fields # 确保在 fields.py 定义了此函数
from app.api.common.parser import post_publish_parser
from app.api.common.response import error, success
from app.utils.decorators import login_required
from app.services.community.post_service import PostService

class PostPublish(Resource):
    method_decorators = [login_required]

    def post(self):
        # 1. 解析参数
        args = post_publish_parser()
        
        # 2. 调用专门的业务函数
        ok, result = PostService.create_post(
            user_id=g.user.id,
            title=args['title'],
            content=args['content'],
            image_files=args.get('images', []), # 必须是列表
            is_public=args.get('is_public', 1)
        )

        if not ok:
            return error(error_code.SYSTEM_ERROR, msg=result)

        return success(
            msg=u'发布成功', 
            data=result, 
            data_fileds=post_fields()
        )