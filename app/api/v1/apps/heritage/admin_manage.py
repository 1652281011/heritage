from flask import g
from flask_restful import Resource

from app.api.common.parser import admin_heritage_direct_parser
from app.api.common.response import error, success
from app.services.heritage.heritage_service import HeritageService
from app.utils.decorators import admin_logger, admin_required


class AdminHeritageDirectResource(Resource):

    method_decorators = [admin_required]

    @admin_logger(module="非遗管理", action="管理非遗", id_field="heritage_id")

    def post(self):
        # 1. 解析 Form-Data 参数 (含文件)
        args = admin_heritage_direct_parser()
        
        # 2. 执行直接管理逻辑
        result, msg = HeritageService.admin_direct_manage(g.user.id, args)
        
        # 3. 失败处理
        if not result:
            return error(msg=msg)

        return success(msg=msg)