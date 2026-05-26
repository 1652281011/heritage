from flask import g
from flask_restful import Resource, marshal

from app.api.common.fields import creator_progress_fields
from app.api.common.response import success
from app.services.user.application import CreatorService
from app.utils.decorators import login_required


class CreatorProgressResource(Resource):

    method_decorators = [login_required]

    def get(self):
        # 1. 调用 Service 获取当前登录用户的最新一条申请
        app_record, msg = CreatorService.get_latest_progress(user_id=g.user.id)
        
        # 2. 如果没有任何申请记录
        if not app_record:
            # 这里的 error 可以返回 200 业务码但 data 为空，或者直接提示无记录
            return success(msg=msg, data=None)
            
        # 3. 使用单一 Fields 格式化并返回
        return marshal({"data": app_record}, creator_progress_fields())