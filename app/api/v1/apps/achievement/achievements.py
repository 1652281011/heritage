# -*- coding: utf-8 -*-
import time
from flask import g, request
from flask_restful import Resource
from app.api.common.fields import achievement_list_fields
from app.api.common.parser import achievement_query_parser
from app.api.common.response import error, success
from app.models.users import User
from app.models.achievements import Achievement, UserAchievement
from app.services.achievements.achievement_service import AchievementService

class AchievementAtlasResource(Resource):
    """
    接口：获取成就图鉴（包含未获得的）
    GET /v1/achievement/atlas
    支持：游客查看公开图鉴、登录者查看自己、管理员查看全部
    """
    def get(self):
        # 1. 解析查询参数 (user_id)
        args = achievement_query_parser()
        
        # 2. 【核心修复】：尝试获取当前访问者身份
        # 如果装饰器没给 g.user 赋值，我们手动从 Header 拿 Token 校验一次
        viewer = getattr(g, 'user', None)
        if not viewer:
            token = request.headers.get('Auth-Token')
            if token:
                # 调用你模型中的 verify_auth_token 方法
                viewer = User.verify_auth_token(token)
        
        # 3. 确定要看谁的成就
        target_id = args.get('user_id')
        if not target_id:
            # 如果没传 user_id，则默认看自己。如果自己也没登录，才报之前的错
            if viewer:
                target_id = viewer.id
            else:
                # 对应你日志中的报错点：既没传参数，也没能识别出登录身份
                return error(msg=u"请指定目标用户ID或先登录")

        # 4. 调用 Service（Service 内部会判断 target_id 是否开启了 is_public_achievement）
        result, msg = AchievementService.get_full_atlas(target_id, viewer)
        
        # 5. 处理结果
        if result is None:
            return error(msg=msg)

        return success(
            msg=msg,
            data=result,
            data_fileds=achievement_list_fields()
        )