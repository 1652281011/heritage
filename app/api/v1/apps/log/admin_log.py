from flask_restful import Resource, marshal
from app.api.common.fields import log_list_fields
from app.api.common.parser import log_list_parser
from app.api.common.response import success
from app.services.adminlog.adminlog_service import AdminLogService
from app.utils.decorators import admin_required

class AdminLogListResource(Resource):
    """
    接口：查看管理员操作日志列表
    GET /v1/admin/logs
    """
    method_decorators = [admin_required]

    def get(self):
        # 1. 解析参数
        args = log_list_parser()
        
        # 2. 获取分页数据
        data = AdminLogService.get_log_list(args)
        
        # 3. 使用单一 Fields 格式化并返回
        # 注意：此处返回的 data 本身是一个字典 {"list": [...], "total": 100, ...}
        return marshal({"data": data}, log_list_fields())