from flask import g
from flask_restful import Resource

from app.api.common.parser import interaction_id_parser
from app.api.common.response import error, success
from app.services.heritage.interactive_service import InteractionService
from app.utils.decorators import expert_required


class InteractionCancelResource(Resource):
    """
    专家撤销投稿接口
    POST /v1/interact/cancel
    """
    method_decorators = [expert_required]

    def post(self):
        args = interaction_id_parser()
        
        # 调用 Service 层
        ok, msg = InteractionService.cancel_work(
            user_id=g.user.id, 
            it_id=args['id']
        )
        
        if not ok:
            return error(msg=msg)
            
        return success(msg=msg)