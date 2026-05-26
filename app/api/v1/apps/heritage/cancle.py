from flask import g
from flask_restful import Resource

from app.api.common.parser import heritage_request_id_parser
from app.api.common.response import error, success
from app.services.heritage.heritage_request_service import HeritageRequestService
from app.utils.decorators import expert_required


class HeritageRequestCancelResource(Resource):
    """
    接口：用户撤销已提交但未审核的申请
    POST /v1/heritage/request/cancel
    """
    method_decorators = [expert_required]

    def post(self):
        # 1. 获取参数
        args = heritage_request_id_parser()
        
        # 2. 调用 Service 
        success_flag, msg = HeritageRequestService.cancel_request(
            user_id=g.user.id, 
            req_id=args['request_id']
        )
        
        # 3. 返回结果
        if not success_flag:
            return error(msg=msg)
            
        return success(msg=msg)
