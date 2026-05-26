from flask import g
from flask_restful import Resource

from app.api.common.parser import question_request_submit_parser
from app.api.common.response import error, success
from app.services.heritage.question_request_service import QuestionService
from app.utils.decorators import expert_required


class QuestionRequestSubmitResource(Resource):
    method_decorators = [expert_required]
    def post(self):
        args = question_request_submit_parser()
        work, msg = QuestionService.submit_request(g.user.id, args)
        return success(msg=msg) if work else error(msg=msg)