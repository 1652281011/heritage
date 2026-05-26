from flask_restful import Resource
from app.models.base import db

from app.api.common.fields import interaction_user_detail_fields
from app.api.common.parser import get_interaction_id_parser, interaction_id_parser
from app.api.common.response import error, success
from app.models.heritage_interaction import HeritageInteraction
from app.services.heritage.interactive_service import InteractionService


class InteractionDetailResource(Resource):
    def get(self):
        args = get_interaction_id_parser()
        work = HeritageInteraction.query.filter_by(id=args['id'], status=1).first()
        if not work: return error(msg="该互动未上架")
        work.view_count += 1
        db.session.commit()
        return success(data=work, data_fileds=interaction_user_detail_fields())