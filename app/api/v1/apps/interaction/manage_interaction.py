from flask import g
from flask_restful import Resource

from app.api.common.fields import interaction_manage_detail_fields
from app.api.common.parser import get_interaction_id_parser, interaction_id_parser
from app.api.common.response import error, success
from app.models.heritage_interaction import HeritageInteraction
from app.services.heritage.interactive_service import InteractionService
from app.utils.decorators import login_required


class ManageInteractionDetailResource(Resource):
    method_decorators = [login_required]
    def get(self):
        args = get_interaction_id_parser()
        work = HeritageInteraction.query.get(args['id'])
        if not work: return error(msg="不存在")
        if str(g.user.role_type) != "3" and work.author_id != g.user.id:
            return error(msg="无权查看")
        return success(data=work, data_fileds=interaction_manage_detail_fields())