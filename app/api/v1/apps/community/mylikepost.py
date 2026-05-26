from flask import g
from flask_restful import Resource
from app.api.common.fields import post_list_fields
from app.api.common.parser import post_list_parser
from app.api.common.response import success
from app.services.community.post_service import PostService
from app.utils.decorators import login_required

class MyLikedPostResource(Resource):
    method_decorators = [login_required]

    def get(self):
        args = post_list_parser()
        # 调用 Service，传入 liked_by_user_id 参数
        result = PostService.get_post_list(
            page=args.get('page'),
            per_page=args.get('per_page'),
            keyword=args.get('keyword'),
            liked_by_user_id=g.user.id
        )
        return success(msg=u"获取点赞列表成功", data=result, data_fileds=post_list_fields())