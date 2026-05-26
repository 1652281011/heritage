from flask import g
from flask_restful import Resource
from app.api.common.fields import request_list_fields
from app.api.common.parser import heritage_request_list_parser, heritage_request_search_parser
from app.api.common.response import success
from app.services.heritage.heritage_request_service import HeritageRequestService
from app.utils.decorators import expert_required


class UserMyHeritageRequestResource(Resource):

    # 只需要登录，不需要 role_type=2 的专家限制
    method_decorators = [expert_required]

    def get(self):
        # 1. 获取分页和过滤参数 (status, heritage_keyword)
        args = heritage_request_list_parser()
        
        # 2. 调用 Service。重点：固定 user_id=g.user.id
        # 这样即使是 role_type=1 的群众，也能看到他们提交过的历史记录
        result = HeritageRequestService.get_filtered_list(
            user_id=g.user.id, # 锁定本人
            status=args.get('status'),
            heritage_keyword=args.get('heritage_keyword'),
            page=args['page'],
            per_page=args['per_page']
        )
        
        return success(
            msg="获取我的申请列表成功",
            data=result,
            data_fileds=request_list_fields()
        )