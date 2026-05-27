from flask import g, request
from flask_restful import Resource

from app.api.common.response import error, success
from app.services.user.user_service import UserService
from app.utils.decorators import admin_logger, login_required


class LogoutResource(Resource):
    """
    接口：用户退出登录
    POST /v1/user/logout
    """
    # 必须登录才能注销
    method_decorators = [login_required]

    # 如果是管理员退出，可以记录日志；普通用户通常不需要记入 admin_logger
    @admin_logger(module=u"账号管理", action=u"退出登录")
    def post(self):
        # 1. 获取当前请求头中的 Token
        token = request.headers.get('Auth-Token')
        
        # 2. 调用 Service 执行注销逻辑
        # g.user 是在 login_required 装饰器中填充的
        work, msg = UserService.logout(user_id=g.user.id, token=token)
        
        if not work:
            return error(msg=msg)
            
        return success(msg=u"您已安全退出")
