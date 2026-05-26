from flask import g
from flask_restful import Resource

from app.api.common.fields import request_list_fields
from app.api.common.parser import heritage_request_list_parser, heritage_request_search_parser
from app.api.common.response import success
from app.models.heritage_edit import HeritageRequest
from app.services.heritage.heritage_request_service import HeritageRequestService
from app.services.heritage.heritage_service import HeritageService
from app.utils.decorators import admin_required, login_required


class AdminHeritageRequestListResource(Resource):
    """
    接口：管理员获取全量非遗申请/审核列表
    路由：GET /v1/heritage/admin/request-list
    支持：按状态过滤、按用户搜索、按非遗名称搜索
    """
    # 强制校验管理员权限 (role_type == '3')
    method_decorators = [admin_required]

    def get(self):
        # 1. 获取并解析搜索参数
        args = heritage_request_search_parser()

        # 2. 调用通用 Service 方法
        # 关键点：user_id 传 None，表示管理员查询全量数据，不进行个人数据隔离
        result = HeritageRequestService.get_filtered_list(
            user_id=None, 
            status=args.get('status'),
            user_keyword=args.get('user_keyword'),
            heritage_keyword=args.get('heritage_keyword'),
            page=args['page'],
            per_page=args['per_page']
        )

        # 3. 规范化返回结果 (注意拼写 data_fileds)
        return success(
            msg="获取全量申请列表成功",
            data=result,
            data_fileds=request_list_fields()
        )