from flask_restful import Resource, marshal

from app.api.common.fields import creator_detail_admin_fields
from app.api.common.parser import creator_id_parser
from app.api.common.response import error
from app.services.user.application import CreatorService
from app.utils.decorators import admin_required


class AdminCreatorDetailResource(Resource):
    """
    接口：管理员查看具体的创作者入驻申请详情
    GET /v1/admin/creator/detail
    """
    method_decorators = [admin_required]

    def get(self):
        # 1. 解析参数
        args = creator_id_parser()
        
        # 2. 调用 Service 获取数据
        application, msg = CreatorService.get_application_detail(app_id=args['application_id'])
        
        if not application:
            return error(msg=msg)
            
        # 3. 返回数据（marshal 会自动处理嵌套的 user 字段）
        return marshal({"data": application}, creator_detail_admin_fields())