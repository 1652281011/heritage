from flask import g
from flask_restful import Resource

from app.api.common.fields import interaction_contribute_result_fields
from app.api.common.parser import interaction_submit_parser
from app.api.common.response import error, success
from app.services.heritage.interactive_service import InteractionService
from app.utils.decorators import expert_or_admin_required


class InteractionContributeResource(Resource):
    # 【核心修复】：只使用这一个自包含装饰器，避免顺序问题
    method_decorators = [expert_or_admin_required]

    def post(self):
        # 1. 获取参数
        args = interaction_submit_parser()
        
        # 2. 调用 Service。此时 g.user 已经被装饰器安全注入了
        work, msg = InteractionService.contribute(g.user, args)
        
        if not work:
            return error(msg=msg)

        # 3. 返回成功
        return success(
            msg=msg, 
            data=work, 
            data_fileds=interaction_contribute_result_fields()
        )