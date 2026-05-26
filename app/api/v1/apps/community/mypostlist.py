from flask import g
from flask_restful import Resource
from app.api.common.fields import post_list_fields
from app.api.common.parser import post_list_parser
from app.api.common.response import success
from app.services.community.post_service import PostService
from app.utils.decorators import login_required


class MyPostListResource(Resource):
    method_decorators = [login_required]

    def get(self):
        args = post_list_parser()
        # 调用 Service，传入当前登录用户 ID，并标记 is_own=True (显示私密贴)
        result = PostService.get_post_list(
            page=args.get('page'),
            per_page=args.get('per_page'),
            keyword=args.get('keyword'),
            user_id=g.user.id,
            is_own=True
        )
        return success(msg=u"获取个人动态成功", data=result, data_fileds=post_list_fields())