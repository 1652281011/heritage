from flask import g
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import post_interact_parser
from app.services.community.interact_service import InteractService
from app.utils.decorators import login_required

class LikeResource(Resource):
    # 强制登录，user_id 从 g.user 中获取，保证安全
    method_decorators = [login_required]
    
    def post(self):
        # 1. 解析参数 (现在只接收 post_id)
        args = post_interact_parser()
        
        # 2. 从 Token 注入的 g 对象中获取当前用户 ID
        user_id = g.user.id
        
        # 3. 调用 Service
        ok, res = InteractService.toggle_like(args['post_id'], user_id)
        
        if ok:
            # --- 核心修改：根据 action 区分返回信息 ---
            if res['action'] == "LIKE":
                display_msg = u"点赞成功"
            else:
                display_msg = u"已取消点赞"
            
            return success(
                data={"like_count": res['count']}, 
                msg=display_msg
            )
        
        # 4. 异常处理
        if res == "POST_NOT_FOUND":
            return error(msg=u"帖子不存在或已被删除", resid=404)
        return error(msg=u"操作失败，请稍后重试", resid=500)