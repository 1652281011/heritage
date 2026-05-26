from flask import g, request
from flask_restful import Resource

from app.api.common.parser import heritage_request_submit_parser
from app.api.common.response import error, success
from app.services.heritage.heritage_request_service import HeritageRequestService
from app.services.heritage.heritage_service import HeritageService
from app.utils.decorators import expert_required


class HeritageRequestSubmitResource(Resource):
    method_decorators = [expert_required]
    def post(self):
        args = heritage_request_submit_parser()
        work, msg = HeritageRequestService.submit_request(g.user.id, args)
        return success(msg=msg) if work else error(msg=msg)