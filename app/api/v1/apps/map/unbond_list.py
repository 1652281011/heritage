from flask_restful import Resource, marshal

from app.api.common.fields import unbound_heritage_fields
from app.api.common.parser import unbound_heritage_parser
from app.services.heritage.heritage_service import HeritageService
from app.utils.decorators import admin_required


class UnboundHeritageResource(Resource):

    method_decorators = [admin_required]

    def get(self):
        # 1. 解析查询参数
        args = unbound_heritage_parser()
        
        # 2. 调用 Service 获取未绑定的非遗
        unbound_list = HeritageService.get_unbound_list(
            keyword=args.get('keyword')
        )
        
        # 3. 使用单一 fields 包装结果
        return marshal({"data": unbound_list}, unbound_heritage_fields())