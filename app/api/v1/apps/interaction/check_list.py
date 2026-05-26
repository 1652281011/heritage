from flask import g
from flask_restful import Resource

from app.api.common.fields import interaction_list_fields
from app.api.common.parser import interaction_query_list_parser
from app.api.common.response import success
from app.services.heritage.interactive_service import InteractionService
from app.utils.decorators import expert_required


class ExpertMyInteractionListResource(Resource):
    method_decorators = [expert_required]
    def get(self):
        args = interaction_query_list_parser()
        data = InteractionService.get_list(user_id=g.user.id, **args)
        return success(data=data, data_fileds=interaction_list_fields())