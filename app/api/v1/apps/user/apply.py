from flask import g
from flask_restful import Resource

from app.api.common.fields import creator_app_fields
from app.api.common.parser import creator_apply_parser
from app.api.common.response import error, success
from app.services.user.application import CreatorService
from app.utils.decorators import login_required


class CreatorApplyResource(Resource):
    """
    POST /v1/user/creator/apply
    用户提交申请
    """
    method_decorators = [login_required]

    def post(self):
        args = creator_apply_parser()
        # 内部自带“内存锁”防抖（如果你的 admin_logger 同时也支持普通 login_required 用户）
        # 如果不需要日志，这里直接调 service 即可
        result, msg = CreatorService.submit_application(g.user, args)
        
        if not result:
            return error(msg=msg)
            
        return success(msg=msg, data=result, data_fileds=creator_app_fields())