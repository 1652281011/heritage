from flask import g, request
from flask_restful import Resource

from app.api.common.fields import achievement_list_fields
from app.api.common.parser import achievement_query_parser
from app.api.common.response import error, success
from app.models.users import User
from app.services.achievements.achievement_service import AchievementService


class UserEarnedAchievementResource(Resource):
    """
    接口：查看已获得成就
    GET /v1/user/achiecement (对应你日志中的路径)
    """
    def get(self):
        # 1. 获取解析参数 (user_id)
        args = achievement_query_parser()
        
        # 2. 【核心修复】：手动识别身份
        # 如果 g.user 为空，尝试从请求头拿 Token 校验
        viewer = getattr(g, 'user', None)
        if not viewer:
            token = request.headers.get('Auth-Token')
            if token:
                viewer = User.verify_auth_token(token)

        # 3. 确定目标用户 ID
        # 逻辑：URL传了用URL的，没传用当前登录者的
        target_id = args.get('user_id')
        if not target_id:
            if viewer:
                target_id = viewer.id
            else:
                # 此时既没传参也没登录，返回更有意义的报错
                return error(msg=u"请指定要查看的用户ID或先登录")

        # 4. 调用 Service
        result, msg = AchievementService.get_earned_list(target_id, viewer)
        
        if result is None:
            return error(msg=msg)

        return success(msg=msg, data=result, data_fileds=achievement_list_fields())