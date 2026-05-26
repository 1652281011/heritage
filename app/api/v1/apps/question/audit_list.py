from flask import g
from flask_restful import Resource

from app.api.common.fields import question_request_list_fields
from app.api.common.parser import question_request_query_parser
from app.api.common.response import success
from app.services.heritage.question_request_service import QuestionService
from app.utils.decorators import login_required


class QuestionRequestListResource(Resource):
    method_decorators = [login_required]
    def get(self):
        args = question_request_query_parser()
        is_admin = str(g.user.role_type) == "3"
        data = QuestionService.get_request_list(user_id=None if is_admin else g.user.id, args=args)
        return success(data=data, data_fileds=question_request_list_fields())