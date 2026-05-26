from flask_restful import Resource, marshal

from app.api.common.fields import element_create_fields
from app.api.common.parser import element_add_parser
from app.api.common.response import error
from app.services.heritage.element_service import ElementService
from app.utils.decorators import admin_logger, admin_required


class ElementAddResource(Resource):
    """管理员新增板块"""
    method_decorators = [admin_required]
    @admin_logger(module=u"地图管理", action=u"新增板块", id_field='bind_element_id')

    def post(self):
        args = element_add_parser()
        
        flag, result = ElementService.add_element(
            bind_element_id=args['bind_element_id'],
            is_active=args['is_active']
        )
        
        if not flag:
            return error(msg=result)
            
        return marshal({"data": result}, element_create_fields())