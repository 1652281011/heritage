from flask_restful import Resource, marshal

from app.api.common.fields import element_update_fields
from app.api.common.parser import element_update_parser
from app.api.common.response import error
from app.services.heritage.element_service import ElementService
from app.utils.decorators import admin_logger, admin_required


class ElementUpdateResource(Resource):
    """
    接口：管理员修改板块绑定关系
    POST /v1/heritage/map/elements/update
    权限：管理员 (role_type == "3")
    """
    method_decorators = [admin_required]

    @admin_logger(module=u"地图管理", action=u"修改绑定", id_field='bind_element_id')

    def post(self):
        # 1. 解析参数
        args = element_update_parser()
        
        # 2. 调用 Service 执行更新逻辑
        flag, result = ElementService.update_binding(
            bind_id=args['bind_element_id'],
            heritage_id=args.get('heritage_id'),
            is_active=args.get('is_active')
        )
        
        # 3. 错误处理
        if not flag:
            return error(msg=result)
            
        # 4. 成功返回（使用单一 fields 定义）
        return marshal({"data": result}, element_update_fields())