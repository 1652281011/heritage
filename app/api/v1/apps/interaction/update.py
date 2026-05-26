from flask import g
from flask_restful import Resource

from app.api.common.fields import interaction_contribute_result_fields, interaction_manage_detail_fields
from app.api.common.parser import interaction_update_parser
from app.api.common.response import error, success
from app.services.heritage.interactive_service import InteractionService
from app.utils.decorators import expert_required


class ExpertInteractionUpdateResource(Resource):
    """专家修改接口: /v1/interact/update"""
    method_decorators = [expert_required]
    
    def post(self):
        args = interaction_update_parser()
        work, msg = InteractionService.update_work(g.user.id, args['interaction_id'], args)
        if not work:
            return error(msg=msg)
        return success(msg=msg, data=work, data_fileds=interaction_contribute_result_fields())