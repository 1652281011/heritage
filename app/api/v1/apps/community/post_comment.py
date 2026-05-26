from flask import g
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import post_interact_parser
from app.services.community.interact_service import InteractService
from app.utils.decorators import login_required

class CommentResource(Resource):
    method_decorators = [login_required]
    
    def post(self):
        args = post_interact_parser()
        if not args['content']: 
            return error(msg="内容不能为空")

        # --- 核心修改：从 g.user 获取 id ---
        user_id = g.user.id
        
        ok, res = InteractService.add_comment(args['post_id'], user_id, args['content'])
        
        if ok:
            return success(data=res, msg="评论成功")
        return error(msg=res)