# -*- coding: utf-8 -*-
from flask import g
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import post_delete_parser
from app.utils.decorators import login_required
from app.services.community.post_service import PostService

class PostDeleteResource(Resource):
    method_decorators = [login_required]

    def post(self):
        """
        用户删帖接口
        """
        args = post_delete_parser()
        post_id = args.get('post_id')

        # 判断执行人身份（如果是管理员，传入 is_admin=True）
        is_admin = True if getattr(g.user, 'role', '') == 'admin' else False

        # 调用 Service
        ok, msg = PostService.delete_post(
            post_id=post_id, 
            user_id=g.user.id, 
            is_admin=is_admin
        )

        if ok:
            return success(msg=msg)
        return error(msg=msg)