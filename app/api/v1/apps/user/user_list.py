from flask_restful import Resource, marshal

from app.api.common.fields import admin_user_list_fields
from app.api.common.parser import admin_user_list_parser
from app.services.user.user_service import UserService
from app.utils.decorators import admin_required


class AdminUserListResource(Resource):
    method_decorators = [admin_required]

    def get(self):
        # 1. 获取解析后的参数
        args = admin_user_list_parser()
        
        # 2. 调用 Service 获取分页数据
        data = UserService.get_user_list_admin(args)
        
        # 3. 格式化并返回
        return marshal({"data": data}, admin_user_list_fields())