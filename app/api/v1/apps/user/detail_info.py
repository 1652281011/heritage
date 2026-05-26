from flask import g
from flask_restful import Resource
from app.api.common.response import success, error
from app.api.common.parser import user_info_get_parser
from app.api.common.fields import user_fields
from app.services.user.user_service import UserService
from app.utils.decorators import login_required

class UserDetailResource(Resource):
    method_decorators = [login_required]

    def get(self):
        """获取全量用户信息"""
        args = user_info_get_parser()
        
        # 确定目标 ID（传了查别人，没传查自己）
        target_id = args.get('user_id') or g.user.id
        
        # 调用 Service
        ok, res = UserService.get_user_profile(target_id)
        
        if ok:
            # 返回包含所有数值和开关的 JSON
            return success(data=res, data_fileds=user_fields())
        
        return error(msg=res, resid=404)