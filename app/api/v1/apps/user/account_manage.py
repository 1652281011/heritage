from flask import g
from flask_restful import Resource

from app.api.common.parser import admin_user_manage_parser
from app.api.common.response import error, success
from app.services.user.user_service import UserService
from app.utils.decorators import admin_logger, admin_required


class AdminUserManageResource(Resource):
    """管理员管理用户账号（禁用/启用/改角色）接口"""
    method_decorators = [admin_required]

    @admin_logger(module=u"账号管理", action=u"修改用户信息", id_field='user_id')
    def post(self):
        args = admin_user_manage_parser()
        # 调用 Service
        work, msg = UserService.manage_user_account(admin_user=g.user, args=args)
        
        if not work:
            return error(msg=msg)
            
        return success(msg=msg)