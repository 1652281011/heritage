from flask import g, current_app
from flask_restful import Resource
from app.api.common import error_code
from app.api.common.fields import user_fields, user_uodate_fields
from app.models.base import db
from app.models.users import User
from app.api.common.response import success, error
from app.api.common.parser import user_update_parser
from app.services.user.user_service import UserService
from app.utils.decorators import login_required
from app.utils.uploader import Uploader

class UserInfoResource(Resource):
    method_decorators = [login_required]

    def post(self):
        """
        更新个人资料接口
        """
        # 1. 解析参数
        args = user_update_parser()
        
        # 2. 调用服务层 (传入当前登录用户的 ID)
        ok, res = UserService.update_profile(g.user.id, args)
        
        if ok:
            # res 为最新的 user.to_dict()
            return success(data=res, data_fileds=user_uodate_fields(), msg="资料更新成功")
        if res == "FILE_TYPE_NOT_ALLOWED":
            return error(resid=error_code.USER_NOT_EXISTS, msg=u"头像上传失败，文件类型不允许")
        
        elif res == "FILE_TOO_BIG":
            return error(resid=error_code.USER_PASSWORD_NOT_CORRECT, msg=u"头像上传失败，文件大小超出网站限制")

        return error(msg=res, resid=400)