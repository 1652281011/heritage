from flask import g
from flask_restful import Resource, marshal

from app.api.common.fields import element_list_fields
from app.api.common.parser import element_list_parser
from app.services.heritage.element_service import ElementService
from app.utils.decorators import login_required


class ElementListResource(Resource):

    method_decorators = [login_required]

    def get(self):
        # 1. 解析参数（如有）
        args = element_list_parser()
        
        # 2. 获取当前用户角色类型
        # 根据你提供的 login_required，g.user 会被填充
        user_role = getattr(g.user, 'role_type', None)
        
        # 3. 调用 Service 层，根据角色过滤数据
        bindings = ElementService.get_element_list(user_role=user_role)
        
        # 4. 使用单一 fields 进行数据包装
        # marshal 会自动处理 common_fields 中的 resid, msg, status 等字段
        result = marshal(
            {"data": bindings}, 
            element_list_fields()
        )
        
        return result