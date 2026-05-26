from flask import g
from flask_restful import Resource

from app.api.common.parser import heritage_request_id_parser
from app.api.common.response import error, success
from app.services.heritage.heritage_request_service import HeritageRequestService
from app.utils.decorators import expert_required


class HeritageRequestCancelResource(Resource):
    method_decorators = [expert_required]
    def post(self):
        args = heritage_request_id_parser()
        ok, msg = HeritageRequestService.cancel_request(g.user.id, args['request_id'])
        return success(msg=msg) if ok else error(msg=msg)