# -*- coding: utf-8 -*-
from flask import g
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import post_update_parser
from app.api.common.fields import post_fields 
from app.utils.decorators import login_required
from app.services.community.post_service import PostService

class PostUpdateResource(Resource):
    method_decorators = [login_required]

    def post(self):
        """
        修改帖子接口 (仅文本)
        """
        args = post_update_parser()
        
        # 调用 Service
        ok, result = PostService.update_post(
            post_id=args.get('post_id'),
            user_id=g.user.id,
            title=args.get('title'),
            content=args.get('content'),
            is_public=args.get('is_public')
        )

        if ok:
            # 成功则返回更新后的帖子数据
            return success(
                msg=u"修改成功", 
                data=result, 
                data_fileds=post_fields() 
            )
        else:
            return error(msg=result)